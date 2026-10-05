// 庭園（庭園ラッシュ）型が狙える、固定の王国で NEW（cpu.js）と OLD（cpu-baseline.js）を戦わせる。
//   node tools/test-rush.mjs [局数]
// 王国は「size」プリセット（庭園・工房・祝祭ほか）。あまり強くない札が多く、庭園ラッシュが有効な形。
import fs from 'node:fs';
import * as E from '../engine.js';
import * as NEW from '../cpu.js';
import * as OLD from '../cpu-baseline.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

// 庭園・獲得札 2 種（工房・鉄工所）・木こり（+購入）と、あまり強くない札だけの王国。庭園ラッシュが働きやすい形
const KINGDOM = ['meadow', 'workshop', 'foundry', 'woodsman', 'abbey', 'command', 'warehouse', 'crier', 'hunter', 'attendant'];

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
console.log(`庭園ラッシュの王国（size）: new ${wNew} - ${wOld} old（引き分け ${draws}、打ち切り ${stalls}、${games} 局、${((Date.now() - t0) / 1000).toFixed(1)} 秒）`);
console.log(`new 勝率: ${(wNew / (wNew + wOld) * 100).toFixed(1)}%`);
