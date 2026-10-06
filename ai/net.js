'use strict';
// AI の推論（手書き。行列の積と ReLU だけ。docs/ai-design.md §2・§5）。外部ライブラリなし。
//   loadModel(meta, buffer)           … model.json（meta）と model.bin（float16 の ArrayBuffer）から作る
//   evaluate(model, base, cand)       … 候補を選んだあとの状態の、[自分の勝つ見込み, 相手の勝つ見込み]
//   scoreCandidates(model, base, cands) … 候補ごとの「自分の勝つ見込み」
// 形（model.json の shapes に書いてある）: D = 32
//   カードのベクトル = Wp·性質 + bp + emb[ID の番号]（ID が並びにない札は埋め込みなし）
//   袋（デッキの中身など）= Σ log(1+枚数) × カードのベクトル
//   サプライ = Σ relu(Ws·[カードのベクトル; 残り・コスト・禁輸・勝利点] + bs)（Deep Sets）
//   全部をつなぎ（袋 5・サプライ・数値・候補のベクトルと種類と値）→ relu(W1) → relu(W2) → W3 → softmax（自分・相手）
import { postState, cardProps, supplyExt, bagWeight, candExt, P, NS, SUPPLY_EXT, CAND_EXT, KINDS, BAGS } from './features.js';

function f16(h) {
  const e = (h >> 10) & 31;
  const m = h & 1023;
  const v = e === 0 ? m * 2 ** -24 : e === 31 ? (m ? NaN : Infinity) : (1 + m / 1024) * 2 ** (e - 15);
  return h & 0x8000 ? -v : v;
}

export const inSize = (D) => BAGS.length * D + D + NS + D + KINDS + CAND_EXT;

// meta.shapes の順に、float16 を Float32Array に直して名前で引けるようにする
export function loadModel(meta, buffer) {
  const raw = new Uint16Array(buffer);
  const w = {};
  let off = 0;
  for (const [name, shape] of Object.entries(meta.shapes)) {
    const n = shape.reduce((a, b) => a * b, 1);
    const a = new Float32Array(n);
    for (let i = 0; i < n; i++) a[i] = f16(raw[off + i]);
    w[name] = a;
    off += n;
  }
  if (off !== raw.length) throw new Error(`model.bin の大きさが model.json と合わない（${off} と ${raw.length}）`);
  const D = meta.dim;
  const index = new Map(meta.ids.map((id, i) => [id, i + 1])); // 0 は「並びにない札」
  if (meta.shapes.emb[0] !== meta.ids.length + 1 || meta.shapes.Wp[1] !== P || meta.shapes.W1[1] !== inSize(D)) throw new Error('model.json の形が特徴量と合わない');
  return { meta, w, D, H: meta.hidden, index, cache: new Map() };
}

function cardVec(m, id) {
  let v = m.cache.get(id);
  if (v) return v;
  const { D, w } = m;
  v = new Float32Array(D);
  const pr = cardProps(id);
  for (let o = 0; o < D; o++) {
    let s = w.bp[o];
    for (let i = 0; i < P; i++) s += w.Wp[o * P + i] * pr[i];
    v[o] = s;
  }
  const idx = m.index.get(id);
  if (idx) for (let o = 0; o < D; o++) v[o] += w.emb[idx * D + o];
  m.cache.set(id, v);
  return v;
}

function dense(W, b, x, nOut, nIn, relu) {
  const y = new Float32Array(nOut);
  for (let o = 0; o < nOut; o++) {
    let s = b[o];
    const r = o * nIn;
    for (let i = 0; i < nIn; i++) s += W[r + i] * x[i];
    y[o] = relu && s < 0 ? 0 : s;
  }
  return y;
}

export function evaluate(m, base, cand) {
  const { D, H, w } = m;
  const st = postState(base, cand);
  const x = new Float32Array(inSize(D));
  let at = 0;
  for (const bag of st.bags) {
    for (const [id, n] of bag) { const v = cardVec(m, id); const k = bagWeight(n); for (let o = 0; o < D; o++) x[at + o] += k * v[o]; }
    at += D;
  }
  const z = new Float32Array(D + SUPPLY_EXT);
  for (const s of st.supply) {
    z.set(cardVec(m, s.id), 0);
    z.set(supplyExt(s), D);
    const h = dense(w.Ws, w.bs, z, D, D + SUPPLY_EXT, true);
    for (let o = 0; o < D; o++) x[at + o] += h[o];
  }
  at += D;
  x.set(st.scalars, at); at += NS;
  if (cand.id) x.set(cardVec(m, cand.id), at);
  at += D;
  x[at + cand.kind] = 1; at += KINDS;
  x.set(candExt(cand), at);
  const h1 = dense(w.W1, w.b1, x, H, x.length, true);
  const h2 = dense(w.W2, w.b2, h1, H, H, true);
  const l = dense(w.W3, w.b3, h2, 2, H, false);
  const mx = Math.max(l[0], l[1]);
  const a = Math.exp(l[0] - mx);
  const b = Math.exp(l[1] - mx);
  return [a / (a + b), b / (a + b)];
}

export const scoreCandidates = (m, base, cands) => cands.map((c) => evaluate(m, base, c)[0]);
