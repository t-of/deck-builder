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
  const [O, CU, CUl, CUd, SI, SIl, SId, GO, GOl, GOd, WD, WDl, WDd, RF, RFl, RFd, WL, WLd, ST, STl, STd, WT, WTl, WTd, ME, MEd, FL, FLl, GR, GRl] = PALETTE.map((_, i) => i);

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
  // ---- 新規 23 種 ----
  function abbey() { // 修道院: アーチ窓
    const px = blank();
    frame(px, 2, 2, 12, 13, ST, O);
    roof(px, 5, 1, 6, 5, GO, GOl, GOd);
    rect(px, 7, 6, 2, 8, GOl);
    return px;
  }
  function crier() { // 呼び込み: ラッパ
    const px = blank();
    lineThick(px, 2, 9, 9, 5, GO, 2);
    circle(px, 11, 5, 3, GOl, GO, GOd, O);
    rect(px, 4, 12, 5, 2, WDd);
    return px;
  }
  function attendant() { // 小姓: 盆とカップ
    const px = blank();
    rect(px, 2, 9, 12, 2, WD);
    circle(px, 5, 8, 2, WL, O, O, O);
    circle(px, 10, 8, 2, RF, RFl, RFd, O);
    return px;
  }
  function pawnbroker() { // 質屋: 天秤と質札
    const px = blank();
    lineThick(px, 4, 2, 4, 9, ME, 1);
    lineThick(px, 1, 4, 7, 4, ME, 1);
    circle(px, 1, 8, 2, SI, SIl, SId, O);
    circle(px, 7, 8, 2, SI, SIl, SId, O);
    frame(px, 9, 8, 6, 5, GOl, O);
    return px;
  }
  function official() { // 徴税官: 巻物
    const px = blank();
    frame(px, 2, 6, 12, 6, WL, O);
    circle(px, 8, 9, 1, RF, RFl, RFd, O);
    lineThick(px, 12, 2, 14, 6, ME, 1);
    return px;
  }
  function meadow() { // 花畑: 花の咲いた庭
    const px = blank();
    rect(px, 0, 10, 16, 6, ME);
    for (const [x, y] of [[2, 8], [6, 9], [9, 7], [12, 9], [4, 12], [11, 12]]) circle(px, x, y, 1, RF, RFl, RFd, RFd);
    return px;
  }
  function hunter() { // 狩人: 弓
    const px = blank();
    for (let y = 2; y < 14; y++) set(px, 5 + Math.round(Math.sin((y - 8) / 6) * 3), y, WD);
    lineThick(px, 5, 2, 5, 14, WDl, 1);
    circle(px, 11, 12, 2, MEd, MEd, MEd, O);
    return px;
  }
  function command() { // 号令: 旗
    const px = blank();
    lineThick(px, 4, 1, 4, 14, WDd, 1);
    for (let y = 1; y < 7; y++) rect(px, 5, y, 8 - (y - 1), 1, RF);
    return px;
  }
  function highwayman() { // 追いはぎ: 森の道の影
    const px = blank();
    rect(px, 0, 9, 16, 5, WDd);
    for (let y = 4; y < 10; y++) set(px, 8, y, O);
    circle(px, 8, 6, 3, O, O, O, O);
    circle(px, 13, 3, 2, GOl, GOl, GOl, O);
    return px;
  }
  function assembly() { // 集会所: 大広間
    const px = blank();
    roof(px, 1, 2, 14, 4, WTd, WTl, WT);
    frame(px, 2, 6, 12, 8, ST, O);
    rect(px, 4, 8, 2, 2, WT); rect(px, 10, 8, 2, 2, WT);
    rect(px, 7, 11, 2, 3, WDd);
    return px;
  }
  function fair() { // 縁日: 提灯と屋台
    const px = blank();
    frame(px, 2, 9, 12, 5, WD, O);
    for (const x of [3, 7, 11]) circle(px, x, 5, 2, GOl, GO, GOd, O);
    return px;
  }
  function alembic() { // 錬金室: フラスコ
    const px = blank();
    lineThick(px, 8, 2, 8, 7, WT, 1);
    circle(px, 8, 10, 4, WT, WTl, WTd, O);
    rect(px, 3, 13, 10, 2, WDd);
    return px;
  }
  function archive() { // 文書館: 本棚
    const px = blank();
    frame(px, 1, 2, 14, 12, WD, O);
    for (const [x, c] of [[3, RF], [6, ME], [9, GO], [12, WT]]) rect(px, x, 4, 2, 8, c);
    return px;
  }
  function sentinel() { // 番兵: 門と槍
    const px = blank();
    rect(px, 1, 3, 4, 11, ST); rect(px, 11, 3, 4, 11, ST);
    lineThick(px, 8, 1, 8, 13, ME, 1);
    lineThick(px, 8, 1, 5, 4, MEd, 1);
    return px;
  }
  function sorcerer() { // 呪術師: 紫の煙
    const px = blank();
    circle(px, 8, 12, 3, MEd, MEd, MEd, O);
    for (let i = 0; i < 6; i++) set(px, 8 + Math.round(Math.sin(i) * 3), 9 - i, FL);
    return px;
  }
  function craftsman() { // 工匠: 作業台
    const px = blank();
    frame(px, 2, 9, 12, 3, WD, O);
    lineThick(px, 3, 8, 7, 5, ME, 1);
    lineThick(px, 9, 7, 12, 4, ME, 1);
    return px;
  }
  function curse() { // 災い: 枯れ木と紫の雲
    const px = blank();
    rect(px, 1, 2, 14, 4, MEd);
    lineThick(px, 8, 6, 8, 14, WDd, 1);
    lineThick(px, 8, 8, 5, 6, WDd, 1); lineThick(px, 8, 9, 11, 7, WDd, 1);
    return px;
  }
  function explorer() { // 探検家: 地図と洞窟
    const px = blank();
    diamond(px, 11, 9, 4, WD, O);
    for (let y = 4; y < 9; y++) set(px, 11, y, O);
    frame(px, 1, 10, 7, 5, WL, O);
    return px;
  }
  function bursar() { // 会計係: 帳簿
    const px = blank();
    frame(px, 2, 5, 12, 8, WL, O);
    for (const y of [7, 9, 11]) lineThick(px, 4, y, 12, y, WLd, 1);
    return px;
  }
  function banquet() { // 晩餐: ごちそう
    const px = blank();
    rect(px, 1, 11, 14, 2, WDd);
    circle(px, 6, 9, 3, RF, RFl, RFd, O);
    rect(px, 11, 6, 2, 5, GOl);
    return px;
  }
  function scout() { // 物見: やぐら
    const px = blank();
    frame(px, 6, 4, 4, 10, WD, O);
    frame(px, 4, 1, 8, 3, WDl, O);
    return px;
  }
  function pickpocket() { // すり: 人ごみの手
    const px = blank();
    for (const x of [2, 6, 10, 13]) rect(px, x, 8, 3, 6, MEd);
    circle(px, 12, 6, 2, GOl, GO, GOd, O);
    return px;
  }
  function woodsman() { // 薪割り: 斧と薪
    const px = blank();
    circle(px, 6, 11, 4, WD, WDl, WDd, O);
    lineThick(px, 6, 11, 12, 3, WDd, 1);
    for (const x of [10, 12, 14]) set(px, x, 2, ME);
    return px;
  }
  // ---- 拡張「陰謀」32 種 ----
  function backyard() { // 裏庭: 柵と木
    const px = blank();
    for (let x = 1; x < 8; x += 3) lineThick(px, x, 14, x, 9, WDd, 1);
    lineThick(px, 1, 11, 7, 11, WDd, 1);
    circle(px, 12, 7, 4, GR, GRl, GR, O);
    rect(px, 11, 11, 2, 3, WDd);
    return px;
  }
  function prowler() { // 忍び: 屋根を跳ぶ影
    const px = blank();
    roof(px, 0, 8, 7, 4, O, O, O);
    roof(px, 8, 4, 8, 5, O, O, O);
    lineThick(px, 6, 8, 10, 4, O, 1);
    return px;
  }
  function errand() { // 使い走り: 走る足あと
    const px = blank();
    circle(px, 8, 4, 2, WL, O, O, O);
    lineThick(px, 8, 6, 8, 11, ME, 1);
    for (const [x, y] of [[2, 13], [5, 12], [9, 12], [12, 13]]) set(px, x, y, WDd);
    return px;
  }
  function carnival() { // 仮装行列: 仮面
    const px = blank();
    circle(px, 8, 8, 6, WL, O, O, O);
    set(px, 5, 6, O); set(px, 11, 6, O);
    lineThick(px, 5, 11, 11, 11, O, 1);
    for (const [x, y] of [[2, 2], [13, 3], [3, 13], [13, 12]]) set(px, x, y, RF);
    return px;
  }
  function slum() { // 長屋: 並んだ小屋
    const px = blank();
    for (const x of [0, 6, 11]) { roof(px, x, 8, 5, 3, RFd, RF, RFl); frame(px, x + 1, 11, 3, 4, WL, O); }
    return px;
  }
  function butler() { // 家令: 盆と蓋
    const px = blank();
    rect(px, 2, 10, 12, 2, WD);
    circle(px, 8, 7, 4, SI, SIl, SId, O);
    set(px, 8, 3, SId);
    return px;
  }
  function conman() { // ぺてん師: 三つ椀
    const px = blank();
    for (const x of [3, 8, 13]) circle(px, x, 10, 2, RF, RFl, RFd, O);
    set(px, 8, 4, O);
    lineThick(px, 5, 6, 11, 6, O, 1);
    return px;
  }
  function fountain() { // 占いの泉: 水盤
    const px = blank();
    circle(px, 8, 11, 6, ST, STl, STd, O);
    circle(px, 8, 11, 4, WT, WTl, WTd, O);
    for (const [x, y] of [[6, 4], [9, 3], [8, 6]]) set(px, x, y, WTl);
    return px;
  }
  function landlord() { // 地主: 小屋と看板
    const px = blank();
    roof(px, 0, 7, 7, 3, RFd, RF, RFl); frame(px, 1, 10, 5, 5, WL, O);
    lineThick(px, 11, 4, 11, 14, WDd, 1);
    rect(px, 8, 3, 6, 3, WLd);
    return px;
  }
  function suspension() { // つり橋
    const px = blank();
    lineThick(px, 2, 2, 2, 14, WDd, 1); lineThick(px, 14, 2, 14, 14, WDd, 1);
    for (let x = 2; x <= 14; x += 2) {
      const y = 9 - Math.round(3 * Math.sin((x - 2) / 12 * Math.PI));
      set(px, x, y, ME);
    }
    lineThick(px, 2, 11, 14, 11, WD, 1);
    return px;
  }
  function plotter() { // 黒幕: 影の人物
    const px = blank();
    for (let r = 0; r < 9; r++) for (let c = -Math.round(r * 0.35); c <= Math.round(r * 0.35); c++) set(px, 8 + c, 13 - r, O);
    circle(px, 8, 5, 2, O, O, O, O);
    set(px, 13, 12, GOl);
    return px;
  }
  function envoy() { // 使節: 手紙と馬
    const px = blank();
    rect(px, 1, 9, 7, 5, WDd);
    lineThick(px, 1, 9, 1, 13, WDd, 2); lineThick(px, 8, 9, 8, 13, WDd, 2);
    frame(px, 9, 4, 6, 5, WL, O);
    set(px, 12, 6, RF);
    return px;
  }
  function foundry() { // 鋳造所: 炉と金床
    const px = blank();
    circle(px, 5, 9, 4, FL, FLl, FL, O);
    rect(px, 10, 10, 5, 2, ME);
    rect(px, 11, 12, 3, 2, MEd);
    return px;
  }
  function watermill() { // 水車小屋
    const px = blank();
    circle(px, 8, 8, 5, WD, WDl, WDd, O);
    lineThick(px, 8, 3, 8, 13, WDd, 1); lineThick(px, 3, 8, 13, 8, WDd, 1);
    rect(px, 0, 12, 16, 3, WT);
    return px;
  }
  function minetown() { // 鉱山町
    const px = blank();
    frame(px, 2, 6, 5, 7, ST, O);
    frame(px, 9, 8, 5, 5, ST, O);
    circle(px, 5, 14, 2, ME, ME, MEd, O);
    circle(px, 11, 14, 2, ME, ME, MEd, O);
    return px;
  }
  function tunnel() { // 抜け道
    const px = blank();
    for (let r = 0; r < 7; r++) { const half = 6 - r; for (let c = -half; c < half; c++) set(px, 8 + c, 13 - r, r < 3 ? GOl : O); }
    return px;
  }
  function chamberlain() { // 侍従: 扉と鍵
    const px = blank();
    frame(px, 5, 2, 6, 12, WD, O);
    circle(px, 2, 12, 2, GO, GOl, GOd, O);
    lineThick(px, 4, 12, 7, 12, GO, 1);
    return px;
  }
  function marquis() { // 侯爵: 高台の館
    const px = blank();
    roof(px, 3, 2, 10, 5, WTd, WTl, WT);
    frame(px, 4, 7, 8, 6, ST, O);
    roof(px, 0, 10, 4, 2, RFd, RF, RFl); frame(px, 0, 12, 3, 2, WL, O);
    roof(px, 12, 10, 4, 2, RFd, RF, RFl); frame(px, 13, 12, 3, 2, WL, O);
    return px;
  }
  function henchman() { // 子分: 三人組
    const px = blank();
    for (const x of [2, 7, 12]) { rect(px, x, 8, 3, 6, MEd); circle(px, x + 1, 6, 2, ME, ME, MEd, O); }
    return px;
  }
  function nightwatch() { // 夜回り: ランタン
    const px = blank();
    rect(px, 7, 2, 2, 8, MEd);
    circle(px, 8, 11, 3, GOl, GO, GOd, O);
    rect(px, 6, 14, 4, 1, MEd);
    return px;
  }
  function swap() { // 取り替え
    const px = blank();
    circle(px, 4, 5, 3, CU, CUl, CUd, O);
    circle(px, 12, 11, 3, SI, SIl, SId, O);
    lineThick(px, 7, 6, 11, 9, O, 1);
    lineThick(px, 9, 10, 5, 7, O, 1);
    return px;
  }
  function jailer() { // 牢番: 鉄格子と鍵
    const px = blank();
    for (let x = 4; x <= 12; x += 3) lineThick(px, x, 2, x, 13, ME, 1);
    circle(px, 2, 13, 2, GO, GOl, GOd, O);
    lineThick(px, 4, 13, 7, 13, GO, 1);
    return px;
  }
  function tradepost() { // 取引所: 屋台と天秤
    const px = blank();
    for (let r = 0; r < 3; r++) for (let c = -(r + 2); c <= r + 2; c++) set(px, 8 + c, 2 + r, (c + 20) % 2 ? RF : WL);
    frame(px, 3, 8, 10, 5, WD, O);
    return px;
  }
  function refine() { // 手直し: 砥石
    const px = blank();
    circle(px, 6, 9, 5, ST, STl, STd, O);
    circle(px, 6, 9, 1, STd, STd, STd, STd);
    lineThick(px, 10, 5, 14, 1, ME, 1);
    sparkleIcon(px, 11, 4);
    return px;
  }
  function sparkleIcon(px, x, y) { set(px, x, y - 1, GOl); set(px, x + 1, y, GOl); set(px, x - 1, y, GOl); }
  function mansion() { // 豪邸: 勝利点も
    const px = blank();
    roof(px, 2, 1, 12, 5, WTd, WTl, WT);
    frame(px, 3, 6, 10, 8, ST, O);
    rect(px, 5, 8, 2, 2, WT); rect(px, 9, 8, 2, 2, WT);
    rect(px, 7, 11, 2, 3, WDd);
    return px;
  }
  function aristocrat() { // 貴人: 勝利点も
    const px = blank();
    circle(px, 8, 5, 3, WL, O, O, O);
    rect(px, 5, 8, 6, 6, RF);
    diamond(px, 8, 12, 2, WT, O);
    return px;
  }
  function hideaway() { // 隠れ部屋
    const px = blank();
    frame(px, 1, 2, 6, 8, WD, O);
    frame(px, 5, 11, 8, 3, MEd, O);
    return px;
  }
  function hall() { // 広間: 勝利点も
    const px = blank();
    for (const x of [2, 7, 12]) { rect(px, x, 3, 2, 11, ST); }
    for (const x of [2, 7, 12]) set(px, x + 1, 2, GOl);
    return px;
  }
  function tinker() { // 鋳物師: 銅を打つ
    const px = blank();
    rect(px, 3, 10, 7, 3, MEd);
    circle(px, 11, 8, 3, CU, CUl, CUd, O);
    lineThick(px, 3, 5, 8, 9, WD, 1);
    return px;
  }
  function surveyor() { // 測量士
    const px = blank();
    lineThick(px, 8, 4, 4, 13, WDd, 1); lineThick(px, 8, 4, 12, 13, WDd, 1); lineThick(px, 8, 4, 8, 13, WDd, 1);
    circle(px, 8, 4, 2, ME, ME, MEd, O);
    return px;
  }
  function wrecker() { // 壊し屋（アタック）
    const px = blank();
    rect(px, 2, 3, 9, 9, ST);
    for (const [x, y] of [[4, 5], [7, 7], [9, 4], [5, 9]]) set(px, x, y, STd);
    lineThick(px, 11, 10, 14, 13, WDd, 1);
    rect(px, 13, 12, 2, 2, ME);
    return px;
  }
  function toll() { // 通行料: 関所
    const px = blank();
    lineThick(px, 2, 2, 2, 13, WDd, 1);
    lineThick(px, 3, 6, 13, 3, RF, 2);
    circle(px, 12, 10, 2, GO, GOl, GOd, O);
    return px;
  }
  // ---- 拡張「海辺」35 種 ----
  function cove() { // 隠し港: 入り江の小舟
    const px = blank();
    rect(px, 0, 10, 16, 5, WT);
    for (let x = 3; x < 13; x++) set(px, x, 10 - Math.round(2 * Math.sin((x - 3) / 10 * Math.PI)), WDd);
    return px;
  }
  function beacon() { // かがり火: 灯台
    const px = blank();
    frame(px, 6, 3, 4, 11, ST, O);
    circle(px, 8, 2, 3, FL, FLl, FL, O);
    return px;
  }
  function shorevillage() { // 浜の集落
    const px = blank();
    roof(px, 3, 6, 8, 4, RFd, RF, RFl); frame(px, 4, 10, 6, 4, WL, O);
    rect(px, 0, 13, 16, 2, WT);
    return px;
  }
  function fishtown() { // 漁師町: 舟と網
    const px = blank();
    rect(px, 2, 9, 9, 4, RF);
    lineThick(px, 11, 9, 11, 3, WDd, 1);
    lineThick(px, 11, 4, 14, 7, MEd, 1);
    return px;
  }
  function overlook() { // 見晴らし台
    const px = blank();
    frame(px, 1, 8, 8, 6, WD, O);
    rect(px, 0, 14, 16, 2, WT);
    circle(px, 11, 5, 2, WL, O, O, O);
    return px;
  }
  function contraband() { // 抜け荷: 木箱
    const px = blank();
    frame(px, 3, 7, 10, 7, WD, O);
    rect(px, 3, 10, 10, 1, WDd);
    return px;
  }
  function storeroom() { // 物置
    const px = blank();
    frame(px, 2, 6, 5, 8, WD, O); frame(px, 9, 8, 5, 6, WDl, O);
    return px;
  }
  function compass() { // 羅針盤
    const px = blank();
    circle(px, 8, 8, 6, GO, GOl, GOd, O);
    diamond(px, 8, 8, 4, O, O);
    return px;
  }
  function gibbon() { // 手長猿
    const px = blank();
    lineThick(px, 4, 13, 4, 3, WDd, 1);
    lineThick(px, 4, 13, 13, 9, WD, 2);
    circle(px, 12, 6, 2, WDd, WDd, WDd, O);
    return px;
  }
  function searoute() { // 航路図
    const px = blank();
    frame(px, 2, 2, 12, 12, WL, O);
    lineThick(px, 4, 4, 12, 12, RF, 1);
    return px;
  }
  function wagon() { // 荷馬車
    const px = blank();
    frame(px, 4, 4, 9, 6, WD, O);
    circle(px, 6, 12, 2, ME, ME, MEd, O);
    circle(px, 11, 12, 2, ME, ME, MEd, O);
    return px;
  }
  function snatcher() { // ひったくり
    const px = blank();
    lineThick(px, 3, 11, 9, 5, MEd, 1);
    circle(px, 11, 4, 2, GOl, GO, GOd, O);
    return px;
  }
  function islet() { // 小島
    const px = blank();
    rect(px, 0, 11, 16, 3, WT);
    circle(px, 8, 9, 4, GR, GRl, GR, O);
    lineThick(px, 8, 8, 8, 3, WDd, 1);
    return px;
  }
  function salvor() { // 引き上げ屋
    const px = blank();
    frame(px, 4, 9, 8, 5, WD, O);
    lineThick(px, 8, 3, 8, 9, ME, 1);
    return px;
  }
  function oldmap() { // 古地図
    const px = blank();
    frame(px, 2, 3, 12, 10, WL, O);
    lineThick(px, 4, 5, 12, 11, RF, 1);
    return px;
  }
  function barricade() { // 通せんぼ
    const px = blank();
    lineThick(px, 2, 2, 14, 14, MEd, 2);
    lineThick(px, 2, 14, 14, 2, MEd, 2);
    return px;
  }
  function deckhand() { // 水夫
    const px = blank();
    circle(px, 8, 8, 5, WD, WDl, WDd, O);
    circle(px, 8, 8, 2, WDd, WDd, WDd, O);
    return px;
  }
  function rockpool() { // 磯
    const px = blank();
    circle(px, 6, 9, 4, ST, STl, STd, O);
    circle(px, 6, 9, 3, WT, WTl, WTd, O);
    circle(px, 12, 11, 1, RF, RFl, RFd, O);
    return px;
  }
  function openmarket() { // 青空市
    const px = blank();
    for (let x = 2; x < 14; x += 3) rect(px, x, 2, 2, 4, (x / 3) % 2 ? RF : WL);
    frame(px, 2, 8, 12, 5, WD, O);
    return px;
  }
  function tradeship() { // 交易船
    const px = blank();
    rect(px, 2, 10, 12, 3, WDd);
    lineThick(px, 8, 10, 8, 2, WDd, 1);
    rect(px, 8, 3, 5, 6, WL);
    return px;
  }
  function fort() { // 出城
    const px = blank();
    frame(px, 3, 5, 10, 9, ST, O);
    for (let x = 3; x < 13; x += 3) rect(px, x, 3, 2, 2, STl);
    return px;
  }
  function strategist() { // 軍師
    const px = blank();
    frame(px, 2, 8, 12, 5, WD, O);
    circle(px, 6, 6, 1, RF, RFl, RFd, O); circle(px, 10, 6, 1, WT, WTl, WTd, O);
    return px;
  }
  function coffer() { // 金蔵
    const px = blank();
    frame(px, 3, 6, 10, 8, WD, O);
    rect(px, 3, 9, 10, 2, GOl);
    return px;
  }
  function pier() { // 波止場
    const px = blank();
    rect(px, 0, 8, 16, 3, WD);
    for (let x = 1; x < 16; x += 4) lineThick(px, x, 11, x, 15, WDd, 1);
    rect(px, 0, 13, 16, 2, WT);
    return px;
  }
  function privateer() { // 私掠船
    const px = blank();
    rect(px, 3, 10, 10, 3, MEd);
    lineThick(px, 8, 10, 8, 2, MEd, 1);
    rect(px, 8, 2, 4, 2, RF);
    return px;
  }
  function buccaneer() { // 海の荒くれ
    const px = blank();
    lineThick(px, 3, 12, 12, 4, ME, 2);
    circle(px, 13, 3, 2, WDd, WDd, WDd, O);
    return px;
  }
  function siren() { // 人魚の呪い
    const px = blank();
    circle(px, 8, 6, 3, WL, O, O, O);
    for (let r = 0; r < 6; r++) { const half = Math.max(1, 3 - r / 2); for (let c = -half; c < half; c++) set(px, 8 + c, 9 + r, WT); }
    return px;
  }
  function diver() { // 海女
    const px = blank();
    rect(px, 0, 4, 16, 12, WT);
    circle(px, 8, 8, 3, MEd, MEd, MEd, O);
    return px;
  }
  function injunction() { // 差し止め
    const px = blank();
    lineThick(px, 5, 3, 5, 13, WDd, 1);
    frame(px, 5, 4, 8, 6, WL, O);
    lineThick(px, 7, 6, 11, 6, RF, 1);
    return px;
  }
  function emissary() { // 特使
    const px = blank();
    frame(px, 4, 5, 8, 6, WL, O);
    circle(px, 8, 8, 2, RF, RFl, RFd, O);
    return px;
  }
  function pilot() { // 水先案内
    const px = blank();
    circle(px, 8, 8, 6, WD, WDl, WDd, O);
    for (let a = 0; a < 360; a += 60) { const r = a * Math.PI / 180; lineThick(px, 8, 8, 8 + Math.round(6 * Math.sin(r)), 8 - Math.round(6 * Math.cos(r)), WDd, 1); }
    return px;
  }
  function raidship() { // 略奪船
    const px = blank();
    rect(px, 1, 11, 7, 3, MEd);
    rect(px, 9, 12, 6, 2, MEd);
    lineThick(px, 5, 11, 12, 6, GO, 1);
    return px;
  }
  function crone() { // 磯の老婆
    const px = blank();
    circle(px, 8, 9, 4, MEd, MEd, MEd, O);
    circle(px, 12, 6, 2, GOl, GO, GOd, O);
    return px;
  }
  function pioneer() { // 開拓者
    const px = blank();
    lineThick(px, 5, 13, 5, 3, WDd, 1);
    frame(px, 9, 8, 6, 6, WD, O);
    return px;
  }
  function fogship() { // 霧の船
    const px = blank();
    rect(px, 3, 10, 10, 3, MEd);
    lineThick(px, 8, 10, 8, 3, MEd, 1);
    rect(px, 8, 4, 4, 5, WLd);
    return px;
  }
  // ---- 拡張「繁栄」36 種 ----
  function platinum() { return coin(WL, SI, STd, 3); }
  function colony() {
    const px = castle();
    set(px, 8, 0, GOl);
    return px;
  }
  function anvil() { // 打ち台
    const px = blank();
    rect(px, 3, 8, 10, 3, ME);
    rect(px, 6, 11, 4, 3, MEd);
    rect(px, 5, 14, 6, 1, MEd);
    circle(px, 11, 12, 1, GOl, GOl, GOl, O);
    return px;
  }
  function firetower() { // 火の見やぐら
    const px = blank();
    frame(px, 6, 3, 4, 11, WD, O);
    circle(px, 8, 2, 2, RF, RFl, RFd, O);
    return px;
  }
  function prelate() { // 高僧
    const px = blank();
    circle(px, 8, 4, 2, WL, O, O, O);
    rect(px, 5, 7, 6, 7, RF);
    return px;
  }
  function stele() { // 石碑
    const px = blank();
    frame(px, 5, 2, 6, 12, ST, O);
    diamond(px, 8, 6, 2, STl, STd);
    return px;
  }
  function stoneyard() { // 石工場
    const px = blank();
    rect(px, 2, 8, 5, 5, ST); rect(px, 9, 6, 5, 7, STl);
    return px;
  }
  function artisanrow() { // 職人町
    const px = blank();
    roof(px, 1, 6, 6, 3, RFd, RF, RFl); frame(px, 2, 9, 4, 4, WL, O);
    roof(px, 9, 5, 6, 3, WTd, WTl, WT); frame(px, 10, 8, 4, 5, ST, O);
    return px;
  }
  function scribe() { // 書役
    const px = blank();
    frame(px, 3, 7, 10, 5, WL, O);
    lineThick(px, 12, 2, 14, 6, ME, 1);
    return px;
  }
  function stake() { // 元手
    const px = blank();
    circle(px, 6, 10, 2, CU, CUl, CUd, O);
    circle(px, 10, 8, 2, SI, SIl, SId, O);
    lineThick(px, 12, 3, 12, 8, RF, 1);
    return px;
  }
  function diadem() { // 髪飾り
    const px = blank();
    rect(px, 4, 9, 8, 2, GO);
    rect(px, 4, 5, 2, 4, GOl); rect(px, 7, 4, 2, 5, GOl); rect(px, 10, 5, 2, 4, GOl);
    return px;
  }
  function castletown() { // 城下町
    const px = blank();
    frame(px, 3, 6, 10, 8, ST, O);
    for (let x = 3; x < 13; x += 3) rect(px, x, 4, 2, 2, STl);
    return px;
  }
  function coinery() { // 鋳貨所
    const px = blank();
    frame(px, 5, 2, 6, 9, ME, O);
    circle(px, 8, 12, 3, GOl, GO, GOd, O);
    return px;
  }
  function mob() { // 群衆
    const px = blank();
    for (const x of [2, 7, 12]) { rect(px, x, 8, 3, 6, MEd); circle(px, x + 1, 6, 2, MEd, MEd, MEd, O); }
    return px;
  }
  function safebox() { // 貸し金庫
    const px = blank();
    frame(px, 3, 3, 10, 10, ME, O);
    circle(px, 8, 8, 3, MEd, MEd, MEd, O);
    return px;
  }
  function charlatan() { // まやかし師
    const px = blank();
    circle(px, 6, 9, 3, FL, FLl, FL, O);
    circle(px, 10, 10, 2, FLl, FLl, FL, O);
    rect(px, 5, 11, 2, 2, WDd); rect(px, 9, 12, 2, 2, WDd);
    return px;
  }
  function curio() { // 蒐集箱
    const px = blank();
    frame(px, 2, 2, 12, 12, WD, O);
    circle(px, 6, 6, 1, GOl, GOl, GOl, O); circle(px, 10, 6, 1, RF, RF, RF, O);
    circle(px, 6, 10, 1, WT, WT, WT, O); circle(px, 10, 10, 1, WL, WL, WL, O);
    return px;
  }
  function orb() { // 占い玉
    const px = blank();
    circle(px, 8, 8, 6, WT, WTl, WTd, O);
    rect(px, 6, 14, 4, 1, WDd);
    return px;
  }
  function tycoon() { // 大旦那
    const px = blank();
    circle(px, 8, 9, 3, CU, CUl, CUd, O); circle(px, 8, 9, 2, GOl, GOl, GOl, O);
    circle(px, 8, 6, 1, WL, O, O, O);
    return px;
  }
  function warfund() { // 軍資金
    const px = blank();
    frame(px, 3, 8, 10, 6, WD, O);
    lineThick(px, 12, 2, 12, 8, ME, 1);
    return px;
  }
  function boulevard() { // 大通り
    const px = blank();
    roof(px, 1, 6, 6, 3, RFd, RF, RFl); frame(px, 2, 9, 4, 5, WL, O);
    roof(px, 9, 5, 6, 3, WTd, WTl, WT); frame(px, 10, 8, 4, 6, ST, O);
    return px;
  }
  function stash() { // へそくり
    const px = blank();
    rect(px, 2, 11, 12, 2, WDd);
    circle(px, 8, 9, 2, GOl, GO, GOd, O);
    return px;
  }
  function banker() { // 金融屋
    const px = blank();
    frame(px, 2, 3, 8, 6, WL, O);
    circle(px, 11, 11, 3, GOl, GO, GOd, O);
    return px;
  }
  function extension() { // 増築
    const px = blank();
    for (const x of [2, 8, 13]) lineThick(px, x, 2, x, 14, WD, 1);
    for (const y of [4, 8, 12]) lineThick(px, 2, y, 13, y, WDl, 1);
    return px;
  }
  function crucible() { // るつぼ
    const px = blank();
    circle(px, 8, 10, 5, MEd, MEd, MEd, O);
    circle(px, 8, 8, 3, FL, FLl, FL, O);
    return px;
  }
  function council() { // 御前会議
    const px = blank();
    circle(px, 8, 9, 5, WD, WDl, WDd, O);
    circle(px, 8, 3, 2, RF, RF, RF, O); circle(px, 3, 11, 2, WT, WT, WT, O); circle(px, 13, 11, 2, GOl, GOl, GOl, O);
    return px;
  }
  function hawker() { // 呼び売り
    const px = blank();
    frame(px, 3, 7, 10, 4, WD, O);
    circle(px, 5, 12, 2, ME, ME, MEd, O); circle(px, 11, 12, 2, ME, ME, MEd, O);
    return px;
  }
  function iou() { // 借用書
    const px = blank();
    frame(px, 3, 5, 10, 7, WL, O);
    circle(px, 8, 8, 2, RF, RFl, RFd, O);
    return px;
  }
  function traderoute() { // 通商路
    const px = blank();
    lineThick(px, 1, 12, 15, 5, WDd, 1);
    circle(px, 6, 9, 1, RF, RF, RF, O); circle(px, 10, 7, 1, ME, ME, MEd, O);
    return px;
  }
  function charm() { // お守り
    const px = blank();
    lineThick(px, 8, 2, 8, 7, WDd, 1);
    diamond(px, 8, 10, 3, FL, O);
    return px;
  }
  function tally() { // 勘定場
    const px = blank();
    for (let x = 3; x < 12; x += 2) lineThick(px, x, 3, x, 10, ME, 1);
    lineThick(px, 2, 8, 12, 4, ME, 1);
    return px;
  }
  function forbidden() { // ご禁制
    const px = blank();
    frame(px, 3, 7, 10, 6, WD, O);
    circle(px, 8, 6, 2, MEd, MEd, MEd, O);
    return px;
  }
  function quack() { // いかさま薬売り
    const px = blank();
    circle(px, 6, 9, 2, FL, FLl, FL, O); circle(px, 10, 9, 2, WT, WTl, WT, O);
    circle(px, 8, 4, 3, WL, O, O, O);
    return px;
  }
  function seal() { // 御印
    const px = blank();
    frame(px, 3, 3, 10, 10, WL, O);
    circle(px, 8, 8, 4, RF, RFl, RFd, O);
    return px;
  }
  function gamble() { // 山っ気
    const px = blank();
    frame(px, 3, 7, 5, 5, WL, O); frame(px, 9, 5, 5, 5, WL, O);
    return px;
  }
  function bouncer() { // 用心棒
    const px = blank();
    frame(px, 4, 2, 8, 12, WD, O);
    circle(px, 8, 8, 2, MEd, MEd, MEd, O);
    return px;
  }
  // ---- 拡張「異郷」35 種 ----
  function crossing() { // 辻
    const px = blank();
    lineThick(px, 8, 1, 8, 14, WDd, 1);
    rect(px, 8, 4, 5, 2, RF); rect(px, 3, 7, 5, 2, WT);
    return px;
  }
  function pyrite() { // にせ金
    const px = blank();
    circle(px, 8, 9, 5, MEd, MEd, MEd, O);
    circle(px, 6, 8, 1, GOl, GOl, GOl, O); circle(px, 10, 7, 1, GOl, GOl, GOl, O); circle(px, 8, 10, 1, GOl, GOl, GOl, O);
    return px;
  }
  function grading() { // 造成
    const px = blank();
    rect(px, 1, 11, 5, 4, WD); rect(px, 6, 8, 5, 7, WDl); rect(px, 11, 5, 4, 10, WDd);
    return px;
  }
  function spring() { // 泉のほとり
    const px = blank();
    circle(px, 8, 9, 5, ST, STl, STd, O);
    circle(px, 8, 9, 3, WT, WTl, WTd, O);
    return px;
  }
  function groundwork() { // 根回し
    const px = blank();
    for (const x of [2, 7, 12]) rect(px, x, 9, 3, 5, ST);
    frame(px, 2, 2, 8, 5, WL, O);
    return px;
  }
  function underpass() { // 地下道
    const px = blank();
    rect(px, 1, 6, 14, 3, ST);
    for (let r = 0; r < 6; r++) { const half = 5 - r; for (let c = -half; c < half; c++) set(px, 8 + c, 15 - r, O); }
    return px;
  }
  function watchdog() { // 見張り犬
    const px = blank();
    rect(px, 5, 9, 6, 4, WD);
    circle(px, 11, 7, 2, WD, WDl, WDd, O);
    return px;
  }
  function handyman() { // 何でも屋
    const px = blank();
    lineThick(px, 11, 2, 11, 14, WD, 1);
    for (let y = 3; y < 14; y += 3) line_(px, y);
    circle(px, 4, 12, 2, SI, SIl, SId, O);
    return px;
  }
  function line_(px, y) { for (let x = 9; x <= 13; x++) set(px, x, y, WDd); }
  function spicer() { // 香料売り
    const px = blank();
    circle(px, 4, 9, 3, RF, RFl, RFd, O);
    circle(px, 8, 10, 3, GO, GOl, GOd, O);
    circle(px, 12, 9, 3, FL, FLl, FL, O);
    return px;
  }
  function silverdealer() { // 銀の商人
    const px = blank();
    frame(px, 3, 6, 10, 6, SI, O);
    return px;
  }
  function drifter() { // 流れ者
    const px = blank();
    lineThick(px, 5, 13, 5, 3, WDd, 1);
    circle(px, 5, 2, 2, WD, WDl, WDd, O);
    return px;
  }
  function pathway() { // けもの道
    const px = blank();
    for (const [x, y] of [[2, 12], [5, 9], [8, 6], [11, 3]]) { circle(px, x, y, 1, WDd, WDd, WDd, O); circle(px, x + 2, y + 1, 1, WDd, WDd, WDd, O); }
    return px;
  }
  function loom() { // 機織り
    const px = blank();
    frame(px, 2, 2, 12, 12, WD, O);
    for (let y = 4; y < 14; y += 2) lineThick(px, 3, y, 13, y, y % 4 ? RF : WT, 1);
    return px;
  }
  function mapmaker() { // 測地師
    const px = blank();
    frame(px, 2, 4, 9, 8, WL, O);
    circle(px, 12, 5, 3, GOl, GO, GOd, O);
    return px;
  }
  function bargainer() { // 値切り上手
    const px = blank();
    circle(px, 4, 6, 2, CU, CUl, CUd, O);
    circle(px, 12, 10, 2, SI, SIl, SId, O);
    lineThick(px, 6, 7, 10, 9, O, 1);
    return px;
  }
  function causeway() { // 石畳
    const px = blank();
    rect(px, 0, 9, 16, 3, WT);
    for (let x = 0; x < 16; x += 4) rect(px, x, 7, 3, 3, ST);
    return px;
  }
  function hatago() { // 旅籠
    const px = blank();
    roof(px, 3, 3, 10, 5, RFd, RF, RFl); frame(px, 4, 8, 8, 6, WL, O);
    rect(px, 1, 10, 2, 3, RF);
    return px;
  }
  function warden() { // 国守
    const px = blank();
    frame(px, 2, 4, 12, 9, ST, O);
    rect(px, 7, 8, 2, 5, MEd);
    return px;
  }
  function stable() { // 馬小屋
    const px = blank();
    roof(px, 2, 3, 10, 4, WDd, WD, WDl); frame(px, 3, 7, 8, 6, WL, O);
    circle(px, 12, 12, 2, ME, ME, MEd, O);
    return px;
  }
  function brute() { // 暴れ者
    const px = blank();
    circle(px, 6, 5, 2, WL, O, O, O);
    lineThick(px, 9, 8, 13, 13, WDd, 2);
    return px;
  }
  function stewpot() { // 煮え鍋
    const px = blank();
    circle(px, 8, 10, 5, MEd, MEd, MEd, O);
    circle(px, 8, 7, 3, GO, GOl, GOd, O);
    circle(px, 8, 13, 1, FL, FLl, FL, O);
    return px;
  }
  function fleamarket() { // のみの市
    const px = blank();
    frame(px, 2, 8, 12, 5, WD, O);
    circle(px, 5, 6, 2, RF, RFl, RFd, O); circle(px, 9, 5, 2, ME, ME, MEd, O); circle(px, 12, 7, 2, GOl, GOl, GOl, O);
    return px;
  }
  function wheeler() { // 車輪職人
    const px = blank();
    circle(px, 8, 8, 6, WD, WDl, WDd, O);
    circle(px, 8, 8, 2, WDd, WDd, WDd, O);
    return px;
  }
  function charmhut() { // まじない小屋
    const px = blank();
    roof(px, 3, 5, 8, 4, WDd, WD, WDl); frame(px, 4, 9, 6, 5, WL, O);
    circle(px, 12, 4, 1, FL, FLl, FL, O);
    return px;
  }
  function gatevillage() { // 関所の村
    const px = blank();
    frame(px, 5, 3, 6, 11, ST, O);
    rect(px, 6, 8, 4, 6, MEd);
    return px;
  }
  function fields() { // 田畑
    const px = blank();
    for (let y = 4; y < 14; y += 3) for (let x = 1; x < 15; x += 3) set(px, x, y, GR);
    rect(px, 0, 13, 16, 2, WD);
    return px;
  }
  function lady() { // 奥方
    const px = blank();
    circle(px, 8, 5, 3, WL, O, O, O);
    rect(px, 5, 8, 6, 7, RF);
    circle(px, 8, 3, 1, GOl, GOl, GOl, O);
    return px;
  }
  function omen() { // お告げ
    const px = blank();
    roof(px, 3, 3, 10, 6, MEd, ME, MEd); frame(px, 4, 9, 8, 5, WL, O);
    circle(px, 8, 11, 2, WT, WTl, WTd, O);
    return px;
  }
  function outlaw() { // 無法者
    const px = blank();
    circle(px, 8, 6, 3, MEd, MEd, MEd, O);
    lineThick(px, 10, 9, 14, 13, ME, 1);
    return px;
  }
  function tent() { // 天幕
    const px = blank();
    for (let r = 0; r < 8; r++) { const half = Math.max(1, Math.round((r + 1) / 8 * 6)); for (let c = -half; c < half; c++) set(px, 8 + c, 12 - r, WL); }
    rect(px, 5, 12, 6, 2, WDd);
    return px;
  }
  function silkway() { // 絹の道
    const px = blank();
    for (const x of [2, 7, 12]) { rect(px, x, 8, 3, 4, WD); circle(px, x + 1, 6, 2, WDl, WDl, WDd, O); }
    return px;
  }
  function hiddengold() { // 隠し金
    const px = blank();
    circle(px, 8, 10, 4, WDd, WDd, WDd, O);
    circle(px, 8, 10, 2, GOl, GO, GOd, O);
    return px;
  }
  function legation() { // 公館
    const px = blank();
    roof(px, 3, 3, 10, 4, WTd, WTl, WT); frame(px, 4, 7, 8, 7, ST, O);
    rect(px, 2, 2, 2, 5, RF); rect(px, 12, 2, 2, 5, MEd);
    return px;
  }
  function dirtymoney() { // 悪銭
    const px = blank();
    circle(px, 8, 9, 3, CU, CUl, CUd, O);
    for (const [x, y] of [[3, 3], [12, 4], [4, 13], [13, 12]]) set(px, x, y, O);
    return px;
  }
  function magistrate() { // 代官
    const px = blank();
    frame(px, 2, 9, 12, 4, WD, O);
    lineThick(px, 8, 2, 8, 9, WDd, 2);
    circle(px, 8, 2, 2, WDd, WDd, WDd, O);
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
    abbey, crier, attendant, pawnbroker, official, meadow, hunter, command, highwayman,
    assembly, fair, alembic, archive, sentinel, sorcerer, craftsman, curse, explorer,
    bursar, banquet, scout, pickpocket, woodsman,
    backyard, prowler, errand, carnival, slum, butler, conman, fountain, landlord,
    suspension, plotter, envoy, foundry, watermill, minetown, tunnel, chamberlain,
    marquis, henchman, nightwatch, swap, jailer, tradepost, refine, mansion,
    aristocrat, hideaway, hall, tinker, surveyor, wrecker, toll,
    cove, beacon, shorevillage, fishtown, overlook, contraband, storeroom, compass,
    gibbon, searoute, wagon, snatcher, islet, salvor, oldmap, barricade, deckhand,
    rockpool, openmarket, tradeship, fort, strategist, coffer, pier, privateer,
    buccaneer, siren, diver, injunction, emissary, pilot, raidship, crone, pioneer, fogship,
    platinum, colony, firetower, anvil, prelate, stele, stoneyard, artisanrow, scribe,
    stake, diadem, castletown, coinery, mob, safebox, charlatan, curio, orb, tycoon,
    warfund, boulevard, stash, banker, extension, crucible, council, hawker, iou,
    traderoute, charm, tally, forbidden, quack, seal, gamble, bouncer,
    crossing, pyrite, grading, spring, groundwork, underpass, watchdog, handyman,
    spicer, silverdealer, drifter, pathway, loom, mapmaker, bargainer, causeway,
    hatago, warden, stable, brute, stewpot, fleamarket, wheeler, charmhut,
    gatevillage, fields, lady, omen, outlaw, tent, silkway, hiddengold, legation,
    dirtymoney, magistrate,
  };

  // 種類ごとの枠の色（ドット絵テーマでカードのふちに使う）
  const FRAME = {
    treasure: '#e8b83a',
    victory: '#4a8a5c',
    action: '#3a5cc8',
    'action-attack': '#c8503c',
    'action-reaction': '#3a9c9c',
    curse: '#8a4ab8',
    'treasure-victory': '#b8a030',
    'action-victory': '#5a8a3a',
    duration: '#d0762a',
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
