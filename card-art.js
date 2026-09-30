// TCG 風テーマの絵。ドットではなくベクター（インライン SVG）。
// pixel-cards.js と同じ考え方だが、こちらは図形パーツを組んだ 120×120 の SVG 文字列を返す。
// main.js は CardArt.render(id) を呼び、返ってきた <svg>...</svg> を innerHTML に入れるだけ。
// グラデーションの id は呼ぶたびに変わる連番を付け、同じカードが画面に何枚あっても衝突しない。
(function (g) {
  let uid = 0;

  function defs(p, list) {
    return `<defs>${list.map((d) => d(p)).join('')}</defs>`;
  }
  const lin = (name, x1, y1, x2, y2, stops) => (p) =>
    `<linearGradient id="${p}${name}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}">${
      stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</linearGradient>`;
  const rad = (name, cx, cy, r, stops) => (p) =>
    `<radialGradient id="${p}${name}" cx="${cx}" cy="${cy}" r="${r}">${
      stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</radialGradient>`;
  const shadow = (name) => (p) =>
    `<filter id="${p}${name}" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.35"/>
    </filter>`;

  // ---- 財宝: コイン。段（銅1枚・銀2枚・金3枚）で価値を見せる ----
  function coin(topColor, midColor, edgeColor, tier) {
    const p = `c${uid++}_`;
    const positions = tier === 1 ? [[60, 68]] : tier === 2 ? [[46, 70], [72, 58]] : [[38, 76], [64, 68], [82, 48]];
    const one = (cx, cy, r) => `
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="${edgeColor}"/>
      <circle cx="${cx}" cy="${cy - 2}" r="${r - 4}" fill="url(#${p}face)"/>
      <circle cx="${cx}" cy="${cy - 2}" r="${r - 4}" fill="none" stroke="${edgeColor}" stroke-width="1.5" opacity="0.6"/>
      <text x="${cx}" y="${cy + 3}" font-size="${r * 0.9}" text-anchor="middle" fill="${edgeColor}" opacity="0.85" font-weight="700">$</text>`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [rad('face', 0.35, 0.3, 0.9, [[0, topColor], [0.6, midColor], [1, edgeColor]]), shadow('shadow')])}
      ${positions.map(([x, y]) => one(x, y, 26)).join('')}
    </svg>`;
  }

  // ---- 勝利点: 建物。だんだん立派に ----
  function cottage() { // 小屋: 屋根ひとつ・窓ひとつ
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('roof', 0, 0, 0, 1, [[0, '#e07a52'], [1, '#a8442a']]), lin('wall', 0, 0, 0, 1, [[0, '#f2e6c8'], [1, '#cdb98a']]), shadow('shadow')])}
      <polygon points="20,58 60,26 100,58" fill="url(#${p}roof)" stroke="#5c2a18" stroke-width="2"/>
      <rect x="30" y="58" width="60" height="42" fill="url(#${p}wall)" stroke="#5c2a18" stroke-width="2"/>
      <rect x="52" y="76" width="16" height="24" fill="#7a4a1e"/>
      <rect x="38" y="66" width="12" height="12" fill="#8fb8d8" stroke="#5c2a18" stroke-width="1.5"/>
    </svg>`;
  }
  function manor() { // 荘園: 屋根ふたつ・煙突
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('roof', 0, 0, 0, 1, [[0, '#5c6a8c'], [1, '#2f3a58']]), lin('wall', 0, 0, 0, 1, [[0, '#e8e2d0'], [1, '#b7ac8e']]), shadow('shadow')])}
      <rect x="78" y="18" width="8" height="16" fill="#6a5a48"/>
      <polygon points="14,56 62,20 110,56" fill="url(#${p}roof)" stroke="#1c2338" stroke-width="2"/>
      <rect x="24" y="56" width="72" height="44" fill="url(#${p}wall)" stroke="#1c2338" stroke-width="2"/>
      <rect x="54" y="76" width="16" height="24" fill="#5a4a34"/>
      <rect x="32" y="66" width="12" height="12" fill="#8fb8d8" stroke="#1c2338" stroke-width="1.5"/>
      <rect x="76" y="66" width="12" height="12" fill="#8fb8d8" stroke="#1c2338" stroke-width="1.5"/>
    </svg>`;
  }
  function castle() { // 領地: 塔ふたつ・旗・大きな門
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('stone', 0, 0, 0, 1, [[0, '#c9ccd6'], [1, '#8b8f9c']]), lin('flag', 0, 0, 1, 0, [[0, '#d94a3a'], [1, '#a8281c']]), shadow('shadow')])}
      <rect x="14" y="40" width="20" height="60" fill="url(#${p}stone)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="86" y="40" width="20" height="60" fill="url(#${p}stone)" stroke="#3a3d46" stroke-width="2"/>
      <polygon points="14,40 24,26 34,40" fill="#7a3028"/>
      <polygon points="86,40 96,26 106,40" fill="#7a3028"/>
      <rect x="32" y="30" width="56" height="70" fill="url(#${p}stone)" stroke="#3a3d46" stroke-width="2"/>
      <path d="M52 100 v-26 a8 8 0 0 1 16 0 v26 z" fill="#3a3d46"/>
      <line x1="60" y1="12" x2="60" y2="30" stroke="#3a3d46" stroke-width="2"/>
      <polygon points="60,12 80,18 60,24" fill="url(#${p}flag)"/>
      <rect x="40" y="42" width="10" height="10" fill="#1c2029"/>
      <rect x="70" y="42" width="10" height="10" fill="#1c2029"/>
    </svg>`;
  }

  // ---- アクション類 ----
  function warehouse() { // 倉庫: 木箱と樽
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('box', 0, 0, 1, 1, [[0, '#c08a4a'], [1, '#8a5a24']]), lin('barrel', 0, 0, 1, 1, [[0, '#b57a3a'], [1, '#7a4c1e']]), shadow('shadow')])}
      <rect x="16" y="52" width="42" height="42" fill="url(#${p}box)" stroke="#4a2e14" stroke-width="2"/>
      <line x1="16" y1="73" x2="58" y2="73" stroke="#4a2e14" stroke-width="2"/>
      <line x1="37" y1="52" x2="37" y2="94" stroke="#4a2e14" stroke-width="2"/>
      <ellipse cx="86" cy="42" rx="16" ry="7" fill="#6a4420"/>
      <path d="M70 42 q0 44 0 44 q0 10 16 10 q16 0 16 -10 q0 0 0 -44" fill="url(#${p}barrel)" stroke="#4a2e14" stroke-width="2"/>
      <line x1="70" y1="58" x2="102" y2="58" stroke="#4a2e14" stroke-width="2"/>
      <line x1="70" y1="76" x2="102" y2="76" stroke="#4a2e14" stroke-width="2"/>
    </svg>`;
  }
  function moat() { // 水濠: 城壁と堀の水
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('wall', 0, 0, 0, 1, [[0, '#aab0bc'], [1, '#787e8c']]), lin('water', 0, 0, 0, 1, [[0, '#5a8cd8'], [1, '#2c4c9c']]), shadow('shadow')])}
      <rect x="10" y="30" width="100" height="30" fill="url(#${p}wall)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="14" y="18" width="12" height="12" fill="url(#${p}wall)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="40" y="18" width="12" height="12" fill="url(#${p}wall)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="66" y="18" width="12" height="12" fill="url(#${p}wall)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="92" y="18" width="12" height="12" fill="url(#${p}wall)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="10" y="60" width="100" height="40" fill="url(#${p}water)"/>
      <path d="M10 68 q10 -6 20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="#8fc0f0" stroke-width="3" opacity="0.7"/>
      <path d="M10 82 q10 -6 20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="#8fc0f0" stroke-width="3" opacity="0.5"/>
    </svg>`;
  }
  function moneylender() { // 両替商: 天秤と硬貨
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('metal', 0, 0, 0, 1, [[0, '#e8d090'], [1, '#a8822c']]), shadow('shadow')])}
      <rect x="56" y="14" width="8" height="70" fill="url(#${p}metal)"/>
      <rect x="28" y="80" width="64" height="10" fill="url(#${p}metal)" rx="2"/>
      <line x1="20" y1="30" x2="100" y2="30" stroke="url(#${p}metal)" stroke-width="4"/>
      <line x1="20" y1="30" x2="20" y2="52" stroke="#4a3a14" stroke-width="2"/>
      <line x1="100" y1="30" x2="100" y2="52" stroke="#4a3a14" stroke-width="2"/>
      <path d="M8 52 a12 10 0 0 0 24 0 z" fill="#e8b83a" stroke="#4a3a14" stroke-width="1.5"/>
      <path d="M88 52 a12 10 0 0 0 24 0 z" fill="#c9ccd1" stroke="#4a3a14" stroke-width="1.5"/>
      <circle cx="60" cy="18" r="8" fill="url(#${p}metal)" stroke="#4a3a14" stroke-width="1.5"/>
    </svg>`;
  }
  function village() { // 集落: 家並み
    const p = `c${uid++}_`;
    const house = (x, s, roof, wall) => `
      <polygon points="${x},${58 - s * 0.3} ${x + s},${34 - s * 0.5} ${x + s * 2},${58 - s * 0.3}" fill="${roof}" stroke="#3a2a18" stroke-width="1.5"/>
      <rect x="${x + s * 0.15}" y="${58 - s * 0.3}" width="${s * 1.7}" height="${s * 1.2}" fill="${wall}" stroke="#3a2a18" stroke-width="1.5"/>`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [shadow('shadow')])}
      ${house(6, 24, '#c8503c', '#e8dcc0')}
      ${house(42, 30, '#b8452f', '#efe4c8')}
      ${house(84, 22, '#a8442a', '#e0d4b4')}
    </svg>`;
  }
  function workshop() { // 作業場: 金槌と作業台
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('wood', 0, 0, 1, 0, [[0, '#a8703a'], [1, '#7a4c1e']]), lin('head', 0, 0, 1, 1, [[0, '#c7ccd4'], [1, '#787e8c']]), shadow('shadow')])}
      <rect x="14" y="82" width="92" height="10" fill="url(#${p}wood)" stroke="#3a2410" stroke-width="2"/>
      <rect x="24" y="92" width="8" height="16" fill="#5a3a1c"/>
      <rect x="88" y="92" width="8" height="16" fill="#5a3a1c"/>
      <g transform="rotate(-32 70 40)">
        <rect x="60" y="20" width="20" height="16" fill="url(#${p}head)" stroke="#3a3d46" stroke-width="2"/>
        <rect x="66" y="34" width="8" height="46" fill="url(#${p}wood)" stroke="#3a2410" stroke-width="2"/>
      </g>
      <circle cx="34" cy="86" r="2.5" fill="#3a3d46"/>
      <circle cx="46" cy="86" r="2.5" fill="#3a3d46"/>
    </svg>`;
  }
  function mercenary() { // 傭兵: 剣と兜
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('blade', 0, 0, 1, 0, [[0, '#e8ecf2'], [1, '#9aa0ac']]), lin('helm', 0, 0, 0, 1, [[0, '#b8bcc6'], [1, '#787e8c']]), shadow('shadow')])}
      <polygon points="42,16 50,16 56,74 36,74" fill="url(#${p}blade)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="30" y="74" width="32" height="8" fill="#7a4c1e" stroke="#3a2410" stroke-width="1.5"/>
      <rect x="42" y="82" width="8" height="20" fill="#5a3a1c"/>
      <path d="M78 30 a20 20 0 0 1 40 0 q0 20 -20 34 q-20 -14 -20 -34 z" fill="url(#${p}helm)" stroke="#3a3d46" stroke-width="2"/>
      <rect x="90" y="34" width="16" height="6" fill="#3a3d46"/>
      <polygon points="98,10 98,26 88,18" fill="#c8503c"/>
    </svg>`;
  }
  function remodel() { // 建て替え: 足場とこて
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('pole', 0, 0, 1, 0, [[0, '#c8a860'], [1, '#8a6c2c']]), lin('trowel', 0, 0, 1, 1, [[0, '#d4d8de'], [1, '#8a8f9c']]), shadow('shadow')])}
      <g stroke="url(#${p}pole)" stroke-width="4" fill="none">
        <line x1="16" y1="16" x2="16" y2="104"/>
        <line x1="56" y1="10" x2="56" y2="104"/>
        <line x1="96" y1="16" x2="96" y2="104"/>
        <line x1="16" y1="36" x2="96" y2="36"/>
        <line x1="16" y1="68" x2="96" y2="68"/>
        <line x1="16" y1="100" x2="96" y2="100"/>
        <line x1="16" y1="36" x2="56" y2="68"/>
        <line x1="56" y1="36" x2="96" y2="68"/>
      </g>
      <path d="M70 16 l20 10 -8 16 -18 -10 z" fill="url(#${p}trowel)" stroke="#4a4e58" stroke-width="1.5"/>
      <line x1="82" y1="42" x2="70" y2="58" stroke="#7a5a2c" stroke-width="4"/>
    </svg>`;
  }
  function smithy() { // 鍛冶場: 金床と火花
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('anvil', 0, 0, 0, 1, [[0, '#7a8090'], [1, '#3a3d46']]), rad('spark', 0.5, 0.5, 0.6, [[0, '#ffe08a'], [0.6, '#f2a83a'], [1, 'rgba(242,168,58,0)']]), shadow('shadow')])}
      <rect x="20" y="88" width="80" height="12" fill="#4a3a24"/>
      <rect x="46" y="72" width="28" height="18" fill="url(#${p}anvil)" stroke="#1c1e24" stroke-width="2"/>
      <path d="M18 60 q0 -14 20 -14 h44 q20 0 20 14 v6 h-84 z" fill="url(#${p}anvil)" stroke="#1c1e24" stroke-width="2"/>
      <circle cx="88" cy="30" r="22" fill="url(#${p}spark)"/>
      <g stroke="#ffcf5c" stroke-width="2">
        <line x1="88" y1="14" x2="88" y2="6"/>
        <line x1="102" y1="20" x2="110" y2="14"/>
        <line x1="104" y1="34" x2="114" y2="34"/>
        <line x1="74" y1="20" x2="66" y2="14"/>
      </g>
    </svg>`;
  }
  function market() { // 露店: 縞の屋根の屋台
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('stripeA', 0, 0, 0, 1, [[0, '#d9503f'], [1, '#a8382a']]), lin('wood', 0, 0, 0, 1, [[0, '#b58244'], [1, '#8a5c26']]), shadow('shadow')])}
      <path d="M10 46 L60 16 L110 46 Z" fill="#efe6d4" stroke="#3a2a18" stroke-width="2"/>
      <g fill="url(#${p}stripeA)">
        <polygon points="16,44 30,44 24,20"/>
        <polygon points="44,44 58,44 60,17"/>
        <polygon points="72,44 86,44 90,20"/>
      </g>
      <rect x="20" y="46" width="80" height="40" fill="url(#${p}wood)" stroke="#3a2a18" stroke-width="2"/>
      <rect x="14" y="86" width="92" height="8" fill="#5a3c1c"/>
      <circle cx="42" cy="66" r="8" fill="#e8b83a" stroke="#5a3c1c" stroke-width="1.5"/>
      <circle cx="66" cy="70" r="7" fill="#c8503c" stroke="#5a3c1c" stroke-width="1.5"/>
      <circle cx="84" cy="64" r="6" fill="#4a8a5c" stroke="#5a3c1c" stroke-width="1.5"/>
    </svg>`;
  }
  function mine() { // 鉱脈: つるはしと鉱石
    const p = `c${uid++}_`;
    return `<svg viewBox="0 0 120 120" filter="url(#${p}shadow)">
      ${defs(p, [lin('head', 0, 0, 1, 1, [[0, '#c7ccd4'], [1, '#787e8c']]), rad('gem', 0.35, 0.3, 0.9, [[0, '#bfe6ff'], [0.6, '#5aa8e0'], [1, '#2c5c9c']]), shadow('shadow')])}
      <g transform="rotate(20 40 60)">
        <rect x="36" y="14" width="8" height="70" fill="#8a5c26" stroke="#3a2410" stroke-width="1.5"/>
        <path d="M14 14 q26 -14 52 0 q-4 10 -26 10 q-22 0 -26 -10 z" fill="url(#${p}head)" stroke="#3a3d46" stroke-width="2"/>
      </g>
      <polygon points="76,60 96,48 112,66 100,96 78,94" fill="url(#${p}gem)" stroke="#1c3c66" stroke-width="2"/>
      <polygon points="76,60 96,48 100,70 78,94" fill="#8fd0ff" opacity="0.5"/>
    </svg>`;
  }

  const BUILDERS = {
    copper: () => coin('#e0a05a', '#b87333', '#6a3d16', 1),
    silver: () => coin('#f2f4f7', '#c9ccd1', '#6f737c', 2),
    gold: () => coin('#fff0b0', '#e8b83a', '#8a641c', 3),
    estate: cottage,
    duchy: manor,
    province: castle,
    warehouse, moat, moneylender, village, workshop, mercenary, remodel, smithy, market, mine,
  };

  function render(id) {
    const build = BUILDERS[id];
    return build ? build() : '<svg viewBox="0 0 120 120"></svg>';
  }

  g.CardArt = { render };
})(typeof window !== 'undefined' ? window : globalThis);
