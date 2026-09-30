// CPU の試験: CPU どうしで対局させ、落ちない・終わる・強さの順（つよい > ふつう > よわい）を見る。
//   node test/cpu.mjs [局数] [base=基本だけ / all] [対戦の組 'strong,normal;normal,weak']
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as E from '../engine.js';
import { simulate } from '../cpu.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

export function playGame(kingdom, levels, landscapes = []) {
  const g = simulate(kingdom, landscapes, levels);
  return { g, stalled: !g };
}

const isMain = process.argv[1] && process.argv[1].endsWith('cpu.mjs');
const games = Number(process.argv[2] || 60);
const onlyBase = process.argv[3] === 'base';
const pool = E.kingdomPool(onlyBase ? ['base'] : undefined);
function match(a, b) {
  let wa = 0; let wb = 0; let stalls = 0;
  for (let i = 0; i < games; i++) {
    const swap = i % 2 === 1;
    const levels = swap ? [b, a] : [a, b];
    const { g, stalled } = playGame(E.randomKingdom(pool), levels);
    if (stalled) { stalls++; continue; }
    const r = E.finalResults(g);
    const win = r.filter((x) => x.rank === 1).map((x) => levels[x.index]);
    if (win.length === 1) { if (win[0] === a) wa++; else wb++; }
  }
  return { wa, wb, stalls };
}
if (isMain) {
const t0 = Date.now();
const which = process.argv[4] || 'strong,normal;normal,weak';
for (const pair of which.split(';')) {
  const [a, b] = pair.split(',');
  const m = match(a, b);
  console.log(`${a} ${m.wa} - ${m.wb} ${b}（打ち切り ${m.stalls}）`);
  if (a === 'normal' && b === 'weak') assert.ok(m.wa > m.wb, 'ふつうがよわいに勝てていない');
}
console.log(`${((Date.now() - t0) / 1000).toFixed(1)} 秒`);
}
