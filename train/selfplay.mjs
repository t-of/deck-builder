// 自己対局の記録（docs/ai-design.md §4・「記録の形」）。N 局打って、買う・獲得する判断ごとの特徴量と、最後の結果を書く。
//   node train/selfplay.mjs --games 20 --mode expert|ai|self --out runs/x/shard0 [--seed 1] [--model ai/model] [--temp 0.05] [--base] [--preset <id>]
//                           [--opp-model 名前（self で、相手の席を別のモデルにする）] [--f32（小数を float32 で書く）] [--check N（最初の N 判断の全候補を JS の net で評価して checkOut に書く。train/check_equiv.py 用）]
//   expert … さいきょう同士の棋譜（約 20 秒／局）。ai … AI（席は局ごとに交代）対 さいきょう。AI のも さいきょう のも記録する。self … AI 同士
//   --base: 基本の王国だけ（段階 1）。省略すると全拡張・ランドスケープ 0〜2 枚
// 出力: <out>.json（配列の名前・型・形・オフセット）と <out>.bin（配列を順に並べたもの。リトルエンディアン）
import fs from 'node:fs';
import path from 'node:path';
import { kingdomPool, landscapePool, randomKingdom, PRESETS, finalResults, CARDS } from '../engine.js';
import { encode, cardProps, supplyExt, candExt, BAGS, SCALARS, NS, P, SUPPLY_EXT, CAND_EXT } from '../ai/features.js';
import { loadModel, evaluate } from '../ai/net.js';
import { toF16 } from './f16.mjs';
import { createAI, expertActor, playGame } from '../ai/player.js';

const dir = new URL('..', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`);

const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : (process.argv[i + 1] ?? true); };
const games = Number(arg('games', 20));
const mode = arg('mode', 'expert');
const out = arg('out', 'runs/test/shard0');
let seed = Number(arg('seed', 1)) >>> 0;
const temp = Number(arg('temp', 0.05));
const onlyBase = process.argv.includes('--base');
const presetId = arg('preset', null); // 指定したら毎局その王国（--base より優先）
const preset = presetId && PRESETS.find((p) => p.id === presetId);
if (presetId && !preset) { console.error(`知らない preset: ${presetId}`); process.exit(1); }
const modelPath = arg('model', `${dir}ai/model`);

const f32 = process.argv.includes('--f32');
const checkN = Number(arg('check', 0));
const FT = f32 ? 'float32' : 'float16'; // 数値の保存の型。float16 で十分（学習の入力。JS と PyTorch の一致を見るときだけ float32）
const load = (p) => { const b = fs.readFileSync(`${p}.bin`); return loadModel(JSON.parse(fs.readFileSync(`${p}.json`, 'utf8')), b.buffer.slice(b.byteOffset, b.byteOffset + b.length)); };
const model = load(modelPath);
const oppModel = arg('opp-model', null) ? load(arg('opp-model')) : model;
const idxOf = (id) => model.index.get(id) || 0;

// 乱数（王国・ランドスケープを決める。局ごとに種を変える）
const rnd = () => { seed = (seed + 0x6d2b79f5) >>> 0; let t = Math.imul(seed ^ (seed >>> 15), seed | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const realRandom = Math.random;
Math.random = rnd; // randomKingdom が Math.random を使う。--seed で同じ列になる

const A = {};
const push = (name, type, ...vals) => { (A[name] ||= { type, data: [] }).data.push(...vals); };
const pool = kingdomPool(onlyBase ? ['base'] : undefined);
const lpool = onlyBase ? [] : landscapePool();
let nDec = 0;
let nCand = 0;
let gi = 0;
let kept = 0; // 打ち切りを除いた局の数（decGame・gameResult の番号）
let seat = 0;

function record({ me, base, cands, chosen, source }) {
  push('decGame', 'int32', kept); push('decSeat', 'int8', me); push('decSource', 'int8', source === 'ai' ? 1 : 0); push('decChosen', 'int16', chosen);
  push('scalars', FT, ...base.scalars);
  for (const bag of base.bags) {
    push('bagOff', 'int32', (A.bagIdx?.data.length) || 0);
    for (const [id, n] of bag) { push('bagIdx', 'int16', idxOf(id)); push('bagCnt', 'int16', n); }
  }
  push('supOff', 'int32', (A.supIdx?.data.length) || 0);
  for (const s of base.supply) { push('supIdx', 'int16', idxOf(s.id)); push('supExt', FT, ...supplyExt(s)); }
  push('candOff', 'int32', nCand);
  for (const c of cands) { push('candKind', 'int8', c.kind); push('candIdx', 'int16', idxOf(c.id)); push('candExt', FT, ...candExt(c)); }
  if (nDec < checkN) for (const c of cands) push('checkOut', 'float32', ...evaluate(model, base, c));
  nCand += cands.length;
  nDec++;
}

const t0 = Date.now();
let stalls = 0;
for (gi = 0; gi < games; gi++) {
  const kingdom = preset ? [...preset.cards] : randomKingdom(pool);
  const landscapes = preset ? [...(preset.landscapes || [])] : randomKingdom(lpool, lpool.length ? Math.floor(rnd() * 3) : 0);
  const onDecision = (d) => record(d);
  seat = gi % 2;
  const ai = (m) => createAI(m, { temperature: temp, rand: rnd, onDecision });
  const actors = mode === 'ai' ? [0, 1].map((i) => (i === seat ? ai(model) : expertActor({ onDecision })))
    : mode === 'self' ? [0, 1].map((i) => ai(i === seat ? model : oppModel))
      : [expertActor({ onDecision }), expertActor({ onDecision })];
  const before = [nDec, nCand, Object.fromEntries(Object.entries(A).map(([k, v]) => [k, v.data.length]))];
  const g = playGame({ kingdom, landscapes, actors, seed: Math.floor(rnd() * 2 ** 31) });
  if (!g) { // 打ち切りは捨てる（記録を巻き戻す）
    stalls++; nDec = before[0]; nCand = before[1];
    for (const [k, v] of Object.entries(A)) v.data.length = before[2][k] ?? 0;
    continue;
  }
  const r = finalResults(g);
  const top = r.filter((x) => x.rank === 1);
  const res = [0, 0];
  for (const x of top) res[x.index] = top.length === 1 ? 1 : 0.5;
  push('gameResult', 'float32', ...res); push('gameTurns', 'int16', g.players[0].turnsTaken);
  push('gameSeatAI', 'int8', mode === 'ai' ? seat : mode === 'self' ? 2 : -1);
  kept++;
}
Math.random = realRandom;
// ragged の終わりの番兵
push('candOff', 'int32', nCand); push('supOff', 'int32', A.supIdx?.data.length || 0); push('bagOff', 'int32', A.bagIdx?.data.length || 0);
const ids = model.meta.ids;
const props = new Float32Array((ids.length + 1) * P);
ids.forEach((id, i) => props.set(cardProps(id), (i + 1) * P));
A.cardProps = { type: 'float32', data: props };

const TYPED = { int8: Int8Array, int16: Int16Array, int32: Int32Array, float32: Float32Array, float16: Uint16Array };
const header = { version: 1, games: Object.keys(A).length ? A.gameResult.data.length / 2 : 0, decisions: nDec, candidates: nCand, ns: NS, p: P, supplyExt: SUPPLY_EXT, candExt: CAND_EXT, bags: BAGS, scalars: SCALARS, mode, arrays: {} };
const chunks = [];
let off = 0;
for (const [name, { type, data }] of Object.entries(A)) {
  const arr = type === 'float16' ? Uint16Array.from(data, toF16) : TYPED[type].from(data);
  const buf = Buffer.from(arr.buffer, arr.byteOffset, arr.byteLength);
  header.arrays[name] = { type, length: arr.length, offset: off };
  chunks.push(buf);
  off += buf.length;
}
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(`${out}.bin`, Buffer.concat(chunks));
fs.writeFileSync(`${out}.json`, JSON.stringify(header, null, 1));
const sec = (Date.now() - t0) / 1000;
console.log(`${games - stalls} 局（打ち切り ${stalls}）、判断 ${nDec}、候補 ${nCand}、${sec.toFixed(1)} 秒（${(sec / games).toFixed(2)} 秒／局）、${off} バイト → ${out}.bin`);
