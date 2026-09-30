// ルールの自己チェック: ランダムに答える人で何百局も回し、落ちない・カードの枚数が変わらない・必ず終わることを見る。
//   node test/sim.mjs [局数]
import assert from 'node:assert/strict';
import {
  CARDS, SETS, kingdomPool, randomKingdom, newGame, currentPlayer, playAction, playTreasureGen,
  startBuyPhase, buyCard, endTurn, beginTurn, finalResults, is, PRESETS, allCards, canBuy, costOf, spendCoffers, landscapePool, canBuyEvent, buyEvent,
  enterBuyPhase, enterNightPhase, playNight, canPlayNight, spendVillager,
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
import '../cards-empires.js';
import '../cards-nocturne.js';
import '../cards-renaissance.js';
import '../cards-menagerie.js';
import '../cards-promo.js';
import '../cards-allies.js';
import '../cards-plunder.js';

const rnd = (n) => Math.floor(Math.random() * n);
function answer(q) {
  if (q.type === 'hand' || q.type === 'cards') {
    const pool = q.type === 'hand' ? [...q.options] : q.cards.map((_, i) => i);
    const k = q.min + rnd(Math.min(q.max - q.min, 3) + 1); // 好きな枚数のときも多くて 3 枚（全部廃棄して終わらなくなるのを避ける）
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
const total = (g) => {
  const parts = {
    players: g.players.reduce((s, p) => s + allCards(p).length, 0), trash: g.trash.length, play: g.playArea.length,
    supply: Object.values(g.supply).reduce((a, b) => a + b, 0), non: Object.values(g.nonSupply).reduce((a, b) => a + b, 0),
    bm: (g.blackMarket || []).length,
    stacks: -Object.keys(g.stacks).reduce((a, k) => a + (k in g.supply ? g.supply[k] : g.nonSupply[k]) - g.stacks[k].length, 0),
  };
  const t = Object.values(parts).reduce((a, b) => a + b, 0);
  if (!Number.isFinite(t)) console.error('NAN', JSON.stringify(parts), JSON.stringify(g.supply), JSON.stringify(g.nonSupply), Object.keys(g.stacks));
  return t;
}

const stalls = [];
export function simulate(kingdom, n, landscapes = []) {
  const g = newGame(n, kingdom, null, { landscapes });
  const start = total(g);
  assert.ok(Number.isFinite(start), '枚数が数えられない');
  for (let turns = 0; !g.over; turns++) {
    // でたらめに廃棄して山札がなくなると終わらないことがある。まれなら数えるだけ
    if (turns >= 3000) { stalls.push(kingdom.join(',') + ' + ' + landscapes.join(',') + ' debt=' + g.players.map((p) => p.tokens.debt || 0).join('/') + ' deck=' + g.players.map((p) => allCards(p).length).join('/')); return g; }
    const p = currentPlayer(g);
    run(beginTurn(g));
    while (g.turn.actions > 0 || (p.tokens.villagers > 0 && spendVillager(g))) {
      const acts = p.hand.filter((id) => is(id, 'action'));
      if (!acts.length || Math.random() < 0.1) break;
      const id = acts[rnd(acts.length)];
      run(playAction(g, id));
      assert.equal(total(g), start, `カードの枚数が変わった（${id}）`);
    }
    run(enterBuyPhase(g));
    for (const id of [...p.hand]) {
      if (is(id, 'treasure')) run(playTreasureGen(g, id));
      assert.equal(total(g), start, `カードの枚数が変わった（財宝 ${id}）`);
    }
    if (Math.random() < 0.5) spendCoffers(g, rnd(3));
    for (const e of g.landscapes) if (Math.random() < 0.3 && canBuyEvent(g, e)) assert.ok(run(buyEvent(g, e)));
    while (g.turn.buys > 0) {
      // でたらめに借金の札ばかり買うと終わらないので、借金の札はたまにだけ買う
      const top = (id) => (g.stacks[id] ? g.stacks[id].at(-1) : id);
      const ok = Object.keys(g.supply).filter((id) => canBuy(g, id) && id !== 'curse' && (!CARDS[top(id)].debt || Math.random() < 0.1));
      if (!ok.length || Math.random() < 0.15) break;
      const best = ok.sort((a, b) => costOf(g, b) - costOf(g, a));
      assert.ok(run(buyCard(g, Math.random() < 0.6 ? best[0] : best[rnd(best.length)])));
    }
    enterNightPhase(g);
    for (const id of [...p.hand]) if (canPlayNight(g, id) && Math.random() < 0.8) { run(playNight(g, id)); assert.equal(total(g), start, `カードの枚数が変わった（夜 ${id}）`); }
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
if (process.env.STALLS) console.log(stalls.join('\n'));
assert.ok(stalls.length <= games * 0.02, '終わらない対局が多い: ' + stalls.slice(0, 3).join(' / '));
console.log(`ok: ${SETS.map((s) => s.name).join('・')} / 王国 ${pool.length} 種 / ${games + PRESETS.length} 局（打ち切り ${stalls.length}）`);
