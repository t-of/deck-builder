// さいきょう（今の cpu.js）と前の版（cpu-baseline.js）を自己対局させ、勝率と考える時間を見る。
//   node tools/versus.mjs [局数]
// 王国はランダム（拡張込み）、先手後手を半分ずつ入れ替える。
import fs from 'node:fs';
import * as E from '../engine.js';
import * as NEW from '../cpu.js';
import * as OLD from '../cpu-baseline.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

// NEW・OLD を自由に混ぜて 1 局打つ（mods[i] が i 番目の人の nextMove/answer/planFor）
function playGame(kingdom, landscapes, mods) {
  const g = E.newGame(mods.length, kingdom, mods.map((_, i) => `P${i + 1}`), { landscapes });
  g.cpuPlans = {};
  const run = (mod, gen) => {
    let st = gen.next();
    for (let k = 0; !st.done; k++) {
      if (k > 3000) throw new Error('問いが終わらない');
      st = gen.next(mods[st.value.player].answer(g, st.value, 'expert'));
    }
    return st.value;
  };
  for (let turns = 0; !g.over; turns++) {
    if (turns > 300) return null;
    run(null, E.beginTurn(g));
    const mod = mods[E.turnController(g)];
    for (let steps = 0; steps < 400; steps++) {
      const m = mod.nextMove(g, 'expert');
      if (m.type === 'action') run(mod, E.playAction(g, m.id));
      else if (m.type === 'shadow') run(mod, E.playShadow(g, m.id));
      else if (m.type === 'villager') E.spendVillager(g);
      else if (m.type === 'buyPhase') run(mod, E.enterBuyPhase(g));
      else if (m.type === 'treasure') run(mod, E.playTreasureGen(g, m.id));
      else if (m.type === 'coffers') E.spendCoffers(g, m.n);
      else if (m.type === 'buy') { if (!run(mod, E.buyCard(g, m.id))) break; }
      else if (m.type === 'event') run(mod, E.buyEvent(g, m.id));
      else if (m.type === 'nightPhase') E.enterNightPhase(g);
      else if (m.type === 'night') run(mod, E.playNight(g, m.id));
      else break;
    }
    run(null, E.endTurn(g));
  }
  return g;
}

const games = Number(process.argv[2] || 200);
const pool = E.kingdomPool();
let wNew = 0; let wOld = 0; let draws = 0; let stalls = 0;
const t0 = Date.now();
let planMs = []; // 1 局目の最初の考える時間（NEW 側）を見る
for (let i = 0; i < games; i++) {
  const swap = i % 2 === 1;
  const mods = swap ? [OLD, NEW] : [NEW, OLD];
  const kingdom = E.randomKingdom(pool);
  const g0 = E.newGame(2, kingdom, ['a', 'b'], {});
  if (i < 20) { const t = Date.now(); NEW.planFor(g0, 0, 'expert'); planMs.push(Date.now() - t); }
  const g = playGame(kingdom, [], mods);
  if (!g) { stalls++; continue; }
  const r = E.finalResults(g);
  const top = r.filter((x) => x.rank === 1);
  if (top.length !== 1) { draws++; continue; }
  const winnerIsNew = (top[0].index === 0) === !swap;
  if (winnerIsNew) wNew++; else wOld++;
}
console.log(`new ${wNew} - ${wOld} old（引き分け ${draws}、打ち切り ${stalls}、${games} 局、${((Date.now() - t0) / 1000).toFixed(1)} 秒）`);
console.log(`new 勝率: ${(wNew / (wNew + wOld) * 100).toFixed(1)}%`);
planMs.sort((a, b) => a - b);
console.log(`考える時間（1 手番目、ms）: 最小 ${planMs[0]} 中央 ${planMs[Math.floor(planMs.length / 2)]} 最大 ${planMs.at(-1)}`);
