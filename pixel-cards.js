// ドット絵のカード絵柄。16×16 の升目に、種類ごとの絵をコードで組み立てる（手描きの表は持たない）。
// carcassonne の pixel-tiles.js と同じ考え方: 図形の関数を組み合わせて、カード ID ごとに 1 枚の絵を作る。
(function (g) {
  const N = 16;
  const T = 255; // 透明（palette の外）

  const PALETTE = [
    '#2a2018', // 0 ふちの墨
    '#b87333', '#d99a5b', '#7a4a1e', // 1-3 銅：地・明・影
    '#c9ccd1', '#eef0f3', '#8f939c', // 4-6 銀：地・明・影
    '#e8b83a', '#f6d878', '#a8791c', // 7-9 金：地・明・影
    '#8e6436', '#b98a52', '#5a3f22', // 10-12 木：地・明・影
    '#c8503c', '#e6785a', '#8a3028', // 13-15 屋根：地・明・影
    '#efe8d8', '#b8a57a',            // 16-17 壁：地・影
    '#9aa0ab', '#c7ccd4', '#666c76', // 18-20 石：地・明・影
    '#3a5cc8', '#6a8ce0', '#25398a', // 21-23 水：地・明・影
    '#c7d0da', '#6d7480',            // 24-25 鋼：地・影
    '#e8763a', '#f7b25c',            // 26-27 炎：地・明
    '#4a8a5c', '#6bb37e',            // 28-29 草：地・明
  ];
  const [O, CU, CUl, CUd, SI, SIl, SId, GO, GOl, GOd, WD, WDl, WDd, RF, RFl, RFd, WL, WLd, ST, STl, STd, WT, WTl, WTd, ME, MEd, FL, FLl] = PALETTE.map((_, i) => i);

  function blank() { return new Uint8Array(N * N).fill(T); }
  function inb(x, y) { return x >= 0 && y >= 0 && x < N && y < N; }
  function set(px, x, y, c) { if (inb(x, y)) px[y * N + x] = c; }
  function rect(px, x, y, w, h, c) { for (let yy = y; yy < y + h; yy++) for (let xx = x; xx < x + w; xx++) set(px, xx, yy, c); }
  function frame(px, x, y, w, h, fill, edge) { rect(px, x, y, w, h, fill); for (let xx = x; xx < x + w; xx++) { set(px, xx, y, edge); set(px, xx, y + h - 1, edge); } for (let yy = y; yy < y + h; yy++) { set(px, x, yy, edge); set(px, x + w - 1, yy, edge); } }
  // 三角の屋根。頂点が上、底辺が幅 w
  function roof(px, x, y, w, h, base, light, dark) {
    for (let r = 0; r < h; r++) {
      const half = Math.max(1, Math.round(((r + 1) / h) * (w / 2)));
      for (let c = -half; c < half; c++) set(px, x + w / 2 + c, y + r, c < -half + 2 ? light : c >= half - 2 ? dark : base);
      set(px, x + w / 2 - half, y + r, O); set(px, x + w / 2 + half - 1, y + r, O);
    }
  }
  function circle(px, cx, cy, r, base, light, dark, edge) {
    for (let y = cy - r; y <= cy + r; y++) for (let x = cx - r; x <= cx + r; x++) {
      const d = Math.hypot(x - cx + 0.5, y - cy + 0.5);
      if (d > r + 0.3) continue;
      const c = d > r - 1 ? edge : (x - cx) - (y - cy) > 1 ? light : (y - cy) - (x - cx) > 1 ? dark : base;
      set(px, x, y, c);
    }
  }
  function diamond(px, cx, cy, r, base, edge) {
    for (let y = -r; y <= r; y++) for (let x = -r; x <= r; x++) {
      if (Math.abs(x) + Math.abs(y) > r) continue;
      set(px, cx + x, cy + y, Math.abs(x) + Math.abs(y) === r ? edge : base);
    }
  }
  function lineThick(px, x0, y0, x1, y1, c, w) {
    const dx = x1 - x0, dy = y1 - y0, steps = Math.max(Math.abs(dx), Math.abs(dy));
    for (let i = 0; i <= steps; i++) {
      const x = Math.round(x0 + (dx * i) / steps), y = Math.round(y0 + (dy * i) / steps);
      for (let ox = -w >> 1; ox <= w >> 1; ox++) for (let oy = -w >> 1; oy <= w >> 1; oy++) set(px, x + ox, y + oy, c);
    }
  }

  // ---- 財宝: 円貨。中の点の数で銅(1)・銀(2)・金(3)を見分ける ----
  function coin(base, light, dark, pips) {
    const px = blank();
    circle(px, 8, 8, 6, base, light, dark, O);
    const xs = pips === 1 ? [8] : pips === 2 ? [6, 10] : [5, 8, 11];
    for (const x of xs) set(px, x, 8, dark);
    return px;
  }
  // ---- 建物（勝利点）----
  function cottage() { // 小屋
    const px = blank();
    roof(px, 4, 3, 8, 4, RF, RFl, RFd);
    frame(px, 5, 7, 6, 6, WL, O);
    rect(px, 7, 10, 2, 3, WDd);
    return px;
  }
  function manor() { // 荘園
    const px = blank();
    roof(px, 2, 2, 12, 5, WTd, WTl, WT);
    frame(px, 3, 7, 10, 7, ST, O);
    rect(px, 5, 9, 2, 2, WT); rect(px, 9, 9, 2, 2, WT);
    rect(px, 7, 11, 2, 3, WDd);
    return px;
  }
  function castle() { // 領地: 塔2つ＋旗
    const px = blank();
    rect(px, 1, 6, 4, 9, ST); rect(px, 11, 6, 4, 9, ST);
    frame(px, 3, 4, 10, 11, STl, O);
    for (let x = 1; x < N; x += 2) { set(px, x, 5, O); set(px, x, 3, O); }
    lineThick(px, 8, 4, 8, 0, WDd, 1); set(px, 9, 0, RF); set(px, 9, 1, RF);
    rect(px, 6, 10, 4, 5, STd);
    return px;
  }
  // ---- アクション類 ----
  function warehouse() { // 倉庫: 木箱を2段
    const px = blank();
    frame(px, 3, 8, 10, 5, WD, O);
    frame(px, 4, 3, 8, 5, WDl, O);
    lineThick(px, 3, 8, 12, 12, WDd, 1); lineThick(px, 12, 8, 3, 12, WDd, 1);
    lineThick(px, 4, 3, 11, 7, WDd, 1); lineThick(px, 11, 3, 4, 7, WDd, 1);
    return px;
  }
  function moat() { // 水濠: 水面の波
    const px = blank();
    for (let y = 6; y < N; y++) for (let x = 0; x < N; x++) {
      const w = (x + y * 2) % 6;
      set(px, x, y, w < 1 ? WT : w < 3 ? WTl : WT);
    }
    rect(px, 2, 4, 12, 2, WDd);
    return px;
  }
  function moneylender() { // 両替商: 天秤
    const px = blank();
    lineThick(px, 8, 2, 8, 11, ME, 1);
    lineThick(px, 3, 4, 13, 4, ME, 1);
    lineThick(px, 3, 4, 3, 7, MEd, 1); lineThick(px, 13, 4, 13, 7, MEd, 1);
    circle(px, 3, 9, 2, GO, GOl, GOd, O);
    circle(px, 13, 9, 2, SI, SIl, SId, O);
    rect(px, 5, 12, 6, 2, WDd);
    return px;
  }
  function village() { // 集落: 小さな家3つ
    const px = blank();
    roof(px, 0, 6, 6, 3, RF, RFl, RFd); frame(px, 1, 9, 4, 4, WL, O);
    roof(px, 5, 3, 7, 4, WTd, WTl, WT); frame(px, 6, 7, 5, 6, ST, O);
    roof(px, 11, 7, 5, 3, RFd, RF, RFl); frame(px, 12, 10, 3, 3, WL, O);
    return px;
  }
  function workshop() { // 作業場: 金槌
    const px = blank();
    lineThick(px, 4, 13, 12, 5, WD, 2);
    frame(px, 9, 1, 6, 5, ME, O);
    rect(px, 10, 2, 2, 3, MEd);
    return px;
  }
  function mercenary() { // 傭兵: 剣と兜
    const px = blank();
    lineThick(px, 5, 2, 5, 11, ME, 2);
    lineThick(px, 2, 5, 8, 5, MEd, 1);
    rect(px, 4, 11, 2, 3, WDd);
    circle(px, 12, 6, 3, ST, STl, STd, O);
    rect(px, 10, 6, 5, 2, STd);
    rect(px, 11, 3, 2, 2, RF);
    return px;
  }
  function remodel() { // 建て替え: 足場
    const px = blank();
    for (const x of [2, 8, 13]) lineThick(px, x, 1, x, 14, WD, 1);
    for (const y of [3, 7, 11]) lineThick(px, 2, y, 13, y, WDl, 1);
    lineThick(px, 2, 1, 8, 7, WDd, 1); lineThick(px, 8, 7, 13, 3, WDd, 1);
    return px;
  }
  function smithy() { // 鍛冶場: 金床
    const px = blank();
    rect(px, 5, 3, 6, 2, MEd);
    for (let r = 0; r < 4; r++) rect(px, 3 - r, 5 + r, 10 + r * 2, 1, ME);
    rect(px, 6, 9, 4, 4, MEd);
    rect(px, 3, 13, 10, 2, ME);
    circle(px, 12, 4, 2, FL, FLl, FL, O);
    return px;
  }
  function market() { // 露店: 縞の屋根と台
    const px = blank();
    for (let r = 0; r < 4; r++) {
      const half = Math.round(((r + 1) / 4) * 7);
      for (let c = -half; c < half; c++) set(px, 8 + c, 2 + r, (c + 20) % 4 < 2 ? RF : WL);
    }
    frame(px, 3, 9, 10, 5, WD, O);
    circle(px, 6, 8, 1, RF, RFl, RFd, O);
    circle(px, 10, 8, 1, GO, GOl, GOd, O);
    return px;
  }
  function mine() { // 鉱脈: つるはしと鉱石
    const px = blank();
    lineThick(px, 2, 13, 10, 4, WD, 2);
    lineThick(px, 7, 2, 13, 5, ME, 2);
    lineThick(px, 7, 2, 3, 6, ME, 2);
    diamond(px, 12, 12, 3, WT, O);
    set(px, 12, 11, WTl);
    return px;
  }

  const BUILDERS = {
    copper: () => coin(CU, CUl, CUd, 1),
    silver: () => coin(SI, SIl, SId, 2),
    gold: () => coin(GO, GOl, GOd, 3),
    estate: cottage,
    duchy: manor,
    province: castle,
    warehouse, moat, moneylender, village, workshop, mercenary, remodel, smithy, market, mine,
  };

  // 種類ごとの枠の色（ドット絵テーマでカードのふちに使う）
  const FRAME = {
    treasure: '#e8b83a',
    victory: '#4a8a5c',
    action: '#3a5cc8',
    'action-attack': '#c8503c',
    'action-reaction': '#3a9c9c',
  };

  const cache = new Map();
  function build(id) {
    if (!cache.has(id)) cache.set(id, (BUILDERS[id] || (() => blank()))());
    return cache.get(id);
  }
  // canvas（の 2D context）に id の絵を描く。ctx.canvas の幅・高さぶんに拡大する
  function draw(ctx, id) {
    const px = build(id);
    const w = ctx.canvas.width, h = ctx.canvas.height, s = w / N;
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, w, h);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const v = px[y * N + x];
      if (v === T) continue;
      ctx.fillStyle = PALETTE[v];
      ctx.fillRect(Math.floor(x * s), Math.floor(y * s), Math.ceil(s), Math.ceil(s));
    }
  }

  g.PixelCards = { N, PALETTE, build, draw, frameColor: (type) => FRAME[type] || '#9aa0c0' };
})(typeof window !== 'undefined' ? window : globalThis);
