// 圧縮型（礼拝堂で山を薄くして高回転にする型）が狙える、固定の王国で NEW（cpu.js）と OLD（cpu-baseline.js）を戦わせる。
//   node tools/test-thin.mjs [局数]
// 王国は礼拝堂・研究所・市場と、あまり強くない札だけ（庭園・魔女のような別の型が強い札は入れない）。
import fs from 'node:fs';
import * as E from '../engine.js';
import * as NEW from '../cpu.js';
import * as OLD from '../cpu-baseline.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

// 「銀貨と金貨」プリセット（礼拝堂・研究所があり、庭園・魔女のような別の型が強い札はない）
const KINGDOM = ['highwayman', 'official', 'abbey', 'crier', 'alembic', 'moneylender', 'mine', 'pawnbroker', 'command', 'attendant'];

function playGame(kingdom, mods) {
  const g = E.newGame(mods.length, kingdom, mods.map((_, i) => `P${i + 1}`), {});
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

const games = Number(process.argv[2] || 100);
let wNew = 0; let wOld = 0; let draws = 0; let stalls = 0;
const t0 = Date.now();
for (let i = 0; i < games; i++) {
  const swap = i % 2 === 1;
  const mods = swap ? [OLD, NEW] : [NEW, OLD];
  const g = playGame(KINGDOM, mods);
  if (!g) { stalls++; continue; }
  const r = E.finalResults(g);
  const top = r.filter((x) => x.rank === 1);
  if (top.length !== 1) { draws++; continue; }
  const winnerIsNew = (top[0].index === 0) === !swap;
  if (winnerIsNew) wNew++; else wOld++;
}
console.log(`圧縮型の王国（礼拝堂）: new ${wNew} - ${wOld} old（引き分け ${draws}、打ち切り ${stalls}、${games} 局、${((Date.now() - t0) / 1000).toFixed(1)} 秒）`);
console.log(`new 勝率: ${(wNew / (wNew + wOld) * 100).toFixed(1)}%`);
