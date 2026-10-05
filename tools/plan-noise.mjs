// さいきょう CPU の型選び（planFor）が、同じ王国でどれだけぶれるかを測る。
//   node tools/plan-noise.mjs [回数] [王国の数]
// 王国ごとに N 回 planFor を呼び、一番多く選ばれた型の割合（一致率）を出す。平均が低いほどぶれが大きい。
import fs from 'node:fs';
import * as E from '../engine.js';
import { planFor } from '../cpu.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

const repeats = Number(process.argv[2] || 8);
const kingdoms = Number(process.argv[3] || 10);
const pool = E.kingdomPool();

function planKey(plan) {
  if (!plan || !plan.length) return '(none)';
  const parts = plan.map((p) => `${p.pile}:${p.limit}${p.event ? 'e' : ''}`).sort();
  return (plan.style || '') + '/' + parts.join(',');
}

let agreements = [];
const t0 = Date.now();
for (let i = 0; i < kingdoms; i++) {
  const kingdom = E.randomKingdom(pool);
  const counts = new Map();
  for (let r = 0; r < repeats; r++) {
    const g = E.newGame(2, kingdom, ['a', 'b'], {});
    const plan = planFor(g, 0, 'expert');
    const key = planKey(plan);
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  const top = Math.max(...counts.values());
  const agree = top / repeats;
  agreements.push(agree);
  console.log(`王国 ${i + 1}: 一致率 ${(agree * 100).toFixed(0)}%（${[...counts.entries()].map(([k, c]) => `${k}×${c}`).join(' / ')}）`);
}
const avg = agreements.reduce((a, b) => a + b, 0) / agreements.length;
console.log(`平均一致率: ${(avg * 100).toFixed(1)}%（${kingdoms} 王国 × ${repeats} 回、${((Date.now() - t0) / 1000).toFixed(1)} 秒）`);
