// ルールの自己チェック: ランダムに答える人で何百局も回し、落ちない・カードの枚数が変わらない・必ず終わることを見る。
//   node test/sim.mjs [局数]
import assert from 'node:assert/strict';
import {
  CARDS, SETS, kingdomPool, randomKingdom, newGame, currentPlayer, playAction, playTreasureGen,
  startBuyPhase, buyCard, endTurn, beginTurn, finalResults, is, PRESETS, allCards, canBuy, costOf, spendCoffers, landscapePool, canBuyEvent, buyEvent,
} from '../engine.js';
import '../cards-base.js';
import '../cards-intrigue.js';
import '../cards-seaside.js';
import '../cards-prosperity.js';
import '../cards-hinterlands.js';
import '../cards-guilds.js';
import '../cards-alchemy.js';
import '../cards-darkages.js';
import '../cards-adventures.js';

const rnd = (n) => Math.floor(Math.random() * n);
function answer(q) {
  if (q.type === 'hand' || q.type === 'cards') {
    const pool = q.type === 'hand' ? [...q.options] : q.cards.map((_, i) => i);
    const k = q.min + rnd(q.max - q.min + 1);
    return pool.sort(() => Math.random() - 0.5).slice(0, k);
  }
  if (q.type === 'supply') return q.optional && Math.random() < 0.2 ? null : q.options[rnd(q.options.length)];
  if (q.type === 'choose') return q.choices[rnd(q.choices.length)].value;
  throw new Error('知らない問い ' + q.type);
}
function run(gen) {
  let step = gen.next();
  while (!step.done) {
    const q = step.value;
    assert.ok(Number.isInteger(q.player) && Number.isInteger(q.owner), '問いに player / owner がない');
    if (q.type === 'hand') assert.ok(q.min <= q.max && q.max <= q.options.length);
    step = gen.next(answer(q));
  }
  return step.value;
}
const total = (g) => g.players.reduce((s, p) => s + allCards(p).length, 0)
  + g.trash.length + g.playArea.length + Object.values(g.supply).reduce((a, b) => a + b, 0) + Object.values(g.nonSupply).reduce((a, b) => a + b, 0) - Object.keys(g.stacks).reduce((a, k) => a + g.supply[k] - g.stacks[k].length, 0);

const stalls = [];
export function simulate(kingdom, n, landscapes = []) {
  const g = newGame(n, kingdom, null, { landscapes });
  const start = total(g);
  for (let turns = 0; !g.over; turns++) {
    // でたらめに廃棄して山札がなくなると終わらないことがある。まれなら数えるだけ
    if (turns >= 3000) { stalls.push(kingdom.join(',')); return g; }
    const p = currentPlayer(g);
    run(beginTurn(g));
    while (g.turn.actions > 0) {
      const acts = p.hand.filter((id) => is(id, 'action'));
      if (!acts.length || Math.random() < 0.1) break;
      const id = acts[rnd(acts.length)];
      run(playAction(g, id));
      assert.equal(total(g), start, `カードの枚数が変わった（${id}）`);
    }
    startBuyPhase(g);
    for (const id of [...p.hand]) {
      if (is(id, 'treasure')) run(playTreasureGen(g, id));
      assert.equal(total(g), start, `カードの枚数が変わった（財宝 ${id}）`);
    }
    if (Math.random() < 0.5) spendCoffers(g, rnd(3));
    for (const e of g.landscapes) if (Math.random() < 0.3 && canBuyEvent(g, e)) assert.ok(run(buyEvent(g, e)));
    while (g.turn.buys > 0) {
      const ok = Object.keys(g.supply).filter((id) => canBuy(g, id) && id !== 'curse');
      if (!ok.length || Math.random() < 0.15) break;
      const best = ok.sort((a, b) => costOf(g, b) - costOf(g, a));
      assert.ok(run(buyCard(g, Math.random() < 0.6 ? best[0] : best[rnd(best.length)])));
    }
    run(endTurn(g));
    assert.equal(total(g), start, 'カードの枚数が変わった');
  }
  const r = finalResults(g);
  assert.equal(r.length, n);
  return g;
}

const games = Number(process.argv[2] || 300);
const pool = kingdomPool();
for (const pr of PRESETS) for (const id of pr.cards) assert.ok(CARDS[id], `${pr.name} の ${id} がない`);
for (const pr of PRESETS) assert.equal(new Set(pr.cards).size, 10, `${pr.name} が 10 種でない`);
for (const id of pool) assert.ok(CARDS[id].main != null && CARDS[id].desc != null, `${id} の文言がない`);
for (const pr of PRESETS) simulate(pr.cards, 2 + rnd(3), pr.landscapes || []);
const lpool = landscapePool();
for (let i = 0; i < games; i++) simulate(randomKingdom(pool), 2 + rnd(3), randomKingdom(lpool, rnd(3)));
assert.ok(stalls.length <= games * 0.02, '終わらない対局が多い: ' + stalls.slice(0, 3).join(' / '));
console.log(`ok: ${SETS.map((s) => s.name).join('・')} / 王国 ${pool.length} 種 / ${games + PRESETS.length} 局（打ち切り ${stalls.length}）`);
