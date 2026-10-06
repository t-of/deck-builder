// AI の試験: 隠れた情報を特徴量が使っていないこと、net が動くこと、AI が 1 局打ち切れること。
//   node test/ai.mjs [局数 4]
// 隠れた情報 = 相手の手札・山札の順（中身も入れ替える）、伏せたマット、自分の山札の並び。
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as E from '../engine.js';
import { nextMove as cpuMove, answer as cpuAnswer } from '../cpu.js';
import { encode, buyCandidates, postState, KIND, NS } from '../ai/features.js';
import { loadModel, evaluate, scoreCandidates } from '../ai/net.js';
import { createAI, playGame } from '../ai/player.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

const meta = JSON.parse(fs.readFileSync(`${dir}ai/model.json`, 'utf8'));
const bin = fs.readFileSync(`${dir}ai/model.bin`);
const model = loadModel(meta, bin.buffer.slice(bin.byteOffset, bin.byteOffset + bin.length));

// ---- net ----
assert.equal(meta.params, Object.values(meta.shapes).reduce((a, s) => a + s.reduce((x, y) => x * y, 1), 0));
for (const a of Object.values(model.w)) for (const v of a) assert.ok(Number.isFinite(v), '重みに有限でない値');

const snap = (b) => JSON.stringify({ s: Array.from(b.scalars), bags: b.bags.map((m) => [...m].sort()), sup: b.supply.map((s) => ({ ...s })) });
let checked = 0;
let decisions = 0;
const BAD = ['copper', 'curse', 'gold'];

// 隠れた札を入れ替えて、特徴量と候補が変わらないことを見る（そのあと元に戻す）
function checkHidden(game) {
  for (let me = 0; me < game.players.length; me++) {
    const before = encode(game, me);
    const cBefore = JSON.stringify(buyCandidates(before).map((c) => [c.kind, c.pile, c.coffers]));
    const saved = game.players.map((p, i) => i === me ? { deck: [...p.deck] } : { hand: [...p.hand], deck: [...p.deck], mats: Object.fromEntries(Object.entries(p.mats).map(([k, v]) => [k, [...v]])) });
    game.players.forEach((p, i) => {
      if (i === me) { p.deck.reverse(); return; }
      const pool = [...p.hand, ...p.deck].reverse().map((_, k) => BAD[k % 3]); // 中身ごと別の札にする（枚数は同じ）
      p.hand.splice(0, p.hand.length, ...pool.slice(0, p.hand.length));
      p.deck.splice(0, p.deck.length, ...pool.slice(p.hand.length));
      for (const k of Object.keys(p.mats)) if (k !== 'tavern' && k !== 'exile') p.mats[k].fill('curse');
    });
    const after = encode(game, me);
    const cAfter = JSON.stringify(buyCandidates(after).map((c) => [c.kind, c.pile, c.coffers]));
    game.players.forEach((p, i) => {
      if (i === me) { p.deck.splice(0, p.deck.length, ...saved[i].deck); return; }
      p.hand.splice(0, p.hand.length, ...saved[i].hand);
      p.deck.splice(0, p.deck.length, ...saved[i].deck);
      for (const k of Object.keys(p.mats)) if (k !== 'tavern' && k !== 'exile') p.mats[k].splice(0, p.mats[k].length, ...saved[i].mats[k]);
    });
    assert.equal(snap(after), snap(before), '隠れた札で特徴量が変わった');
    assert.equal(cAfter, cBefore, '隠れた札で候補が変わった');
    assert.equal(before.scalars.length, NS);
    assert.ok(before.scalars.every(Number.isFinite), '特徴量に有限でない値');
    // viewFor（エンジンの隠し方）を通した game からも同じ特徴量になる（持続の効果が残っていて複製できない場面は除く）
    let v = null;
    try { v = E.viewFor(game, me); } catch { /* 複製できない */ }
    if (v) { v.ledger = game.ledger; assert.equal(snap(encode(v, me)), snap(before), 'viewFor を通すと特徴量が変わった'); }
    checked++;
  }
}

// 候補ごとの評価: 確率の合計が 1、決まった値、「何もしない」以外は買ったあとの袋が 1 枚増える
function checkNet(game) {
  const me = game.current;
  const base = encode(game, me);
  const cands = buyCandidates(base);
  const sc = scoreCandidates(model, base, cands);
  assert.equal(sc.length, cands.length);
  const [a, b] = evaluate(model, base, cands[0]);
  assert.ok(Math.abs(a + b - 1) < 1e-5 && a >= 0 && b >= 0);
  assert.deepEqual(evaluate(model, base, cands[0]), [a, b]);
  for (const c of cands) {
    const post = postState(base, c);
    const n = (st) => [...st.bags[0].values()].reduce((x, y) => x + y, 0);
    assert.equal(n(post) - n(base), c.kind === KIND.buy || c.kind === KIND.gain ? 1 : 0);
  }
  decisions++;
}

const wrap = (inner, check) => ({
  nextMove(game) { check(game); return inner.nextMove(game); },
  answer: (game, q) => inner.answer(game, q),
});
const cpu = (level) => ({ nextMove: (g) => cpuMove(g, level), answer: (g, q) => cpuAnswer(g, q, level) });

const games = Number(process.argv[2] || 4);
const pool = E.kingdomPool();
const lpool = E.landscapePool();
for (let i = 0; i < games; i++) {
  const ai = createAI(model, { temperature: 0.1 });
  const actors = i % 2 ? [wrap(cpu('normal'), checkHidden), wrap(cpu('normal'), checkHidden)]
    : [wrap(ai, (g) => { checkHidden(g); if (g.turn.phase === 'buy' && g.turn.buys > 0) checkNet(g); }), wrap(cpu('strong'), checkHidden)];
  const g = playGame({ kingdom: E.randomKingdom(pool), landscapes: E.randomKingdom(lpool, i % 3), actors });
  assert.ok(g && g.over, '対局が終わらない');
}
assert.ok(checked > 100 && decisions > 20, `確かめた回数が少ない（${checked}, ${decisions}）`);
console.log(`ai: ok（隠れた札の確認 ${checked} 回、net の確認 ${decisions} 回）`);
