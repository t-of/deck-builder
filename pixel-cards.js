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
    '#8a5ab0', '#b892d8', '#5a3878', // 30-32 紫：地・明・影（夜行・恵み・呪詛）
    '#d8d0c0', '#8a8278',            // 33-34 骨・生成り：地・影
  ];
  const [O, CU, CUl, CUd, SI, SIl, SId, GO, GOl, GOd, WD, WDl, WDd, RF, RFl, RFd, WL, WLd, ST, STl, STd, WT, WTl, WTd, ME, MEd, FL, FLl, GR, GRl, PU, PUl, PUd, BN, BNd] = PALETTE.map((_, i) => i);

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


  function candleIcon(px, x, y) { // 小さなろうそく（アイコン内の飾り用）
    rect(px, x, y - 4, 2, 4, WL);
    set(px, x, y - 6, FL);
    return px;
  }

  // ---- 拡張「収穫祭＆ギルド」追加分 (45) ----
  function coronet() { // 宝の冠
    const px = blank();
    frame(px, 3, 9, 10, 4, RF, O);
    for (const x of [4, 8, 11]) { rect(px, x, 5, 2, 5, GO); circle(px, x + 1, 4, 1, GOl, GOl, GOl, O); }
    return px;
  }
  function courser() { // 駿足の馬
    const px = blank();
    rect(px, 2, 8, 9, 5, WD);
    rect(px, 9, 5, 4, 5, WDd);
    for (const x of [3, 6, 9]) lineThick(px, x, 13, x - 1, 15, WDd, 1);
    return px;
  }
  function demesne() { // 直轄地
    const px = blank();
    roof(px, 3, 3, 10, 4, RFd, RF, RFl); frame(px, 4, 7, 8, 7, WL, O);
    circle(px, 3, 13, 2, GO, GOl, GOd, O);
    return px;
  }
  function guardsman() { // 近衛兵
    const px = blank();
    rect(px, 2, 3, 3, 11, ST); rect(px, 11, 3, 3, 11, ST);
    lineThick(px, 8, 2, 8, 12, ME, 1);
    circle(px, 8, 4, 2, WDl, WDl, WDd, O);
    return px;
  }
  function turnip() { // 大かぶ
    const px = blank();
    circle(px, 8, 10, 5, WL, WL, WLd, O);
    circle(px, 8, 7, 3, RF, RFl, RFd, O);
    lineThick(px, 8, 4, 8, 1, GR, 1);
    return px;
  }
  function renown() { // 誉れ
    const px = blank();
    circle(px, 8, 5, 3, GO, GOl, GOd, O);
    for (const x of [4, 12]) lineThick(px, x, 6, x, 14, WDd, 1);
    return px;
  }
  function smallvillage() { // 里
    const px = blank();
    roof(px, 0, 7, 6, 3, RF, RFl, RFd); frame(px, 1, 10, 4, 4, WL, O);
    roof(px, 6, 4, 6, 4, WTd, WTl, WT); frame(px, 7, 8, 4, 6, ST, O);
    roof(px, 11, 8, 5, 3, RFd, RF, RFl); frame(px, 12, 11, 3, 3, WL, O);
    return px;
  }
  function chandler() { // ろうそく屋
    const px = blank();
    frame(px, 2, 11, 12, 2, WD, O);
    for (const x of [4, 8, 12]) { rect(px, x, 6, 2, 5, WL); set(px, x, 4, FL); }
    return px;
  }
  function mason() { // 石切り
    const px = blank();
    frame(px, 6, 6, 9, 8, ST, O);
    rect(px, 8, 8, 2, 2, STd); rect(px, 11, 10, 2, 2, STd);
    lineThick(px, 2, 12, 6, 7, WD, 2);
    return px;
  }
  function shoer() { // 蹄鉄屋
    const px = blank();
    circle(px, 8, 8, 5, ME, ME, MEd, O);
    circle(px, 8, 8, 2, T, T, T, O);
    rect(px, 6, 13, 4, 2, WDd);
    return px;
  }
  function sideshow() { // 見世物小屋
    const px = blank();
    frame(px, 2, 4, 12, 10, RF, O);
    for (let x = 3; x < 14; x += 3) rect(px, x, 4, 2, 10, WL);
    circle(px, 8, 8, 2, WL, WL, WL, O);
    return px;
  }
  function clinic() { // 養生所
    const px = blank();
    rect(px, 3, 9, 3, 5, WT); circle(px, 4, 8, 2, WTl, WTl, WTl, O);
    rect(px, 9, 10, 3, 4, CU); circle(px, 10, 9, 2, CUl, CUl, CUl, O);
    return px;
  }
  function notions() { // 小間物屋
    const px = blank();
    frame(px, 2, 9, 5, 5, RF, O); frame(px, 9, 9, 5, 5, WT, O);
    circle(px, 8, 4, 2, GO, GOl, GOd, O);
    return px;
  }
  function redo() { // 作り直し
    const px = blank();
    rect(px, 3, 10, 5, 3, MEd);
    for (let r = 0; r < 3; r++) rect(px, 2 - r, 9 + r, 9 + r * 2, 1, ME);
    lineThick(px, 11, 4, 11, 9, WDd, 1);
    circle(px, 11, 3, 2, GOl, GOl, GOd, O);
    return px;
  }
  function apprentice() { // 見習い魔女
    const px = blank();
    lineThick(px, 5, 14, 5, 6, FL, 2);
    circle(px, 5, 4, 2, T, T, T, O);
    for (let i = 0; i < 4; i++) set(px, 9 + i, 10 - i, FL);
    return px;
  }
  function counselor() { // 相談役
    const px = blank();
    frame(px, 2, 10, 12, 4, WD, O);
    frame(px, 5, 3, 6, 6, WL, O);
    return px;
  }
  function forerunner() { // 先駆け
    const px = blank();
    lineThick(px, 3, 13, 12, 4, WDl, 1);
    for (const [x, y] of [[4, 13], [7, 12], [10, 13]]) set(px, x, y, WDd);
    return px;
  }
  function square() { // 市の広場
    const px = blank();
    for (const x of [2, 7, 11]) rect(px, x, 8, 3, 1, ME);
    rect(px, 2, 9, 12, 5, ST);
    return px;
  }
  function farmhand() { // 作男
    const px = blank();
    lineThick(px, 5, 14, 11, 2, WDd, 2);
    circle(px, 11, 1, 2, RFl, RFl, RFl, O);
    return px;
  }
  function expo() { // 博覧会
    const px = blank();
    frame(px, 2, 4, 5, 8, WD, O); frame(px, 9, 4, 5, 8, WD, O);
    circle(px, 4, 8, 1, GO, GO, GO, O);
    rect(px, 10, 7, 2, 3, WTl);
    return px;
  }
  function cornhorn() { // 実りの角
    const px = blank();
    for (let r = 0; r < 10; r++) { const half = Math.max(1, Math.round(r * 0.45)); for (let c = -half; c <= half; c++) set(px, 5 + r + c / 2, 13 - r, GO); }
    circle(px, 12, 5, 1, RF, RF, RF, O); circle(px, 10, 3, 1, GR, GR, GR, O);
    return px;
  }
  function huntparty() { // 猟の一行
    const px = blank();
    for (const x of [3, 7, 11]) { rect(px, x, 8, 2, 6, ME); circle(px, x + 1, 6, 2, WDl, WDl, WDd, O); }
    return px;
  }
  function clown() { // ひょうきん者
    const px = blank();
    circle(px, 8, 9, 5, WL, WL, WL, O);
    set(px, 5, 7, O); set(px, 11, 7, O);
    circle(px, 8, 3, 2, RF, RFl, RFd, O);
    return px;
  }
  function breadmaker() { // パン焼き
    const px = blank();
    for (const x of [4, 8, 12]) circle(px, x, 10, 2, GOl, GOl, GO, O);
    frame(px, 2, 12, 12, 2, WDd, O);
    return px;
  }
  function meatseller() { // 肉売り
    const px = blank();
    rect(px, 7, 2, 2, 8, WDd);
    for (const x of [5, 8, 11]) rect(px, x, 3, 2, 5, CUd);
    return px;
  }
  function wanderer() { // 渡り職人
    const px = blank();
    lineThick(px, 3, 13, 12, 4, WDl, 1);
    frame(px, 2, 9, 5, 4, WD, O);
    return px;
  }
  function guildhall() { // 商工会
    const px = blank();
    roof(px, 1, 2, 14, 4, WTd, WTl, WT); frame(px, 2, 6, 12, 8, ST, O);
    rect(px, 4, 8, 2, 2, WT); rect(px, 10, 8, 2, 2, WT);
    lineThick(px, 8, 2, 8, 0, WDd, 1);
    return px;
  }
  function stargazer() { // 星読み
    const px = blank();
    circle(px, 8, 10, 4, MEd, MEd, MEd, O);
    for (const [x, y] of [[3, 3], [12, 4], [8, 2], [5, 6]]) set(px, x, y, GOl);
    return px;
  }
  function funfair() { // お祭り
    const px = blank();
    for (const x of [2, 7, 12]) { rect(px, x, 8, 3, 6, RF); circle(px, x + 1, 6, 2, GOl, GO, GOd, O); }
    return px;
  }
  function ferry() { // 渡し舟
    const px = blank();
    for (let y = 10; y < 14; y++) for (let x = 0; x < 16; x++) set(px, x, y, (x + y) % 4 < 2 ? WT : WTl);
    rect(px, 4, 6, 8, 4, WD);
    lineThick(px, 8, 1, 8, 6, WDd, 1);
    return px;
  }
  function mugger() { // 辻強盗
    const px = blank();
    rect(px, 0, 4, 5, 11, O); rect(px, 11, 4, 5, 11, O);
    circle(px, 8, 10, 2, MEd, MEd, MEd, O);
    return px;
  }
  function duel() { // 果たし合い
    const px = blank();
    lineThick(px, 2, 13, 13, 3, ME, 2);
    lineThick(px, 2, 3, 13, 13, MEd, 2);
    return px;
  }
  function goldbag() { // 金の袋
    const px = blank();
    circle(px, 8, 10, 5, GOd, GOd, GOd, O);
    circle(px, 8, 6, 2, GOd, GOd, GOd, O);
    circle(px, 8, 10, 2, GOl, GO, GOd, O);
    return px;
  }
  function crown() { // 金の冠
    const px = blank();
    frame(px, 3, 10, 10, 4, RF, O);
    for (const x of [4, 8, 11]) { rect(px, x, 4, 2, 6, GO); circle(px, x + 1, 3, 1, GOl, GOl, GOl, O); }
    return px;
  }
  function retinue() { // 取り巻き
    const px = blank();
    for (const x of [2, 7, 11]) { rect(px, x, 8, 3, 6, MEd); circle(px, x + 1, 6, 2, WDl, WDl, WDd, O); }
    return px;
  }
  function hime() { // 姫君
    const px = blank();
    circle(px, 8, 10, 4, RF, RFl, RFd, O);
    circle(px, 8, 5, 3, WDl, WDl, WDd, O);
    circle(px, 8, 2, 1, GOl, GOl, GOl, O);
    return px;
  }
  function steed() { // 愛馬
    const px = blank();
    rect(px, 2, 8, 9, 5, WD);
    rect(px, 9, 5, 4, 5, WDd);
    circle(px, 13, 5, 1, WL, WL, WL, O);
    return px;
  }
  function diviner() { // 易者
    const px = blank();
    circle(px, 8, 9, 4, FL, FLl, FL, O);
    circle(px, 8, 4, 2, MEd, MEd, MEd, O);
    return px;
  }
  function healer() { // 町医者
    const px = blank();
    rect(px, 3, 9, 3, 5, WT); circle(px, 4, 8, 2, WTl, WTl, WTl, O);
    frame(px, 8, 10, 6, 4, WD, O);
    return px;
  }
  function gem() { // 逸品
    const px = blank();
    diamond(px, 8, 8, 5, WT, O);
    diamond(px, 8, 8, 2, WTl, O);
    return px;
  }
  function countryside() { // 田舎村
    const px = blank();
    rect(px, 0, 10, 16, 6, GR);
    for (const [x, y] of [[2, 8], [6, 9], [9, 7], [12, 9]]) circle(px, x, y, 1, RF, RFl, RFd, RFd);
    return px;
  }
  function horsedealer() { // 馬喰
    const px = blank();
    rect(px, 2, 8, 9, 5, WD);
    circle(px, 13, 10, 2, GO, GOl, GOd, O);
    return px;
  }
  function tourney() { // 武芸大会
    const px = blank();
    lineThick(px, 3, 13, 3, 2, WDd, 1); lineThick(px, 13, 13, 13, 2, WDd, 1);
    for (const x of [3, 13]) rect(px, x - 2, 1, 4, 3, RF);
    lineThick(px, 4, 8, 12, 8, ME, 1);
    return px;
  }
  function collector() { // 取り立て屋
    const px = blank();
    frame(px, 2, 10, 12, 4, WD, O);
    circle(px, 5, 7, 2, CU, CUl, CUd, O);
    circle(px, 8, 6, 2, SI, SIl, SId, O);
    circle(px, 11, 7, 2, GO, GOl, GOd, O);
    return px;
  }
  function reaping() { // 取り入れ
    const px = blank();
    for (let x = 2; x < 14; x += 3) lineThick(px, x, 13, x, 7, GO, 1);
    return px;
  }

  // ---- 拡張「錬金術」追加分 (13) ----
  function potion() { // 霊薬
    const px = blank();
    lineThick(px, 8, 2, 8, 6, WT, 1);
    circle(px, 8, 10, 4, FL, FLl, FL, O);
    return px;
  }
  function transform() { // 転化
    const px = blank();
    diamond(px, 8, 8, 6, MEd, O);
    diamond(px, 8, 8, 3, FL, O);
    return px;
  }
  function vinerack() { // ぶどう棚
    const px = blank();
    lineThick(px, 1, 4, 15, 4, WDd, 1);
    for (let x = 2; x < 15; x += 3) { lineThick(px, x, 14, x, 4, WDd, 1); circle(px, x, 8, 1, FL, FL, FL, O); }
    return px;
  }
  function herbpicker() { // 草摘み
    const px = blank();
    rect(px, 0, 11, 16, 5, GR);
    for (const [x, y] of [[3, 9], [7, 8], [10, 10], [13, 9]]) circle(px, x, y, 1, FLl, FLl, FLl, FLl);
    return px;
  }
  function druggist() { // 調薬師
    const px = blank();
    for (const [x, c] of [[3, WT], [7, FL], [11, GO]]) { rect(px, x, 8, 3, 6, c); circle(px, x + 1, 6, 2, WTl, WTl, WTd, O); }
    return px;
  }
  function mirrorpool() { // のぞき水鏡
    const px = blank();
    circle(px, 8, 8, 6, ST, STl, STd, O);
    circle(px, 8, 8, 4, WT, WTl, WTd, O);
    return px;
  }
  function academy() { // 学び舎
    const px = blank();
    roof(px, 2, 2, 12, 5, MEd, ME, MEd); frame(px, 3, 7, 10, 7, WL, O);
    rect(px, 5, 9, 2, 2, WT); rect(px, 9, 9, 2, 2, WT);
    return px;
  }
  function adept() { // 術士
    const px = blank();
    circle(px, 8, 10, 3, MEd, MEd, MEd, O);
    for (let i = 0; i < 5; i++) set(px, 8 + Math.round(Math.sin(i) * 3), 6 - i, FL);
    return px;
  }
  function blackcat() { // 使い猫
    const px = blank();
    circle(px, 8, 10, 4, O, O, O, O);
    circle(px, 8, 4, 3, O, O, O, O);
    set(px, 6, 3, GOl); set(px, 10, 3, GOl);
    return px;
  }
  function arcanestone() { // 秘石
    const px = blank();
    diamond(px, 8, 8, 6, WT, O);
    diamond(px, 8, 8, 3, WTl, O);
    return px;
  }
  function clayman() { // 土人形
    const px = blank();
    rect(px, 5, 3, 6, 7, CUd);
    rect(px, 4, 10, 8, 4, CU);
    circle(px, 8, 2, 2, CU, CU, CUd, O);
    return px;
  }
  function pupil() { // 内弟子
    const px = blank();
    frame(px, 2, 10, 12, 4, WD, O);
    for (const [x, c] of [[4, RF], [9, WT]]) rect(px, x, 4, 3, 5, c);
    return px;
  }
  function takeover() { // 乗っ取り
    const px = blank();
    frame(px, 2, 7, 5, 7, RF, O);
    frame(px, 9, 5, 5, 9, MEd, O);
    return px;
  }

  // ---- 拡張「暗黒時代」追加分 (47) ----
  function ruins() { // がれき
    const px = blank();
    for (const [x, y, w, h] of [[1, 9, 5, 5], [6, 7, 5, 6], [11, 9, 4, 5]]) { frame(px, x, y, w, h, ST, O); }
    return px;
  }
  function ruin_mine() { // 崩れた坑
    const px = blank();
    for (let r = 0; r < 8; r++) { const half = Math.max(1, 6 - r); for (let c = -half; c <= half; c++) set(px, 8 + c, 13 - r, r < 3 ? MEd : O); }
    return px;
  }
  function ruin_library() { // 焼けた書庫
    const px = blank();
    for (const x of [2, 7, 11]) rect(px, x, 8, 4, 6, WDd);
    for (let i = 0; i < 4; i++) set(px, 12 + i, 3 - i, FL);
    return px;
  }
  function ruin_market() { // さびれた市
    const px = blank();
    rect(px, 2, 6, 12, 2, STd);
    for (const x of [3, 8, 12]) lineThick(px, x, 8, x, 13, STd, 1);
    return px;
  }
  function ruin_village() { // 捨てられた村
    const px = blank();
    frame(px, 2, 8, 5, 6, STd, O); frame(px, 9, 7, 5, 7, STd, O);
    return px;
  }
  function ruin_survivors() { // 生き残り
    const px = blank();
    for (const x of [3, 8, 12]) { circle(px, x, 10, 2, WDl, WDl, WDd, O); rect(px, x - 1, 12, 2, 3, WDd); }
    return px;
  }
  function shack() { // 掘っ立て小屋
    const px = blank();
    roof(px, 3, 5, 10, 4, WDd, WD, WDd); frame(px, 4, 9, 8, 6, WDd, O);
    return px;
  }
  function tombs() { // 墓所
    const px = blank();
    for (const x of [2, 7, 11]) { rect(px, x, 8, 3, 6, ST); set(px, x + 1, 7, STl); }
    return px;
  }
  function wildestate() { // 荒れた小屋
    const px = blank();
    frame(px, 3, 7, 10, 7, WDd, O);
    for (const [x, y] of [[2, 6], [12, 5], [4, 13]]) circle(px, x, y, 1, GR, GR, GR, GR);
    return px;
  }
  function booty() { // ぶんどり品
    const px = blank();
    frame(px, 3, 8, 10, 6, WDd, O);
    rect(px, 3, 10, 10, 2, GO);
    return px;
  }
  function lunatic() { // 乱心者
    const px = blank();
    circle(px, 8, 10, 4, MEd, MEd, MEd, O);
    for (const [x, y] of [[3, 3], [13, 4], [6, 2]]) set(px, x, y, RF);
    return px;
  }
  function sellsword() { // 雇われ剣士
    const px = blank();
    lineThick(px, 5, 2, 5, 12, ME, 2);
    circle(px, 5, 13, 2, MEd, MEd, MEd, O);
    circle(px, 11, 6, 3, ST, STl, STd, O);
    return px;
  }
  function knights() { // 遍歴騎士
    const px = blank();
    rect(px, 2, 8, 9, 5, WD);
    circle(px, 11, 5, 3, ME, ME, MEd, O);
    rect(px, 9, 5, 5, 2, MEd);
    return px;
  }
  function poorhouse() { // 貧乏長屋
    const px = blank();
    for (const x of [1, 6, 11]) frame(px, x, 8, 4, 6, WDd, O);
    return px;
  }
  function pauper() { // 文なし
    const px = blank();
    circle(px, 8, 10, 4, CU, CUl, CUd, O);
    circle(px, 8, 10, 2, CUd, CUd, CUd, O);
    return px;
  }
  function footman() { // 若党
    const px = blank();
    lineThick(px, 8, 2, 8, 12, WDd, 1);
    rect(px, 6, 1, 4, 3, ME);
    rect(px, 6, 13, 4, 2, WDd);
    return px;
  }
  function rover() { // 風来坊
    const px = blank();
    frame(px, 2, 9, 9, 5, WD, O);
    lineThick(px, 11, 2, 11, 9, WDd, 1);
    return px;
  }
  function gleaner() { // くず拾い
    const px = blank();
    for (let x = 2; x < 14; x += 3) lineThick(px, x, 13, x, 8, GOd, 1);
    return px;
  }
  function recluse() { // 世捨て人
    const px = blank();
    frame(px, 2, 2, 12, 12, ST, O);
    candleIcon(px, 5, 12);
    return px;
  }
  function marketsquare() { // 広小路
    const px = blank();
    rect(px, 2, 6, 12, 2, WD);
    for (const x of [3, 8, 12]) lineThick(px, x, 8, x, 13, WDd, 1);
    circle(px, 8, 3, 2, GO, GOl, GOd, O);
    return px;
  }
  function scholar() { // 物知り
    const px = blank();
    frame(px, 2, 9, 5, 6, RF, O); frame(px, 9, 9, 5, 6, WT, O);
    candleIcon(px, 13, 8);
    return px;
  }
  function lumberroom() { // がらくた部屋
    const px = blank();
    rect(px, 2, 3, 5, 4, WDd); rect(px, 9, 5, 5, 4, MEd); rect(px, 4, 9, 6, 4, RF);
    return px;
  }
  function waif() { // 宿なし子
    const px = blank();
    rect(px, 0, 4, 5, 11, O); rect(px, 11, 4, 5, 11, O);
    circle(px, 8, 11, 3, WDd, WDd, WDd, O);
    return px;
  }
  function arsenal() { // 武具蔵
    const px = blank();
    for (const x of [3, 8, 12]) lineThick(px, x, 2, x, 8, ME, 1);
    rect(px, 3, 10, 10, 4, WDd);
    return px;
  }
  function corpsecart() { // 屍車
    const px = blank();
    frame(px, 3, 6, 10, 5, WDd, O);
    circle(px, 5, 13, 2, MEd, MEd, MEd, O);
    circle(px, 11, 13, 2, MEd, MEd, MEd, O);
    return px;
  }
  function fief() { // 知行地
    const px = blank();
    roof(px, 3, 3, 10, 4, RFd, RF, RFl); frame(px, 4, 7, 8, 7, WL, O);
    circle(px, 12, 13, 2, SI, SIl, SId, O);
    return px;
  }
  function stronghold() { // 城郭
    const px = blank();
    rect(px, 1, 6, 4, 9, ST); rect(px, 11, 6, 4, 9, ST);
    frame(px, 3, 4, 10, 11, STl, O);
    return px;
  }
  function hardware() { // 金物売り
    const px = blank();
    frame(px, 2, 10, 12, 4, WD, O);
    for (const [x, c] of [[4, ME], [8, RF], [12, GO]]) rect(px, x, 4, 2, 6, c);
    return px;
  }
  function ravager() { // 荒らし
    const px = blank();
    for (let i = 0; i < 8; i++) { const half = Math.max(1, 6 - i); for (let c = -half; c <= half; c++) set(px, 5 + c, 14 - i, FL); }
    return px;
  }
  function parade() { // 練り歩き
    const px = blank();
    for (const x of [2, 6, 10]) { rect(px, x, 8, 2, 6, MEd); circle(px, x + 1, 6, 2, WDl, WDl, WDd, O); }
    return px;
  }
  function rats() { // どぶネズミ
    const px = blank();
    for (const [x, y] of [[4, 11], [9, 9], [12, 12]]) { circle(px, x, y, 2, WDd, WDd, WDd, O); }
    return px;
  }
  function scrounger() { // あさり屋
    const px = blank();
    for (const [x, y, c] of [[3, 10, ST], [7, 11, WDd], [11, 9, MEd]]) rect(px, x, y, 3, 3, c);
    return px;
  }
  function troubadour() { // 旅芸人
    const px = blank();
    lineThick(px, 5, 3, 5, 12, WDd, 1);
    circle(px, 9, 5, 4, WTl, WTl, WTd, O);
    return px;
  }
  function impostor() { // なりすまし
    const px = blank();
    circle(px, 8, 8, 6, WL, WL, WL, O);
    set(px, 5, 6, O); set(px, 11, 6, O);
    return px;
  }
  function hideout() { // 盗賊のねぐら
    const px = blank();
    frame(px, 3, 8, 10, 6, WDd, O);
    rect(px, 3, 10, 10, 2, GO);
    candleIcon(px, 13, 8);
    return px;
  }
  function ossuary() { // 骨の間
    const px = blank();
    for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) circle(px, 2 + c * 4, 3 + r * 5, 1, WL, WL, WL, WL);
    return px;
  }
  function viscount() { // 子爵
    const px = blank();
    frame(px, 3, 5, 10, 8, RF, O);
    circle(px, 8, 3, 2, GO, GOl, GOd, O);
    return px;
  }
  function forgery() { // 贋金
    const px = blank();
    circle(px, 6, 9, 4, GO, GOl, GOd, O);
    circle(px, 10, 6, 3, GOd, GOd, GOd, O);
    return px;
  }
  function zealot() { // 邪教徒
    const px = blank();
    circle(px, 8, 10, 4, MEd, MEd, MEd, O);
    for (const a of [0, 60, 120, 180, 240, 300]) { const rad = a * Math.PI / 180; set(px, Math.round(8 + 5 * Math.sin(rad)), Math.round(4 + 3 * Math.cos(rad)), FL); }
    return px;
  }
  function gravedigger() { // 墓荒らし
    const px = blank();
    lineThick(px, 4, 13, 12, 4, WD, 2);
    rect(px, 3, 7, 12, 2, STd);
    return px;
  }
  function junkman() { // 古物商
    const px = blank();
    rect(px, 2, 8, 5, 5, WDd); rect(px, 8, 6, 5, 7, MEd);
    return px;
  }
  function psychic() { // 霊能者
    const px = blank();
    circle(px, 8, 10, 3, FL, FLl, FL, O);
    for (const [x, y] of [[3, 3], [12, 4]]) set(px, x, y, GOl);
    return px;
  }
  function ransack() { // 強奪
    const px = blank();
    frame(px, 2, 9, 12, 4, WD, O);
    circle(px, 8, 4, 3, GOd, GOd, GOd, O);
    return px;
  }
  function rework() { // 再普請
    const px = blank();
    rect(px, 3, 10, 5, 3, MEd);
    for (let r = 0; r < 3; r++) rect(px, 2 - r, 9 + r, 9 + r * 2, 1, ME);
    lineThick(px, 11, 4, 11, 9, WDd, 1);
    return px;
  }
  function villain() { // 悪漢
    const px = blank();
    circle(px, 8, 9, 5, O, O, O, O);
    set(px, 5, 7, RF); set(px, 11, 7, RF);
    return px;
  }
  function offering() { // 供物台
    const px = blank();
    frame(px, 3, 10, 10, 4, ST, O);
    for (const x of [5, 8, 11]) candleIcon(px, x, 9);
    return px;
  }
  function huntland() { // 猟場
    const px = blank();
    rect(px, 0, 10, 16, 6, GR);
    for (const x of [3, 8, 12]) circle(px, x, 8, 2, WDd, WDd, WDd, O);
    return px;
  }

  // ---- 拡張「冒険」追加分 (57) ----
  function realmcoin() { // 通用貨
    const px = blank();
    circle(px, 8, 8, 6, GO, GOl, GOd, O);
    set(px, 8, 8, GOd);
    return px;
  }
  function lad() { // 小僧
    const px = blank();
    circle(px, 8, 6, 3, WDl, WDl, WDd, O);
    rect(px, 6, 9, 4, 5, GR);
    return px;
  }
  function farmer() { // 百姓
    const px = blank();
    for (let x = 2; x < 14; x += 3) lineThick(px, x, 13, x, 8, GO, 1);
    circle(px, 8, 4, 2, WDl, WDl, WDd, O);
    return px;
  }
  function catpaw() { // 猫の手
    const px = blank();
    circle(px, 8, 9, 4, MEd, MEd, MEd, O);
    for (const dx of [-3, -1, 1, 3]) rect(px, 8 + dx, 12, 2, 3, MEd);
    return px;
  }
  function wreck() { // 打ち壊し
    const px = blank();
    rect(px, 2, 8, 8, 4, WDd);
    circle(px, 12, 11, 3, MEd, MEd, MEd, O);
    return px;
  }
  function wardstone() { // 護り石
    const px = blank();
    frame(px, 6, 3, 4, 10, ST, O);
    for (const [x, y] of [[3, 3], [13, 4]]) set(px, x, y, WTl);
    return px;
  }
  function escort() { // 護衛兵
    const px = blank();
    circle(px, 5, 6, 2, WDl, WDl, WDd, O); rect(px, 4, 9, 2, 5, MEd);
    circle(px, 11, 6, 2, WDl, WDl, WDd, O); rect(px, 10, 9, 2, 5, RF);
    return px;
  }
  function stonecell() { // 石牢
    const px = blank();
    frame(px, 2, 2, 12, 12, ST, O);
    for (const x of [5, 8, 11]) lineThick(px, x, 3, x, 13, O, 1);
    return px;
  }
  function kit() { // 旅支度
    const px = blank();
    frame(px, 3, 8, 10, 6, WDd, O);
    lineThick(px, 3, 10, 13, 10, WD, 1);
    return px;
  }
  function pathguide() { // 道案内
    const px = blank();
    lineThick(px, 8, 3, 8, 13, WDd, 1);
    rect(px, 3, 5, 8, 3, WD);
    rect(px, 6, 8, 8, 3, WD);
    return px;
  }
  function copycat() { // 写し
    const px = blank();
    circle(px, 5, 8, 4, MEd, ME, MEd, O);
    circle(px, 11, 8, 4, MEd, ME, MEd, O);
    return px;
  }
  function crow() { // カラス
    const px = blank();
    circle(px, 8, 9, 4, O, O, O, O);
    circle(px, 8, 5, 3, O, O, O, O);
    lineThick(px, 10, 4, 13, 3, O, 1);
    set(px, 6, 4, GOl);
    return px;
  }
  function courier() { // 早馬
    const px = blank();
    rect(px, 2, 8, 9, 5, WD);
    circle(px, 13, 6, 2, RF, RFl, RFd, O);
    return px;
  }
  function skinflint() { // けちん坊
    const px = blank();
    circle(px, 6, 9, 3, CU, CUl, CUd, O);
    circle(px, 11, 6, 2, WDl, WDl, WDd, O);
    return px;
  }
  function harbor() { // 港
    const px = blank();
    for (let y = 10; y < 14; y++) for (let x = 0; x < 16; x++) set(px, x, y, (x + y) % 4 < 2 ? WT : WTl);
    rect(px, 5, 5, 6, 5, RF);
    lineThick(px, 8, 2, 8, 5, WDd, 1);
    return px;
  }
  function forester() { // 森番
    const px = blank();
    circle(px, 5, 9, 4, GR, GRl, GR, O);
    lineThick(px, 5, 13, 5, 9, WDd, 1);
    rect(px, 10, 5, 5, 6, WL);
    return px;
  }
  function shapeshift() { // 化け替え
    const px = blank();
    circle(px, 8, 10, 4, MEd, MEd, MEd, O);
    for (let i = 0; i < 5; i++) set(px, 10 + Math.round(Math.sin(i) * 2), 6 - i, FL);
    return px;
  }
  function tinkerer() { // からくり師
    const px = blank();
    rect(px, 5, 3, 6, 2, MEd);
    rect(px, 6, 9, 4, 4, MEd);
    circle(px, 12, 4, 2, FL, FLl, FL, O);
    return px;
  }
  function bridgeogre() { // 橋守の鬼
    const px = blank();
    rect(px, 0, 9, 16, 2, WDd);
    circle(px, 8, 5, 4, GR, GRl, GR, O);
    set(px, 6, 4, FL); set(px, 10, 4, FL);
    return px;
  }
  function bigman() { // 大男
    const px = blank();
    rect(px, 5, 4, 6, 7, WDd);
    circle(px, 8, 2, 3, WDl, WDl, WDd, O);
    rect(px, 3, 11, 4, 3, WDd); rect(px, 9, 11, 4, 3, WDd);
    return px;
  }
  function mazewood() { // 迷いの森
    const px = blank();
    for (const [x, y] of [[2, 10], [6, 6], [10, 9], [13, 5]]) circle(px, x, y, 3, GR, GRl, GR, O);
    return px;
  }
  function phantomcity() { // 幻の都
    const px = blank();
    for (const x of [2, 7, 11]) rect(px, x, 14 - (x % 5) - 6, 4, (x % 5) + 6, MEd);
    return px;
  }
  function oldrelic() { // 古の宝
    const px = blank();
    circle(px, 8, 9, 5, ST, STl, STd, O);
    diamond(px, 8, 8, 3, GO, GOd);
    return px;
  }
  function carriage() { // お召し馬車
    const px = blank();
    frame(px, 3, 5, 10, 6, RF, O);
    circle(px, 5, 12, 2, MEd, MEd, MEd, O);
    circle(px, 11, 12, 2, MEd, MEd, MEd, O);
    return px;
  }
  function raconteur() { // 講釈師
    const px = blank();
    circle(px, 8, 8, 5, WDl, WDl, WDd, O);
    circle(px, 8, 5, 2, WL, WL, WL, O);
    return px;
  }
  function bogfiend() { // 沼の魔物
    const px = blank();
    for (let r = 0; r < 8; r++) { const half = Math.max(1, Math.round(r * 0.4)); for (let c = -half; c <= half; c++) set(px, 8 + c, 13 - r, GRl); }
    set(px, 6, 8, GOl); set(px, 10, 8, GOl);
    return px;
  }
  function windfall() { // 掘り当て
    const px = blank();
    rect(px, 3, 10, 10, 3, WDd);
    circle(px, 6, 9, 2, GO, GOl, GOd, O);
    circle(px, 11, 10, 2, CU, CUl, CUd, O);
    return px;
  }
  function vintner() { // 酒屋
    const px = blank();
    rect(px, 6, 2, 4, 3, GO);
    rect(px, 7, 5, 2, 2, GOd);
    rect(px, 5, 7, 6, 6, GOd);
    return px;
  }
  function farland() { // 果ての地
    const px = blank();
    lineThick(px, 5, 14, 5, 3, WDd, 1);
    for (let r = 0; r < 4; r++) rect(px, 6, 3 + r, 6 - r, 1, RF);
    return px;
  }
  function servant() { // 奉公人
    const px = blank();
    circle(px, 8, 6, 2, WDl, WDl, WDd, O);
    rect(px, 5, 9, 6, 5, MEd);
    rect(px, 4, 14, 8, 1, WL);
    return px;
  }
  function seeker() { // 探し屋
    const px = blank();
    circle(px, 6, 6, 4, T, T, T, O);
    lineThick(px, 9, 9, 13, 13, MEd, 2);
    return px;
  }
  function fighter() { // 戦士
    const px = blank();
    lineThick(px, 5, 2, 5, 12, ME, 2);
    lineThick(px, 2, 5, 8, 5, MEd, 1);
    circle(px, 12, 7, 3, ST, STl, STd, O);
    return px;
  }
  function paragon() { // 英傑
    const px = blank();
    circle(px, 8, 9, 5, GO, GOl, GOd, O);
    diamond(px, 8, 8, 2, WTl, O);
    return px;
  }
  function victor() { // 覇者
    const px = blank();
    circle(px, 8, 6, 4, GO, GOl, GOd, O);
    rect(px, 5, 10, 6, 4, RF);
    return px;
  }
  function ashigaru() { // 足軽
    const px = blank();
    circle(px, 8, 6, 4, RF, RFl, RFd, O);
    lineThick(px, 8, 8, 8, 13, WDd, 1);
    return px;
  }
  function deserter() { // 落ち武者
    const px = blank();
    circle(px, 8, 7, 4, MEd, MEd, MEd, O);
    for (const x of [4, 12]) set(px, x, 13, WDd);
    return px;
  }
  function follower() { // 門人
    const px = blank();
    circle(px, 5, 8, 3, WDl, WDl, WDd, O);
    circle(px, 11, 8, 3, WDl, WDl, WDd, O);
    rect(px, 7, 11, 2, 3, RF);
    return px;
  }
  function master() { // 師範
    const px = blank();
    circle(px, 8, 6, 3, WDl, WDl, WDd, O);
    rect(px, 5, 9, 6, 5, MEd);
    for (const [x, c] of [[2, RF], [12, WT]]) rect(px, x, 6, 2, 4, c);
    return px;
  }
  function e_soup() { // 炊き出し
    const px = blank();
    circle(px, 8, 10, 5, MEd, MEd, MEd, O);
    circle(px, 8, 8, 3, FL, FLl, FL, O);
    return px;
  }
  function e_advance() { // 前借り
    const px = blank();
    circle(px, 6, 9, 3, GO, GOl, GOd, O);
    rect(px, 9, 5, 5, 4, WL);
    return px;
  }
  function e_trial() { // 腕試し
    const px = blank();
    circle(px, 8, 8, 6, WDl, WDl, WDd, O);
    circle(px, 8, 8, 4, WD, WD, WDd, O);
    return px;
  }
  function e_keep() { // 取り置き
    const px = blank();
    frame(px, 3, 7, 10, 7, WDd, O);
    rect(px, 3, 9, 10, 2, GO);
    return px;
  }
  function e_scouts() { // 物見の衆
    const px = blank();
    for (const x of [3, 8, 12]) circle(px, x, 9, 2, WDl, WDl, WDd, O);
    return px;
  }
  function e_travelfair() { // 旅回りの市
    const px = blank();
    for (const x of [2, 7, 11]) rect(px, x, 8, 3, 6, RF);
    return px;
  }
  function e_bonfire() { // どんど焼き
    const px = blank();
    for (let r = 0; r < 8; r++) { const half = Math.max(1, 5 - Math.round(r * 0.4)); for (let c = -half; c <= half; c++) set(px, 8 + c, 13 - r, r < 4 ? FL : FLl); }
    return px;
  }
  function e_outing() { // 遠出
    const px = blank();
    lineThick(px, 1, 13, 15, 3, WDl, 1);
    for (const [x, y] of [[4, 11], [8, 8], [12, 6]]) set(px, x, y, WD);
    return px;
  }
  function e_ferry() { // 舟便
    const px = blank();
    for (let y = 10; y < 14; y++) for (let x = 0; x < 16; x++) set(px, x, y, (x + y) % 4 < 2 ? WT : WTl);
    rect(px, 5, 6, 6, 4, WD);
    lineThick(px, 8, 2, 8, 6, WDd, 1);
    return px;
  }
  function e_plan() { // 段取り
    const px = blank();
    frame(px, 2, 3, 12, 9, WL, O);
    for (const y of [6, 9]) lineThick(px, 4, y, 12, y, WLd, 1);
    return px;
  }
  function e_errand() { // 使いの旅
    const px = blank();
    circle(px, 8, 4, 2, WL, WL, WL, O);
    lineThick(px, 8, 6, 8, 11, ME, 1);
    for (const [x, y] of [[3, 13], [6, 12], [10, 12], [13, 13]]) set(px, x, y, WDd);
    return px;
  }
  function e_pilgrim() { // お参り
    const px = blank();
    roof(px, 3, 3, 10, 4, WTd, WTl, WT); frame(px, 4, 7, 8, 7, ST, O);
    lineThick(px, 8, 2, 8, 0, WDd, 1);
    return px;
  }
  function e_soiree() { // 夜会
    const px = blank();
    circle(px, 5, 8, 3, RF, RFl, RFd, O);
    circle(px, 11, 8, 3, MEd, ME, MEd, O);
    return px;
  }
  function e_nightraid() { // 夜討ち
    const px = blank();
    circle(px, 8, 7, 4, O, O, O, O);
    circle(px, 13, 3, 3, WL, WL, WL, WL);
    return px;
  }
  function e_searoute() { // 航路開き
    const px = blank();
    frame(px, 2, 3, 12, 8, WL, O);
    lineThick(px, 4, 5, 12, 9, RF, 1);
    return px;
  }
  function e_barter() { // 物々交換
    const px = blank();
    circle(px, 5, 9, 3, CU, CUl, CUd, O);
    circle(px, 11, 6, 3, WT, WTl, WTd, O);
    return px;
  }
  function e_secretart() { // 秘伝
    const px = blank();
    frame(px, 3, 3, 10, 10, WL, O);
    for (const y of [6, 9, 12]) lineThick(px, 5, y, 11, y, RF, 1);
    return px;
  }
  function e_practice() { // 稽古
    const px = blank();
    rect(px, 5, 3, 6, 2, MEd);
    for (let r = 0; r < 4; r++) rect(px, 3 - r, 5 + r, 10 + r * 2, 1, ME);
    return px;
  }
  function e_signpost() { // 道しるべ
    const px = blank();
    lineThick(px, 5, 14, 5, 3, WDd, 1);
    rect(px, 5, 3, 8, 3, WD);
    return px;
  }

  // ---- 拡張「帝国」76 種 ----
  function twinTower(top, bot) { // 上下 2 種の山を示す、重なった 2 つの三角屋根
    const px = blank();
    roof(px, 2, 2, 8, 5, top, top, top);
    frame(px, 3, 7, 6, 4, WL, O);
    roof(px, 7, 8, 8, 5, bot, bot, bot);
    frame(px, 8, 13, 6, 2, ST, O);
    return px;
  }
  const p_settlers = () => twinTower(RF, WT);
  const p_catapult = () => twinTower(ME, ST);
  const p_patrician = () => twinTower(GO, WD);
  const p_encampment = () => twinTower(RF, WDd);
  const p_gladiator = () => twinTower(CU, SI);
  function colonist() { // 入植者: 小屋と鍬
    const px = blank();
    frame(px, 2, 8, 6, 6, WL, O);
    roof(px, 1, 5, 8, 3, RF, RFl, RFd);
    lineThick(px, 10, 13, 13, 4, WD, 1);
    rect(px, 12, 3, 3, 2, MEd);
    return px;
  }
  function busyvillage() { return village(); }
  function trebuchet() { // 石弓
    const px = blank();
    lineThick(px, 3, 13, 12, 3, WD, 2);
    lineThick(px, 12, 3, 14, 8, WDl, 1);
    circle(px, 3, 13, 2, ST, STl, STd, O);
    return px;
  }
  function pebbles() { // 石ころ
    const px = blank();
    for (const [x, y, r] of [[5, 9, 2], [10, 11, 3], [3, 12, 2]]) circle(px, x, y, r, ST, STl, STd, O);
    return px;
  }
  function notable() { // 名士: 巻物と冠
    const px = blank();
    frame(px, 2, 8, 12, 5, WL, O);
    rect(px, 6, 2, 4, 3, GO);
    for (const x of [6, 8, 10]) set(px, x, 1, GOl);
    return px;
  }
  function emporium() { // 大商店: 積んだ品
    const px = blank();
    rect(px, 2, 6, 4, 8, CU); rect(px, 6, 3, 4, 11, SI); rect(px, 10, 8, 4, 6, GO);
    return px;
  }
  function bivouac() { // 野営: テント
    const px = blank();
    roof(px, 2, 6, 12, 7, WDd, WD, WDl);
    return px;
  }
  function spoil() { // 戦利の品: 開いた宝箱
    const px = blank();
    frame(px, 2, 8, 12, 5, WD, O);
    rect(px, 2, 6, 12, 2, WDd);
    circle(px, 8, 10, 1, GO, GOl, GOd, O);
    return px;
  }
  function fightman() { // 闘士: 交差する剣
    const px = blank();
    lineThick(px, 2, 3, 13, 12, ME, 2);
    lineThick(px, 2, 12, 13, 3, ME, 2);
    return px;
  }
  function fortune() { // 一財産: 二重の金貨
    const px = blank();
    circle(px, 5, 8, 4, GO, GOl, GOd, O);
    circle(px, 11, 8, 4, GO, GOl, GOd, O);
    return px;
  }
  function castles() { return castle(); }
  function chariot() { // 馬車競べ: 車輪
    const px = blank();
    circle(px, 8, 10, 5, WD, WDl, WDd, O);
    circle(px, 8, 10, 1, WDd, WDd, WDd, O);
    for (const a of [0, 60, 120]) { const r = Math.PI * a / 180; set(px, Math.round(8 + 5 * Math.sin(r)), Math.round(10 + 5 * Math.cos(r)), WDd); }
    return px;
  }
  function temptress() { // 魔性の女: 頭巾と瞳
    const px = blank();
    circle(px, 8, 8, 5, PU, PUl, PUd, O);
    set(px, 6, 7, GOl); set(px, 10, 7, GOl);
    return px;
  }
  function vegmarket() { // 野菜市: 台の上の野菜
    const px = blank();
    rect(px, 2, 10, 12, 3, WD);
    circle(px, 5, 8, 2, GR, GRl, GR, O);
    circle(px, 9, 8, 2, RF, RFl, RFd, O);
    circle(px, 12, 9, 2, GOl, GO, GOd, O);
    return px;
  }
  function mechanic() { // 技師: 歯車
    const px = blank();
    circle(px, 8, 8, 5, ME, ME, MEd, O);
    circle(px, 8, 8, 2, MEd, MEd, MEd, O);
    for (const a of [0, 90, 180, 270]) { const r = Math.PI * a / 180; set(px, Math.round(8 + 6 * Math.sin(r)), Math.round(8 + 6 * Math.cos(r)), ME); }
    return px;
  }
  function oblation() { // 捧げ物: 祭壇と炎
    const px = blank();
    frame(px, 4, 9, 8, 5, ST, O);
    circle(px, 8, 6, 2, FL, FLl, FL, O);
    return px;
  }
  function shrine() { return torii(); }
  function torii() { // 鳥居
    const px = blank();
    rect(px, 3, 5, 2, 9, RF); rect(px, 11, 5, 2, 9, RF);
    rect(px, 1, 3, 14, 2, RF);
    rect(px, 2, 5, 12, 1, RFd);
    return px;
  }
  function villa() { return manor(); }
  function archivist() { // 書庫番: 積んだ本
    const px = blank();
    for (const [x, c] of [[1, CU], [5, SI], [9, GO], [13, WD]]) rect(px, x, 6, 3, 9, c);
    return px;
  }
  function principal() { // 元金: 借金の札
    const px = blank();
    frame(px, 2, 3, 12, 9, WL, O);
    for (const y of [6, 9]) lineThick(px, 4, y, 12, y, WLd, 1);
    circle(px, 12, 12, 3, GO, GOl, GOd, O);
    return px;
  }
  function luckycharm() { // 縁起物: 御守り
    const px = blank();
    diamond(px, 8, 8, 5, GO, GOd);
    set(px, 8, 8, GOl);
    return px;
  }
  function scepter() { // 玉冠
    const px = blank();
    lineThick(px, 8, 14, 8, 4, GO, 2);
    circle(px, 8, 3, 3, PU, PUl, PUd, O);
    return px;
  }
  function meetinghall() { // 寄り合い所: 卓を囲む
    const px = blank();
    rect(px, 3, 9, 10, 3, WD);
    circle(px, 3, 7, 2, ST, STl, STd, O);
    circle(px, 13, 7, 2, ST, STl, STd, O);
    return px;
  }
  function gardener() { // 植木屋: 芽
    const px = blank();
    rect(px, 0, 11, 16, 5, GR);
    lineThick(px, 8, 11, 8, 5, GRl, 1);
    circle(px, 8, 4, 2, GRl, GRl, GR, O);
    return px;
  }
  function hoplite() { // 重装兵: 盾と槍
    const px = blank();
    frame(px, 2, 5, 6, 9, ME, O);
    lineThick(px, 10, 13, 14, 2, WD, 1);
    return px;
  }
  function wildchase() { // 狩り立て: 足あと
    const px = blank();
    for (const [x, y] of [[3, 12], [6, 9], [10, 6], [13, 3]]) circle(px, x, y, 1, WDd, WDd, WDd, O);
    return px;
  }
  function townblock() { return village(); }
  function overking() { // 覇王: 玉座
    const px = blank();
    frame(px, 4, 4, 8, 10, RF, O);
    rect(px, 6, 1, 4, 3, GO);
    return px;
  }
  function royalsmith() { return smithy(); }
  function e_promote() { // 出世: 星章
    const px = blank();
    for (const a of [0, 72, 144, 216, 288]) { const r = Math.PI * a / 180 - Math.PI / 2; set(px, Math.round(8 + 5 * Math.cos(r)), Math.round(8 + 5 * Math.sin(r)), GO); }
    set(px, 8, 8, GOl);
    return px;
  }
  function e_dig() { // 掘り下げ: シャベル
    const px = blank();
    lineThick(px, 3, 13, 12, 4, WD, 2);
    rect(px, 11, 2, 4, 4, ME);
    return px;
  }
  function e_levy() { // 年貢: 借金の山
    const px = blank();
    for (let i = 0; i < 3; i++) circle(px, 5 + i * 3, 11 - i, 2, ST, STl, STd, O);
    return px;
  }
  function e_feast() { // 祝い膳: 皿
    const px = blank();
    circle(px, 8, 9, 5, WL, WL, WLd, O);
    circle(px, 8, 8, 2, RF, RFl, RFd, O);
    return px;
  }
  function e_marriage() { // 祝言: 指輪
    const px = blank();
    circle(px, 6, 9, 3, GO, GOl, GOd, O);
    circle(px, 6, 9, 1, T, T, T, T);
    circle(px, 10, 9, 3, SI, SIl, SId, O);
    circle(px, 10, 9, 1, T, T, T, T);
    return px;
  }
  function e_rite() { // 祭祀: 呪いの輪
    const px = blank();
    circle(px, 8, 8, 5, PU, PUl, PUd, O);
    circle(px, 8, 8, 2, O, O, O, O);
    return px;
  }
  function e_scorch() { // 焦土: 炎
    const px = blank();
    for (const x of [4, 8, 12]) { lineThick(px, x, 13, x, 8, FL, 2); set(px, x, 7, FLl); }
    return px;
  }
  function e_luck() { // 思わぬ幸運: 3枚の金
    const px = blank();
    for (let i = 0; i < 3; i++) circle(px, 4 + i * 4, 10 - (i % 2), 2, GO, GOl, GOd, O);
    return px;
  }
  function e_warcry() { // 勝ちどき: 旗と星
    const px = blank();
    lineThick(px, 4, 14, 4, 2, WDd, 1);
    rect(px, 5, 2, 7, 5, RF);
    return px;
  }
  function e_subdue() { // 平定: 銀貨2枚
    const px = blank();
    circle(px, 6, 9, 4, SI, SIl, SId, O);
    circle(px, 11, 7, 4, SI, SIl, SId, O);
    return px;
  }
  function e_absorb() { // 取り込み: 混ぜた札
    const px = blank();
    rect(px, 3, 5, 5, 8, RF); rect(px, 8, 5, 5, 8, WT);
    return px;
  }
  function e_alms2() { // 喜捨: 手
    const px = blank();
    circle(px, 8, 6, 3, WL, WL, WLd, O);
    lineThick(px, 8, 9, 8, 13, WLd, 2);
    return px;
  }
  function e_unify() { // 天下統一: 玉座と旗
    const px = blank();
    lineThick(px, 6, 14, 6, 2, WDd, 1);
    rect(px, 7, 2, 7, 5, RF);
    circle(px, 12, 12, 2, GO, GOl, GOd, O);
    return px;
  }
  function l_canal() { // 用水路
    const px = blank();
    for (let y = 8; y < 14; y++) for (let x = 0; x < 16; x++) set(px, x, y, (x + y) % 5 < 2 ? WT : WTl);
    return px;
  }
  function l_ring() { // 土俵
    const px = blank();
    circle(px, 8, 8, 6, WD, WDl, WDd, O);
    circle(px, 8, 8, 3, WDd, WDd, WDd, O);
    return px;
  }
  function l_banditden() { // 賊の隠れ里: 洞窟
    const px = blank();
    for (let y = 2; y < 14; y++) { const half = Math.max(1, Math.round(6 * Math.sin((y - 2) / 12 * Math.PI))); for (let x = 8 - half; x < 8 + half; x++) set(px, x, y, ST); }
    circle(px, 8, 10, 3, O, O, O, O);
    return px;
  }
  function l_hall() { return manor(); }
  function l_bathhouse() { // 湯屋
    const px = blank();
    circle(px, 8, 9, 6, WT, WTl, WTd, O);
    for (const [x, y] of [[5, 4], [9, 3], [7, 6]]) set(px, x, y, WL);
    return px;
  }
  function l_battleground() { // 古戦場: 旗2本
    const px = blank();
    lineThick(px, 4, 14, 4, 4, WDd, 1); rect(px, 5, 4, 5, 4, RF);
    lineThick(px, 12, 14, 12, 6, WDd, 1); rect(px, 9, 6, 4, 3, ME);
    return px;
  }
  function l_arcade() { // 回廊: 柱並び
    const px = blank();
    for (const x of [2, 6, 10, 14]) rect(px, x, 4, 2, 10, ST);
    rect(px, 1, 3, 14, 2, STl);
    return px;
  }
  function l_ruinedtemple() { // 荒れ寺: 崩れた柱
    const px = blank();
    rect(px, 2, 8, 2, 6, ST); rect(px, 7, 4, 2, 10, ST); rect(px, 12, 10, 2, 4, ST);
    return px;
  }
  function l_fountain() { // 泉水
    const px = blank();
    circle(px, 8, 10, 5, ST, STl, STd, O);
    circle(px, 8, 10, 3, WT, WTl, WTd, O);
    rect(px, 7, 3, 2, 6, ST);
    return px;
  }
  function l_donjon() { // 天守
    const px = blank();
    rect(px, 5, 2, 6, 12, ST);
    rect(px, 4, 1, 8, 2, STl);
    set(px, 7, 6, WT); set(px, 8, 6, WT);
    return px;
  }
  function l_maze() { // 迷路
    const px = blank();
    for (let y = 2; y < 14; y += 4) for (let x = 2; x < 14; x += 4) rect(px, x, y, 3, 2, GR);
    return px;
  }
  function l_pass() { // 関所越え: 門
    const px = blank();
    rect(px, 3, 3, 3, 11, ST); rect(px, 10, 3, 3, 11, ST);
    rect(px, 6, 8, 4, 6, WDd);
    return px;
  }
  function l_treasury() { // 宝物殿
    const px = blank();
    for (let i = 0; i < 3; i++) circle(px, 4 + i * 4, 11 - (i % 2) * 2, 2, GO, GOl, GOd, O);
    diamond(px, 12, 5, 2, WT, O);
    return px;
  }
  function l_pillar() { // 石柱
    const px = blank();
    rect(px, 6, 1, 4, 14, ST);
    rect(px, 5, 1, 6, 2, STl);
    return px;
  }
  function l_fruitfield() { // 果物畑
    const px = blank();
    lineThick(px, 8, 13, 8, 8, WDd, 1);
    circle(px, 8, 6, 4, GR, GRl, GR, O);
    set(px, 6, 5, RF); set(px, 10, 7, RF);
    return px;
  }
  function l_palace() { // 御殿
    const px = blank();
    roof(px, 1, 2, 14, 4, RF, RFl, RFd);
    frame(px, 2, 6, 12, 7, WL, O);
    for (const x of [4, 8, 12]) set(px, x, 8, WT);
    return px;
  }
  function l_mound() { // 塚
    const px = blank();
    for (let y = 9; y < 14; y++) { const half = Math.round((14 - y) * 1.4); for (let x = 8 - half; x < 8 + half; x++) set(px, x, y, GR); }
    rect(px, 7, 4, 2, 5, ST);
    return px;
  }
  function l_tower() { // 高楼
    const px = blank();
    rect(px, 6, 1, 4, 13, ST);
    for (const y of [4, 8]) set(px, 7, y, WT);
    return px;
  }
  function l_gate() { // 大門
    const px = blank();
    rect(px, 1, 2, 3, 12, ST); rect(px, 12, 2, 3, 12, ST);
    rect(px, 1, 1, 14, 2, STl);
    rect(px, 5, 7, 6, 7, WDd);
    return px;
  }
  function l_wall() { // 城壁
    const px = blank();
    rect(px, 0, 7, 16, 7, ST);
    for (let x = 0; x < 16; x += 4) rect(px, x, 5, 2, 2, STl);
    return px;
  }
  function l_lair() { // 獣の巣: 骨
    const px = blank();
    for (let y = 2; y < 14; y++) { const half = Math.max(1, Math.round(6 * Math.sin((y - 2) / 12 * Math.PI))); for (let x = 8 - half; x < 8 + half; x++) set(px, x, y, O); }
    set(px, 6, 10, BN); set(px, 10, 10, BN);
    return px;
  }
  function castleShape(h, towers) { // 城シリーズ共通
    const px = blank();
    rect(px, 3, 16 - h, 10, h, ST);
    for (let x = 3; x < 13; x += 3) rect(px, x, 15 - h, 2, 2, STl);
    return px;
  }
  const c_humble = () => castleShape(6);
  const c_crumbling = () => castleShape(7);
  const c_small = () => castleShape(8);
  function c_haunted() {
    const px = castleShape(9);
    set(px, 7, 10, PU); set(px, 8, 10, PU);
    return px;
  }
  const c_opulent = () => castleShape(10);
  const c_sprawling = () => castleShape(11);
  const c_grand = () => castleShape(12);
  function c_king() {
    const px = castleShape(13);
    set(px, 8, 3, GOl);
    return px;
  }

  // ---- 拡張「夜想曲」77 種 ----
  function boonIcon(c) { // 恵み: 光る輪
    const px = blank();
    for (const a of [0, 45, 90, 135, 180, 225, 270, 315]) { const r = Math.PI * a / 180; set(px, Math.round(8 + 6 * Math.sin(r)), Math.round(8 + 6 * Math.cos(r)), c); }
    circle(px, 8, 8, 3, GOl, GOl, GOl, O);
    return px;
  }
  const b_earth = () => boonIcon(WD);
  const b_field = () => boonIcon(GOl);
  const b_flame = () => boonIcon(FL);
  const b_forest = () => boonIcon(GR);
  const b_moon = () => boonIcon(WT);
  const b_mountain = () => boonIcon(ST);
  const b_river = () => boonIcon(WT);
  const b_sea = () => boonIcon(WTd);
  const b_sky = () => boonIcon(WL);
  const b_sun = () => boonIcon(GO);
  const b_swamp = () => boonIcon(GRl);
  const b_wind = () => boonIcon(WLd);
  function hexIcon(c) { // 呪詛: 割れた輪
    const px = blank();
    circle(px, 8, 8, 6, PUd, PU, PUd, O);
    circle(px, 8, 8, 3, c, c, c, O);
    return px;
  }
  const h_omens = () => hexIcon(O);
  const h_delusion = () => hexIcon(PUl);
  const h_envy = () => hexIcon(GR);
  const h_famine = () => hexIcon(WDd);
  const h_fear = () => hexIcon(ST);
  const h_greed = () => hexIcon(CU);
  const h_haunting = () => hexIcon(WL);
  const h_locusts = () => hexIcon(WDd);
  const h_misery = () => hexIcon(STd);
  const h_plague = () => hexIcon(GR);
  const h_poverty = () => hexIcon(WDd);
  const h_war = () => hexIcon(MEd);
  function s_lost() { // 森の迷い子
    const px = blank();
    circle(px, 8, 9, 3, WL, WL, WLd, O);
    lineThick(px, 6, 12, 6, 15, WLd, 1); lineThick(px, 10, 12, 10, 15, WLd, 1);
    return px;
  }
  function stateIcon(c) { // 状態: 返す札
    const px = blank();
    frame(px, 3, 3, 10, 10, c, O);
    return px;
  }
  const s_deluded = () => stateIcon(PU);
  const s_envious = () => stateIcon(GR);
  const s_miserable = () => stateIcon(STd);
  const s_twice = () => stateIcon(ST);
  function dimmirror() { // 曇り鏡
    const px = blank();
    circle(px, 8, 8, 6, ST, STl, STd, O);
    circle(px, 8, 8, 4, WTl, WTl, WT, O);
    return px;
  }
  function luckycoin() { // 福銭
    const px = blank();
    return coin(GO, GOl, GOd, 3);
  }
  function kid() { // 子山羊
    const px = blank();
    circle(px, 8, 9, 5, WL, WL, WLd, O);
    circle(px, 5, 6, 3, WL, WL, WLd, O);
    rect(px, 4, 13, 2, 2, WLd); rect(px, 10, 13, 2, 2, WLd);
    return px;
  }
  function cursedcoin() { // 祟り金
    const px = blank();
    circle(px, 8, 8, 6, PU, PUl, PUd, O);
    set(px, 8, 8, GOl);
    return px;
  }
  function wishlamp() { return lantern(); }
  function lantern() { // 願いの灯
    const px = blank();
    frame(px, 5, 4, 6, 8, ME, O);
    circle(px, 8, 8, 2, GOl, GOl, GOl, O);
    return px;
  }
  function grazing() { return cottage(); }
  function purse() { // 巾着
    const px = blank();
    circle(px, 8, 9, 6, PUd, PU, PUd, O);
    rect(px, 5, 3, 6, 3, PU);
    return px;
  }
  function wisp() { // 鬼火
    const px = blank();
    circle(px, 8, 8, 5, WT, WTl, WT, O);
    circle(px, 8, 8, 2, WTl, WTl, WTl, O);
    return px;
  }
  function imp2() { // 小悪魔
    const px = blank();
    circle(px, 8, 9, 5, CUd, CU, CUd, O);
    set(px, 6, 8, GOl); set(px, 10, 8, GOl);
    lineThick(px, 5, 4, 3, 1, CUd, 1); lineThick(px, 11, 4, 13, 1, CUd, 1);
    return px;
  }
  function phantom() { // 亡霊
    const px = blank();
    for (let r = 0; r < 9; r++) { const half = Math.max(1, Math.round(r * 0.4)); for (let c = -half; c < half; c++) set(px, 8 + c, 3 + r, WL); }
    set(px, 6, 6, O); set(px, 10, 6, O);
    return px;
  }
  function wish2() { // 願い事
    const px = blank();
    for (const a of [0, 72, 144, 216, 288]) { const r = Math.PI * a / 180 - Math.PI / 2; set(px, Math.round(8 + 5 * Math.cos(r)), Math.round(8 + 5 * Math.sin(r)), GOl); }
    set(px, 8, 8, GO);
    return px;
  }
  function nightwing() { // 夜の羽
    const px = blank();
    for (let r = 0; r < 6; r++) { set(px, 3 + r, 4 + r, O); set(px, 13 - r, 4 + r, O); }
    circle(px, 8, 10, 3, CU, CUl, CUd, O);
    return px;
  }
  function zombieIcon() { // 屍
    const px = blank();
    circle(px, 8, 6, 3, BN, BN, BNd, O);
    rect(px, 5, 9, 6, 6, BNd);
    return px;
  }
  const z_apprentice = zombieIcon;
  const z_mason = zombieIcon;
  const z_spy = zombieIcon;
  function druid() { // 森の賢者
    const px = blank();
    roof(px, 5, 1, 6, 4, GRl, GRl, GR);
    frame(px, 6, 5, 4, 8, WD, O);
    return px;
  }
  function loyaldog() { // 番の犬
    const px = blank();
    circle(px, 6, 10, 4, WD, WDl, WDd, O);
    circle(px, 10, 8, 3, WD, WDl, WDd, O);
    return px;
  }
  function protector() { // 守り手
    const px = blank();
    frame(px, 4, 3, 8, 11, ME, O);
    rect(px, 7, 5, 2, 5, MEd);
    return px;
  }
  function priory() { // 僧坊
    const px = blank();
    frame(px, 3, 2, 10, 12, WL, O);
    lineThick(px, 8, 4, 8, 12, WLd, 1);
    return px;
  }
  function sprite() { // 妖精
    const px = blank();
    circle(px, 8, 8, 4, PUl, PUl, PU, O);
    for (const [x, y] of [[3, 4], [13, 4], [3, 12], [13, 12]]) set(px, x, y, PUl);
    return px;
  }
  function trailer() { // 足跡たどり
    const px = blank();
    for (const [x, y] of [[3, 12], [6, 9], [10, 6], [13, 3]]) circle(px, x, y, 1, WDd, WDd, WDd, O);
    return px;
  }
  function fairychild() { // 化け子
    const px = blank();
    circle(px, 8, 9, 4, PUl, PUl, PU, O);
    for (const [x, y] of [[4, 5], [12, 5], [8, 3]]) set(px, x, y, GOl);
    return px;
  }
  function simpleton() { // うつけ者
    const px = blank();
    circle(px, 8, 9, 5, GOl, GOl, GO, O);
    set(px, 6, 8, O); set(px, 10, 8, O);
    return px;
  }
  function emptytown() { // 無人の町
    const px = blank();
    roof(px, 1, 6, 6, 4, RF, RFl, RFd); frame(px, 2, 10, 4, 4, WLd, O);
    roof(px, 9, 3, 6, 5, RFd, RF, RFl); frame(px, 10, 8, 4, 6, WLd, O);
    return px;
  }
  function goblin() { // 小鬼
    const px = blank();
    circle(px, 8, 9, 5, GR, GRl, GR, O);
    set(px, 5, 8, GOl); set(px, 11, 8, GOl);
    return px;
  }
  function firewatch() { // 火の番
    const px = blank();
    circle(px, 8, 11, 2, FL, FLl, FL, O);
    for (const [x, y] of [[6, 9], [8, 6], [10, 9]]) set(px, x, y, FLl);
    return px;
  }
  function hiddencave() { // 隠れ洞
    const px = blank();
    for (let r = 0; r < 10; r++) { const half = Math.max(1, Math.round(6 * Math.sin(r / 10 * Math.PI))); for (let c = -half; c < half; c++) set(px, 8 + c, 2 + r, ST); }
    circle(px, 8, 8, 2, O, O, O, O);
    return px;
  }
  function minstrel() { // 琵琶法師
    const px = blank();
    circle(px, 10, 10, 4, WD, WDl, WDd, O);
    lineThick(px, 10, 6, 13, 2, WDl, 1);
    return px;
  }
  function luckyvillage() { return village(); }
  function graveyard() { // 無縁墓
    const px = blank();
    rect(px, 5, 6, 6, 8, ST);
    rect(px, 6, 3, 4, 4, ST);
    return px;
  }
  function secretcouncil() { // 密議
    const px = blank();
    circle(px, 5, 9, 3, PUd, PU, PUd, O);
    circle(px, 11, 9, 3, PUd, PU, PUd, O);
    circle(px, 8, 5, 3, PUd, PU, PUd, O);
    return px;
  }
  function demonforge() { // 鬼の仕事場
    const px = blank();
    rect(px, 5, 3, 6, 2, MEd);
    for (let r = 0; r < 4; r++) rect(px, 3 - r, 5 + r, 10 + r * 2, 1, ME);
    circle(px, 12, 3, 2, FL, FLl, FL, O);
    return px;
  }
  function purifier() { // お祓い師
    const px = blank();
    circle(px, 8, 9, 5, WL, WL, WLd, O);
    circle(px, 8, 9, 2, WT, WTl, WTd, O);
    return px;
  }
  function deadcaller() { // 死霊使い
    const px = blank();
    circle(px, 8, 7, 3, BN, BN, BNd, O);
    rect(px, 5, 10, 6, 5, PUd);
    return px;
  }
  function herdsman() { // 牧人
    const px = blank();
    circle(px, 5, 10, 3, WL, WL, WLd, O);
    circle(px, 10, 9, 3, WL, WL, WLd, O);
    circle(px, 13, 10, 3, WL, WL, WLd, O);
    return px;
  }
  function sneak() { // 忍び足
    const px = blank();
    circle(px, 8, 9, 4, O, O, O, O);
    circle(px, 8, 9, 2, PU, PUl, PUd, O);
    return px;
  }
  function shoemender() { // 靴直し
    const px = blank();
    rect(px, 3, 11, 5, 3, WDd); rect(px, 9, 11, 5, 3, WDd);
    lineThick(px, 5, 11, 5, 4, ME, 1);
    return px;
  }
  function tombchamber() { // 石室
    const px = blank();
    frame(px, 3, 4, 10, 9, ST, O);
    for (let i = 0; i < 3; i++) circle(px, 5 + i * 3, 11, 1, GO, GOl, GOd, O);
    return px;
  }
  function hauntedvillage() { // 祟りの村
    const px = blank();
    roof(px, 1, 6, 6, 4, RF, RFl, RFd); frame(px, 2, 10, 4, 4, WLd, O);
    roof(px, 9, 3, 6, 5, RFd, RF, RFl); frame(px, 10, 8, 4, 6, WLd, O);
    circle(px, 8, 2, 2, WL, WL, WL, O);
    return px;
  }
  function rookery() { // 悪党の巣窟
    const px = blank();
    for (const [x, y] of [[3, 3], [7, 2], [11, 4]]) { lineThick(px, x, y, x + 2, y - 2, O, 1); lineThick(px, x + 2, y - 2, x + 4, y, O, 1); }
    frame(px, 4, 8, 8, 6, WDd, O);
    return px;
  }
  function figurine() { // 土偶
    const px = blank();
    rect(px, 6, 5, 4, 8, ST);
    circle(px, 8, 4, 2, STl, STl, STl, O);
    return px;
  }
  function phantomhorse() { // 化け馬
    const px = blank();
    rect(px, 3, 9, 9, 3, WL);
    rect(px, 10, 4, 3, 5, WL);
    for (const x of [4, 10]) rect(px, x, 12, 2, 3, WLd);
    return px;
  }
  function holygrove() { // 鎮守の森
    const px = blank();
    circle(px, 8, 8, 5, GR, GRl, GR, O);
    circle(px, 8, 8, 2, PUl, PUl, PU, O);
    return px;
  }
  function bully() { // いじめっ子
    const px = blank();
    frame(px, 4, 3, 8, 11, CUd, O);
    rect(px, 6, 6, 4, 2, O);
    return px;
  }
  function doomedhero() { // 薄幸の勇者
    const px = blank();
    frame(px, 5, 2, 6, 10, ME, O);
    circle(px, 8, 13, 2, CU, CUl, CUd, O);
    return px;
  }
  function bloodsucker() { // 血吸い
    const px = blank();
    circle(px, 8, 8, 5, CUd, CUd, CUd, O);
    for (const x of [6, 10]) rect(px, x, 8, 1, 3, WL);
    return px;
  }
  function wolfman() { // 狼男
    const px = blank();
    circle(px, 8, 9, 5, WDd, WD, WDd, O);
    for (const [x, y] of [[5, 6], [11, 6]]) { set(px, x, y, WDd); set(px, x, y - 1, WDd); }
    return px;
  }
  function nightthief() { // 夜盗
    const px = blank();
    circle(px, 8, 9, 5, O, O, O, O);
    rect(px, 6, 9, 4, 4, CU);
    return px;
  }

  // ---- 拡張「ルネサンス」49 種 ----
  function gatekeeper() { // 関守
    const px = blank();
    rect(px, 5, 2, 2, 12, ST); rect(px, 9, 2, 2, 12, ST);
    rect(px, 4, 8, 8, 4, WDd);
    return px;
  }
  function koban() { return coin(GO, GOl, GOd, 3); }
  function lackeys() { // 手下衆
    const px = blank();
    circle(px, 5, 10, 3, WL, WL, WLd, O);
    circle(px, 11, 9, 3, WL, WL, WLd, O);
    return px;
  }
  function troupe() { // 旅一座: 仮面
    const px = blank();
    circle(px, 8, 8, 5, WL, WL, WL, O);
    set(px, 6, 7, O); set(px, 10, 7, O);
    return px;
  }
  function cargo() { return boatIcon(); }
  function boatIcon() {
    const px = blank();
    for (let i = 0; i < 4; i++) rect(px, 6 - i, 10 + i, 4 + i * 2, 1, WD);
    lineThick(px, 8, 10, 8, 2, WDd, 1);
    return px;
  }
  function trial2() { // 試し: 手紙
    const px = blank();
    frame(px, 3, 4, 10, 8, WL, O);
    circle(px, 8, 8, 2, RF, RFl, RFd, O);
    return px;
  }
  function improve() { // 手入れ
    const px = blank();
    lineThick(px, 4, 13, 12, 3, ME, 2);
    return px;
  }
  function flagbearer() { // 旗持ち
    const px = blank();
    lineThick(px, 5, 14, 5, 2, WDd, 1);
    rect(px, 6, 2, 7, 5, RF);
    return px;
  }
  function lair2() { // 隠れ家
    const px = blank();
    for (let r = 0; r < 9; r++) { const half = Math.max(1, Math.round(9 * Math.sin(r / 9 * Math.PI))); for (let c = -half; c < half; c++) set(px, 8 + c, 3 + r, ST); }
    circle(px, 8, 9, 2, O, O, O, O);
    return px;
  }
  function inventor() { // 発明の人
    const px = blank();
    circle(px, 8, 8, 6, ME, ME, MEd, O);
    for (const a of [0, 60, 120, 180, 240, 300]) { const r = Math.PI * a / 180; set(px, Math.round(8 + 7 * Math.sin(r)), Math.round(8 + 7 * Math.cos(r)), ME); }
    return px;
  }
  function mountainvillage() { // 山里
    const px = blank();
    for (let x = 0; x < N; x++) { const top = 10 - Math.round(3 * Math.sin(x * 0.4)); for (let y = top; y < 12; y++) set(px, x, y, ST); }
    frame(px, 5, 8, 6, 5, WL, O);
    return px;
  }
  function backer() { // 後ろ盾
    const px = blank();
    circle(px, 8, 8, 6, CUd, CU, CUd, O);
    set(px, 8, 8, GOl);
    return px;
  }
  function kannushi() { return torii(); }
  function research() { // 調べもの
    const px = blank();
    for (const [x, c] of [[1, CU], [5, SI], [9, GO], [13, WD]]) rect(px, x, 6, 3, 9, c);
    circle(px, 8, 3, 2, WL, WL, WL, O);
    return px;
  }
  function draper() { // 呉服屋
    const px = blank();
    rect(px, 2, 4, 3, 10, CU); rect(px, 6, 4, 3, 10, SI); rect(px, 10, 4, 3, 10, GO);
    return px;
  }
  function yamauba() { // 山姥
    const px = blank();
    circle(px, 8, 9, 5, WDd, WD, WDd, O);
    rect(px, 5, 2, 6, 4, ST);
    return px;
  }
  function recruiter() { // 口入れ屋
    const px = blank();
    circle(px, 5, 10, 3, WL, WL, WLd, O);
    circle(px, 11, 9, 3, WL, WL, WLd, O);
    circle(px, 8, 6, 3, WL, WL, WLd, O);
    return px;
  }
  function baton() { // 采配
    const px = blank();
    lineThick(px, 8, 14, 8, 3, GO, 2);
    circle(px, 8, 2, 3, PU, PUl, PUd, O);
    return px;
  }
  function student() { // 書生
    const px = blank();
    frame(px, 3, 5, 10, 8, WL, O);
    for (const y of [7, 9, 11]) lineThick(px, 5, y, 11, y, WLd, 1);
    return px;
  }
  function carver() { // 彫り師
    const px = blank();
    frame(px, 5, 2, 6, 12, WD, O);
    lineThick(px, 3, 5, 5, 5, MEd, 1);
    return px;
  }
  function clairvoyant() { // 千里眼
    const px = blank();
    diamond(px, 8, 8, 6, PUl, O);
    diamond(px, 8, 8, 3, PU, O);
    return px;
  }
  function spices() { // 香辛の品
    const px = blank();
    for (const [x, c] of [[4, FL], [8, GOl], [12, CU]]) circle(px, x, 9, 3, c, c, c, O);
    return px;
  }
  function swordsman() { // 剣豪
    const px = blank();
    lineThick(px, 3, 13, 13, 3, ME, 2);
    rect(px, 3, 12, 3, 3, WDd);
    return px;
  }
  function treasurer() { // 勘定方
    const px = blank();
    for (let i = 0; i < 3; i++) circle(px, 4 + i * 4, 11, 2, GO, GOl, GOd, O);
    circle(px, 8, 4, 2, GOl, GOl, GO, O);
    lineThick(px, 10, 4, 13, 4, GO, 1);
    return px;
  }
  function badguy() { // 悪玉
    const px = blank();
    frame(px, 4, 3, 8, 11, O, O);
    rect(px, 6, 6, 4, 2, CUd);
    return px;
  }
  function a_flag() { // のぼり旗
    const px = blank();
    lineThick(px, 5, 14, 5, 2, WDd, 1);
    rect(px, 6, 2, 8, 6, RF);
    return px;
  }
  function a_horn() { // 法螺貝
    const px = blank();
    lineThick(px, 3, 11, 10, 4, GO, 2);
    circle(px, 12, 4, 3, GOl, GOl, GO, O);
    return px;
  }
  function key() { // 合鍵
    const px = blank();
    circle(px, 5, 8, 3, GO, GOl, GOd, O);
    lineThick(px, 8, 8, 13, 8, GO, 1);
    set(px, 12, 9, GOd); set(px, 12, 10, GOd);
    return px;
  }
  const a_key = key;
  function a_lantern() { return lantern(); }
  function a_chest() { // 千両箱
    const px = blank();
    frame(px, 2, 8, 12, 5, WD, O);
    rect(px, 2, 6, 12, 2, WDd);
    circle(px, 8, 10, 1, GO, GOl, GOd, O);
    return px;
  }
  function jIcon(c1, c2) { // プロジェクト共通: 盾形
    const px = blank();
    for (let y = 2; y < 12; y++) { const half = Math.max(1, Math.round(6 - Math.abs(y - 7) * 0.6)); for (let x = 8 - half; x < 8 + half; x++) set(px, x, y, y < 12 ? c1 : c2); }
    for (let r = 0; r < 4; r++) { const half = 6 - r * 2; for (let x = 8 - half; x < 8 + half; x++) set(px, x, 12 + r, c2); }
    return px;
  }
  const j_cathedral = () => jIcon(RF, RFd);
  const j_citygate = () => jIcon(ST, STd);
  const j_pageant = () => jIcon(GO, GOd);
  const j_sewers = () => jIcon(WT, WTd);
  const j_starchart = () => jIcon(PU, PUd);
  const j_exploration = () => jIcon(WL, WLd);
  const j_marketday = () => jIcon(GR, GRl);
  const j_silos = () => jIcon(WD, WDd);
  const j_plot = () => jIcon(MEd, O);
  const j_academy = () => jIcon(CU, CUd);
  const j_fleet = () => jIcon(WT, WTl);
  const j_guildhall = () => jIcon(SI, SId);
  const j_piazza = () => jIcon(ST, STl);
  const j_roads = () => jIcon(WDd, WD);
  const j_barracks = () => jIcon(RFd, RF);
  const j_croprotation = () => jIcon(GRl, GR);
  const j_innovation = () => jIcon(ME, MEd);
  const j_canal = () => jIcon(WT, WTd);
  const j_citadel = () => jIcon(STl, ST);

  // ---- 拡張「移動動物園」70 種 ----
  function angler() { // 釣り人
    const px = blank();
    lineThick(px, 3, 11, 12, 4, WD, 1);
    for (let y = 10; y < 14; y++) for (let x = 0; x < 16; x++) if ((x + y) % 4 < 2) set(px, x, y, WT);
    return px;
  }
  function archbishop() { // 大僧正
    const px = blank();
    frame(px, 5, 2, 6, 11, WL, O);
    circle(px, 8, 1, 2, CU, CUl, CUd, O);
    return px;
  }
  function beastfair() { return horseIcon(); }
  function horseIcon() { // 馬形共通
    const px = blank();
    rect(px, 3, 7, 9, 4, WD);
    rect(px, 10, 3, 3, 5, WD);
    for (const x of [4, 10]) rect(px, x, 11, 2, 3, WDd);
    return px;
  }
  function bountyman() { // 懸賞稼ぎ
    const px = blank();
    frame(px, 3, 3, 10, 7, WL, O);
    circle(px, 8, 6, 2, RF, RFl, RFd, O);
    return px;
  }
  function caravan2() { return horseIcon(); }
  function commons() { // 村の広っぱ
    const px = blank();
    circle(px, 4, 10, 2, WL, WL, WL, O);
    circle(px, 8, 9, 2, WL, WL, WL, O);
    circle(px, 12, 10, 2, WL, WL, WL, O);
    return px;
  }
  function corral() { // 放し飼い場
    const px = blank();
    for (const x of [2, 7, 12]) lineThick(px, x, 3, x, 13, WD, 1);
    for (const y of [5, 10]) lineThick(px, 2, y, 13, y, WDl, 1);
    return px;
  }
  function evict() { // 追い立て
    const px = blank();
    frame(px, 5, 6, 8, 7, WL, O);
    roof(px, 4, 2, 10, 4, RF, RFl, RFd);
    return px;
  }
  function falconer() { // 鷹使い
    const px = blank();
    lineThick(px, 5, 13, 5, 6, WDd, 1);
    for (const a of [0, 45, -45]) { const r = Math.PI * a / 180; set(px, Math.round(10 + 4 * Math.sin(r)), Math.round(5 + 4 * Math.cos(r)), STd); }
    return px;
  }
  function goatkeeper() { // 山羊番
    const px = blank();
    circle(px, 6, 10, 3, WL, WL, WLd, O);
    circle(px, 11, 9, 3, WL, WL, WLd, O);
    return px;
  }
  function herddog() { // 牧犬
    const px = blank();
    circle(px, 6, 10, 4, WD, WDl, WDd, O);
    circle(px, 11, 8, 3, WD, WDl, WDd, O);
    return px;
  }
  function hoardpile() { // 蓄え
    const px = blank();
    rect(px, 3, 5, 4, 9, CU); rect(px, 8, 3, 4, 11, SI); rect(px, 12, 6, 3, 8, GO);
    return px;
  }
  function horsemen() { return horseIcon(); }
  function hostel() { return manor(); }
  function huntlodge() { // 狩り小屋
    const px = blank();
    roof(px, 3, 3, 10, 5, RF, RFl, RFd);
    frame(px, 4, 8, 8, 6, WD, O);
    return px;
  }
  function kiln() { // 窯
    const px = blank();
    frame(px, 4, 5, 8, 9, STd, O);
    circle(px, 8, 8, 2, FL, FLl, FL, O);
    return px;
  }
  function livery() { return horseIcon(); }
  function mEventIcon(c) { // m_ イベント共通: 蹄鉄
    const px = blank();
    for (let a = 0; a <= 180; a += 20) { const r = Math.PI * a / 180; set(px, Math.round(8 + 5 * Math.sin(r)), Math.round(6 + 5 * Math.cos(r)), c); }
    return px;
  }
  const m_banish = () => mEventIcon(ST);
  const m_bargain = () => mEventIcon(GO);
  const m_delay = () => mEventIcon(WD);
  const m_demand = () => mEventIcon(CUd);
  const m_despair = () => mEventIcon(PUd);
  const m_enclave = () => mEventIcon(GOl);
  const m_enhance = () => mEventIcon(PU);
  const m_gamble = () => mEventIcon(RF);
  const m_invest = () => mEventIcon(MEd);
  const m_league = () => mEventIcon(GR);
  const m_march = () => mEventIcon(STl);
  const m_populate = () => mEventIcon(WL);
  const m_pursue = () => mEventIcon(WD);
  const m_reap = () => mEventIcon(GO);
  const m_ride = () => mEventIcon(WDl);
  const m_seize = () => mEventIcon(GOl);
  const m_stampede = () => mEventIcon(WDd);
  const m_toil = () => mEventIcon(WL);
  const m_trade = () => mEventIcon(GO);
  const m_transport = () => mEventIcon(ME);
  function nightcat() { // 夜の猫
    const px = blank();
    circle(px, 8, 9, 5, O, O, O, O);
    set(px, 6, 7, GOl); set(px, 10, 7, GOl);
    return px;
  }
  function pony() { return horseIcon(); }
  function provisions() { // 糧秣
    const px = blank();
    frame(px, 3, 8, 10, 5, WD, O);
    rect(px, 3, 6, 10, 2, WDd);
    return px;
  }
  function refuge() { return cottage(); }
  function ringleader() { // 元締め
    const px = blank();
    frame(px, 4, 3, 8, 10, RF, O);
    lineThick(px, 10, 6, 14, 2, MEd, 1);
    return px;
  }
  function riverboat() { // 川舟
    const px = blank();
    for (let i = 0; i < 4; i++) rect(px, 6 - i, 11 + i, 4 + i * 2, 1, WD);
    lineThick(px, 8, 11, 8, 3, WDd, 1);
    return px;
  }
  function scrapiron() { // くず鉄
    const px = blank();
    rect(px, 3, 7, 4, 4, ME); rect(px, 8, 5, 4, 6, MEd); rect(px, 12, 8, 3, 4, ME);
    return px;
  }
  function sled() { // 馬そり
    const px = blank();
    rect(px, 3, 9, 10, 4, WD);
    lineThick(px, 2, 13, 5, 9, WDd, 1); lineThick(px, 14, 13, 11, 9, WDd, 1);
    return px;
  }
  function snowvillage() { // 雪の里
    const px = blank();
    roof(px, 0, 6, 6, 3, WL, WL, WLd); frame(px, 1, 9, 4, 4, WL, O);
    roof(px, 9, 3, 6, 5, WL, WL, WLd); frame(px, 10, 8, 4, 6, WL, O);
    return px;
  }
  function stablehand() { // 馬番
    const px = blank();
    frame(px, 3, 5, 6, 8, WD, O);
    for (const y of [7, 10]) lineThick(px, 5, y, 7, y, WDl, 1);
    return px;
  }
  function traveler2() { // 旅の人
    const px = blank();
    circle(px, 8, 6, 2, WL, O, O, O);
    lineThick(px, 8, 8, 8, 13, WLd, 2);
    return px;
  }
  function warder() { // 門衛
    const px = blank();
    frame(px, 4, 3, 8, 11, ME, O);
    rect(px, 7, 5, 2, 5, MEd);
    return px;
  }
  function warhorse() { return horseIcon(); }
  function witchmeet() { // 魔女の寄り合い
    const px = blank();
    circle(px, 8, 8, 6, PU, PUl, PUd, O);
    circle(px, 8, 8, 3, O, O, O, O);
    return px;
  }
  function animalIcon(c, ear) { // ならい（動物）共通: 丸い体と耳
    const px = blank();
    circle(px, 8, 10, 5, c, c, c, O);
    if (ear) circle(px, 5, 6, 2, c, c, c, O);
    return px;
  }
  const w_butterfly = () => { const px = blank(); circle(px, 5, 7, 3, PU, PUl, PU, O); circle(px, 11, 7, 3, PU, PUl, PU, O); lineThick(px, 8, 4, 8, 12, O, 1); return px; };
  const w_camel = () => animalIcon(GOl, true);
  const w_frog = () => animalIcon(GR, false);
  const w_goat = () => animalIcon(WL, true);
  const w_horse = () => horseIcon();
  function w_mole() { // 土竜のならい
    const px = blank();
    circle(px, 8, 10, 5, WDd, WD, WDd, O);
    circle(px, 8, 13, 3, WDd, WDd, WDd, O);
    return px;
  }
  const w_monkey = () => animalIcon(WDd, true);
  const w_mouse = () => animalIcon(STl, true);
  const w_mule = () => animalIcon(STd, true);
  const w_otter = () => animalIcon(WDl, false);
  function w_owl() { // 梟のならい
    const px = blank();
    circle(px, 8, 8, 5, WDd, WD, WDd, O);
    set(px, 6, 7, GOl); set(px, 10, 7, GOl);
    return px;
  }
  const w_ox = () => animalIcon(STd, true);
  const w_pig = () => animalIcon(RFl, false);
  const w_rat = () => animalIcon(STl, false);
  const w_seal = () => animalIcon(ST, false);
  const w_sheep = () => animalIcon(WL, false);
  const w_squirrel = () => animalIcon(WDl, false);
  function w_turtle() { // 亀のならい
    const px = blank();
    circle(px, 8, 10, 5, GR, GRl, GR, O);
    circle(px, 8, 10, 3, GRl, GRl, GR, O);
    return px;
  }
  function w_worm() { // 蚯蚓のならい
    const px = blank();
    for (let i = 0; i < 5; i++) set(px, 4 + i * 2, 9 + (i % 2), RFl);
    return px;
  }

  // ---- 拡張「プロモ」14 種 ----
  function chapel2() { return abbey(); }
  function darkmarket() { // 闇の市
    const px = blank();
    frame(px, 2, 9, 12, 4, WD, O);
    for (const x of [4, 8, 12]) set(px, x, 7, GOl);
    return px;
  }
  function dismantle() { // 解体
    const px = blank();
    rect(px, 4, 5, 4, 8, ME); rect(px, 9, 3, 4, 10, MEd);
    return px;
  }
  function legate() { // 内通者
    const px = blank();
    frame(px, 4, 5, 8, 6, WL, O);
    circle(px, 2, 9, 2, WL, WL, WL, O);
    circle(px, 14, 9, 2, WL, WL, WL, O);
    return px;
  }
  function fencedvillage() { return village(); }
  function bugyo() { // 奉行
    const px = blank();
    frame(px, 5, 2, 6, 10, RF, O);
    rect(px, 6, 0, 4, 2, GO);
    return px;
  }
  function borderland() { // 境の地
    const px = blank();
    lineThick(px, 0, 10, 16, 6, WDd, 1);
    rect(px, 7, 2, 2, 9, ST);
    return px;
  }
  function nestegg() { // 隠し財布
    const px = blank();
    circle(px, 8, 10, 6, WD, WDl, WDd, O);
    for (const [x, y] of [[5, 8], [9, 9], [11, 7]]) circle(px, x, y, 1, WL, WL, WL, O);
    return px;
  }
  function skipper() { // 船頭
    const px = blank();
    for (let i = 0; i < 4; i++) rect(px, 6 - i, 10 + i, 4 + i * 2, 1, WD);
    lineThick(px, 8, 10, 8, 2, WDd, 1);
    rect(px, 8, 2, 4, 2, RF);
    return px;
  }
  function youngload() { // 若殿
    const px = blank();
    frame(px, 4, 2, 8, 11, RF, O);
    set(px, 8, 1, GOl);
    return px;
  }
  function p_sauna() { // 蒸し風呂／氷の湯
    const px = blank();
    circle(px, 8, 8, 6, WT, WTl, WTd, O);
    for (const [x, y] of [[5, 4], [9, 3], [7, 6]]) set(px, x, y, WL);
    return px;
  }
  function steambath() { // 蒸し風呂
    const px = blank();
    circle(px, 8, 8, 6, RF, RFl, RFd, O);
    return px;
  }
  function icebath() { // 氷の湯
    const px = blank();
    circle(px, 8, 8, 6, WT, WTl, WTd, O);
    return px;
  }
  function e_summon() { // 呼び寄せ
    const px = blank();
    circle(px, 8, 8, 5, PU, PUl, PUd, O);
    for (const [x, y] of [[4, 4], [12, 4], [8, 2]]) set(px, x, y, GOl);
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
    coronet, courser, demesne, guardsman, turnip, renown, smallvillage, chandler, mason, shoer, sideshow, clinic, notions, redo, apprentice, counselor, forerunner, square, farmhand, expo, cornhorn, huntparty, clown, breadmaker, meatseller, wanderer, guildhall, stargazer, funfair, ferry, mugger, duel, goldbag, crown, retinue, hime, steed, diviner, healer, gem, countryside, horsedealer, tourney, collector, reaping,
    potion, transform, vinerack, herbpicker, druggist, mirrorpool, academy, adept, blackcat, arcanestone, clayman, pupil, takeover,
    ruins, ruin_mine, ruin_library, ruin_market, ruin_village, ruin_survivors, shack, tombs, wildestate, booty, lunatic, sellsword, knights, poorhouse, pauper, footman, rover, gleaner, recluse, marketsquare, scholar, lumberroom, waif, arsenal, corpsecart, fief, stronghold, hardware, ravager, parade, rats, scrounger, troubadour, impostor, hideout, ossuary, viscount, forgery, zealot, gravedigger, junkman, psychic, ransack, rework, villain, offering, huntland,
    realmcoin, lad, farmer, catpaw, wreck, wardstone, escort, stonecell, kit, pathguide, copycat, crow, courier, skinflint, harbor, forester, shapeshift, tinkerer, bridgeogre, bigman, mazewood, phantomcity, oldrelic, carriage, raconteur, bogfiend, windfall, vintner, farland, servant, seeker, fighter, paragon, victor, ashigaru, deserter, follower, master, e_soup, e_advance, e_trial, e_keep, e_scouts, e_travelfair, e_bonfire, e_outing, e_ferry, e_plan, e_errand, e_pilgrim, e_soiree, e_nightraid, e_searoute, e_barter, e_secretart, e_practice, e_signpost,
    p_settlers, p_catapult, p_patrician, p_encampment, p_gladiator, colonist, busyvillage, trebuchet, pebbles, notable, emporium, bivouac, spoil, fightman, fortune, castles, chariot, temptress, vegmarket, mechanic, oblation, shrine, villa, archivist, principal, luckycharm, scepter, meetinghall, gardener, hoplite, wildchase, townblock, overking, royalsmith, e_promote, e_dig, e_levy, e_feast, e_marriage, e_rite, e_scorch, e_luck, e_warcry, e_subdue, e_absorb, e_alms2, e_unify, l_canal, l_ring, l_banditden, l_hall, l_bathhouse, l_battleground, l_arcade, l_ruinedtemple, l_fountain, l_donjon, l_maze, l_pass, l_treasury, l_pillar, l_fruitfield, l_palace, l_mound, l_tower, l_gate, l_wall, l_lair, c_humble, c_crumbling, c_small, c_haunted, c_opulent, c_sprawling, c_grand, c_king,
    b_earth, b_field, b_flame, b_forest, b_moon, b_mountain, b_river, b_sea, b_sky, b_sun, b_swamp, b_wind,
    h_omens, h_delusion, h_envy, h_famine, h_fear, h_greed, h_haunting, h_locusts, h_misery, h_plague, h_poverty, h_war,
    s_lost, s_deluded, s_envious, s_miserable, s_twice,
    dimmirror, luckycoin, kid, cursedcoin, wishlamp, grazing, purse,
    wisp, imp2, phantom, wish2, nightwing, z_apprentice, z_mason, z_spy,
    druid, loyaldog, protector, priory, sprite, trailer, fairychild, simpleton, emptytown, goblin,
    firewatch, hiddencave, minstrel, luckyvillage, graveyard, secretcouncil, demonforge, purifier,
    deadcaller, herdsman, sneak, shoemender, tombchamber, hauntedvillage, rookery, figurine,
    phantomhorse, holygrove, bully, doomedhero, bloodsucker, wolfman, nightthief,
    gatekeeper, koban, lackeys, troupe, cargo, trial2, improve, flagbearer, lair2, inventor,
    mountainvillage, backer, kannushi, research, draper, yamauba, recruiter, baton, student, carver,
    clairvoyant, spices, swordsman, treasurer, badguy, a_flag, a_horn, a_key, a_lantern, a_chest,
    j_cathedral, j_citygate, j_pageant, j_sewers, j_starchart, j_exploration, j_marketday, j_silos,
    j_plot, j_academy, j_fleet, j_guildhall, j_piazza, j_roads, j_barracks, j_croprotation,
    j_innovation, j_canal, j_citadel,
    angler, archbishop, beastfair, bountyman, caravan2, commons, corral, evict, falconer, goatkeeper,
    herddog, hoardpile, horsemen, hostel, huntlodge, kiln, livery,
    m_banish, m_bargain, m_delay, m_demand, m_despair, m_enclave, m_enhance, m_gamble, m_invest,
    m_league, m_march, m_populate, m_pursue, m_reap, m_ride, m_seize, m_stampede, m_toil, m_trade, m_transport,
    nightcat, pony, provisions, refuge, ringleader, riverboat, scrapiron, sled, snowvillage,
    stablehand, traveler2, warder, warhorse, witchmeet,
    w_butterfly, w_camel, w_frog, w_goat, w_horse, w_mole, w_monkey, w_mouse, w_mule, w_otter,
    w_owl, w_ox, w_pig, w_rat, w_seal, w_sheep, w_squirrel, w_turtle, w_worm,
    chapel2, darkmarket, dismantle, legate, fencedvillage, bugyo, borderland, nestegg, skipper,
    youngload, p_sauna, steambath, icebath, e_summon,
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
    event: '#8a8f98',
    night: '#2b2f5a',
    landmark: '#5f7f4a',
    project: '#b0682c',
    way: '#5a8fa0',
    boon: '#d8b640',
    hex: '#6a3a7a',
    state: '#7a7a7a',
    artifact: '#8a6a3a',
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
