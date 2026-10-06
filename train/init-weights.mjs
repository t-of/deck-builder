// 決まった種の乱数で、学習していない重みを作る（形の確認・手元の試験用）。
//   node train/init-weights.mjs [出力の名前 ai/model] [種 1]
// 出力: <名前>.json（形・ID の並び・版）と <名前>.bin（float16、model.json の shapes の順）
// 埋め込み emb は 0 で始める（設計メモ §2）。ほかは He の初期値（一様乱数）、バイアスは 0
import fs from 'node:fs';
import { CARDS } from '../engine.js';
import { P, NS, SUPPLY_EXT } from '../ai/features.js';
import { inSize } from '../ai/net.js';
import { toF16 } from './f16.mjs';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

const out = process.argv[2] || `${dir}ai/model`;
const seed = Number(process.argv[3] || 1);
const D = 32;
const H = 256;
const ids = Object.keys(CARDS).sort();

let s = seed >>> 0;
const rand = () => { s = (s + 0x6d2b79f5) >>> 0; let t = Math.imul(s ^ (s >>> 15), s | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

const shapes = {
  emb: [ids.length + 1, D], Wp: [D, P], bp: [D], Ws: [D, D + SUPPLY_EXT], bs: [D],
  W1: [H, inSize(D)], b1: [H], W2: [H, H], b2: [H], W3: [2, H], b3: [2],
};
const parts = [];
for (const [name, shape] of Object.entries(shapes)) {
  const n = shape.reduce((a, b) => a * b, 1);
  const a = new Uint16Array(n);
  if (name[0] === 'W') { const k = Math.sqrt(6 / shape[1]); for (let i = 0; i < n; i++) a[i] = toF16((rand() * 2 - 1) * k); }
  parts.push(a);
}
const bin = Buffer.concat(parts.map((a) => Buffer.from(a.buffer)));
const params = Object.values(shapes).reduce((acc, sh) => acc + sh.reduce((a, b) => a * b, 1), 0);
const meta = { version: 1, dtype: 'float16', dim: D, hidden: H, outputs: 2, props: P, scalars: NS, seed, params, ids, shapes };
fs.writeFileSync(`${out}.json`, JSON.stringify(meta));
fs.writeFileSync(`${out}.bin`, bin);
console.log(`${out}.json / .bin: ID ${ids.length} 種、パラメータ ${params}、${bin.length} バイト`);
