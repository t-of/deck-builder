// 強さの測定（docs/ai-design.md §7）。A 対 B を N 局、先手を交互にして、王国は A・B で同じ列。
//   node train/match.mjs --a runs/x/gen_3 --b expert|strong|normal|weak|<モデル>|table:<表の JSON>|table:seed:<定石> --games 40 [--seed 1] [--temp 0] [--base] [--preset <id>]
// 最後の行: RESULT <A の勝ち> <引き分け> <A の負け> <局数>（HAKUSAN では複数の種で並べて足す）
import fs from 'node:fs';
import { kingdomPool, landscapePool, randomKingdom, PRESETS, finalResults } from '../engine.js';
import { loadModel } from '../ai/net.js';
import { createAI, playGame } from '../ai/player.js';
import { nextMove as cpuMove, answer as cpuAnswer } from '../cpu.js';
import { tableActor, SEEDS } from '../ai/table.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : (process.argv[i + 1] ?? true); };
const games = Number(arg('games', 40));
let seed = Number(arg('seed', 1)) >>> 0;
const temp = Number(arg('temp', 0));
const onlyBase = process.argv.includes('--base');
const presetId = arg('preset', null); // 指定したら毎局その王国（--base より優先）
const preset = presetId && PRESETS.find((p) => p.id === presetId);
if (presetId && !preset) { console.error(`知らない preset: ${presetId}`); process.exit(1); }
const load = (p) => { const b = fs.readFileSync(`${p}.bin`); return loadModel(JSON.parse(fs.readFileSync(`${p}.json`, 'utf8')), b.buffer.slice(b.byteOffset, b.byteOffset + b.length)); };
const rnd = () => { seed = (seed + 0x6d2b79f5) >>> 0; let t = Math.imul(seed ^ (seed >>> 15), seed | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
Math.random = rnd;
// 買い方表: table:<JSON のパス>（表そのもの、または train/evolve.mjs の gen_N.json＝top[0]）か table:seed:<定石の名前>
const loadTable = (w) => { const k = w.slice(11); if (w.startsWith('table:seed:')) return SEEDS[k]; const j = JSON.parse(fs.readFileSync(w.slice(6), 'utf8')); return j.top ? j.top[0].table : j; };
const mk = (who) => (who.startsWith('table:') ? (() => { const t = loadTable(who); return () => tableActor(t); })() : ['weak', 'normal', 'strong', 'expert'].includes(who)
  ? () => ({ nextMove: (g) => cpuMove(g, who), answer: (g, q) => cpuAnswer(g, q, who) })
  : ((m) => () => createAI(m, { temperature: temp, rand: rnd }))(load(who)));
const makeA = mk(arg('a'));
const makeB = mk(arg('b', 'expert'));
const pool = kingdomPool(onlyBase ? ['base'] : undefined);
const lpool = onlyBase ? [] : landscapePool();
let w = 0; let d = 0; let l = 0;
for (let i = 0; i < games; i++) {
  const kingdom = preset ? [...preset.cards] : randomKingdom(pool);
  const landscapes = preset ? [...(preset.landscapes || [])] : randomKingdom(lpool, lpool.length ? Math.floor(rnd() * 3) : 0);
  const gs = Math.floor(rnd() * 2 ** 31);
  const aSeat = i % 2;
  const g = playGame({ kingdom, landscapes, actors: [0, 1].map((s) => (s === aSeat ? makeA() : makeB())), seed: gs });
  if (!g) { console.log(`局 ${i}: 打ち切り`); continue; }
  const top = finalResults(g).filter((x) => x.rank === 1);
  if (top.length > 1) d++; else if (top[0].index === aSeat) w++; else l++;
}
console.log(`RESULT ${w} ${d} ${l} ${w + d + l}`);
