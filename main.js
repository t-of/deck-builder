'use strict';

// ルール・状態は engine.js（画面・音を持たない）。カードの定義は cards-*.js。ここは見た目と入力だけ。
import './cards-base.js';
import './cards-intrigue.js';
import './cards-seaside.js';
import './cards-prosperity.js';
import './cards-hinterlands.js';
import './cards-guilds.js';
import './cards-alchemy.js';
import './cards-darkages.js';
import {
  CARDS, SETS, PRESETS, BASIC_IDS, kingdomPool, randomKingdom, styleType, costOf, is,
  newGame, currentPlayer, turnController, playAction, playTreasureGen, playAllTreasures,
  startBuyPhase, canBuy, buyCard, beginTurn, endTurn, spendCoffers, finalResults,
} from './engine.js';

// localStorage はほかのアプリと共有される（同じ t-of.github.io のため）。
// キーは必ず 'deck-builder.' で始める。対局中の状態は保存しないが、設定は保存する。
const STORE = 'deck-builder.';
function load(key, fallback) {
  try {
    const v = localStorage.getItem(STORE + key);
    return v == null ? fallback : JSON.parse(v);
  } catch { return fallback; }
}
function save(key, value) {
  try { localStorage.setItem(STORE + key, JSON.stringify(value)); } catch { /* 保存できなくても遊べる */ }
}

WebAppKit.init({ title: 'deck-builder', text: '財宝・王国カードを買い集めて点を競う、1台を回して遊ぶデッキ構築の試作' });

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js');
}

// ---- 見た目: 'simple'（線と面だけ）/ 'pixel'（RPG 風のドット絵。絵は pixel-cards.js）/ 'card'（トレーディングカード風。絵は art/*.png） ----
const themeBtn = document.getElementById('themeBtn');
const THEMES = ['simple', 'pixel', 'card'];
const THEME_LABEL = { simple: '見た目: シンプル', pixel: '見た目: ドット絵', card: '見た目: カード' };
const THEME_COLOR = { simple: '#2b2320', pixel: '#14162b', card: '#0e2a1c' };
let theme = THEMES.includes(load('theme', 'card')) ? load('theme', 'card') : 'card';
const PIXEL_FONT = "'DotGothic16', monospace";
function applyTheme() {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]').content = THEME_COLOR[theme];
  themeBtn.textContent = THEME_LABEL[theme];
}
themeBtn.addEventListener('click', () => {
  theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
  save('theme', theme);
  applyTheme();
  rerender();
});
applyTheme();
if (document.fonts) document.fonts.load(`16px ${PIXEL_FONT}`).then(() => rerender(), () => {});

function setAudioSession(soundOn) {
  try { if (navigator.audioSession) navigator.audioSession.type = soundOn ? 'playback' : 'auto'; } catch { /* 対応していない */ }
}

// ---- 音（短いビープだけ） ----
let audioCtx = null;
function beep(freq, dur) {
  try {
    if (!audioCtx) { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); setAudioSession(true); }
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.frequency.value = freq;
    osc.type = 'sine';
    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
    osc.connect(gain).connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + dur);
  } catch { /* 音が出せなくても遊べる */ }
}
const soundPlay = () => beep(360, 0.1);
const soundBuy = () => beep(560, 0.14);
const soundEnd = () => beep(220, 0.2);

// ---- DOM 組み立ての小道具 ----
function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'text') node.textContent = v;
    else if (k === 'onclick') node.addEventListener('click', v);
    else if (k === 'class') node.className = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) node.appendChild(c);
  return node;
}
const clear = (node) => { while (node.firstChild) node.removeChild(node.firstChild); };

// 種類の帯の文言（CARDS[id].types から組み立てる）
const TYPE_WORD = { treasure: '財宝', victory: '勝利点', curse: '呪い', action: 'アクション', attack: 'アタック', reaction: 'リアクション' };
const typeLabel = (id) => CARDS[id].types.map((t) => TYPE_WORD[t] || t).join('・');

const screens = {
  setup: document.getElementById('setup'),
  pass: document.getElementById('pass'),
  game: document.getElementById('game'),
  choice: document.getElementById('choiceOverlay'),
  result: document.getElementById('result'),
};
function showScreen(name) {
  for (const [k, node] of Object.entries(screens)) node.hidden = k !== name;
}

let game = null;
let shownPlayer = 0; // 今この端末に見えている人（渡す画面をはさまず勝手に見せない）
let pendingGen = null;   // 今進めているジェネレータ（カード・購入・手番の始め/終わりのどれか）
let pendingDone = null;  // 終わったときに呼ぶ（省略時は backToTurn）
let selected = new Set();

// ---- カードの見た目 ----
// cost を渡さなければ CARDS[id].cost（対局前の画面用）。対局中は costOf(game, id) を渡す。
// badge: 印の数・厄よけなど、右上・左上に小さく出す文言
function cardNode(id, clickable, onClick, count, cost, badge) {
  const card = CARDS[id];
  const type = styleType(id);
  const showCost = cost != null ? cost : card.cost;
  const discounted = showCost !== card.cost;
  const costClass = `card__cost${discounted ? ' card__cost--down' : ''}`;
  const potionText = card.potion ? ` ⚗${card.potion > 1 ? `×${card.potion}` : ''}` : '';
  const node = el('button', { class: `card${clickable ? ' card--active' : ''}`, 'data-type': type });
  if (theme === 'pixel' && window.PixelCards) {
    node.style.borderColor = window.PixelCards.frameColor(type);
    const icon = el('span', { class: 'card__icon' });
    const canvas = document.createElement('canvas');
    canvas.width = 32; canvas.height = 32;
    window.PixelCards.draw(canvas.getContext('2d'), id);
    icon.appendChild(canvas);
    node.appendChild(icon);
  } else if (theme === 'card') {
    node.classList.add('tcgcard');
    node.appendChild(el('div', { class: 'tcgcard__name', text: card.name }));
    const art = el('div', { class: 'tcgcard__art' });
    const img = document.createElement('img');
    img.src = `./art/${id}.png`;
    img.alt = card.name;
    img.onerror = () => { img.remove(); }; // まだ絵がないカードは無地の枠のまま
    art.appendChild(img);
    node.appendChild(art);
    const body = el('div', { class: 'tcgcard__body' });
    const mainClass = card.main.includes('\n') ? 'tcgcard__main tcgcard__main--small' : 'tcgcard__main';
    body.appendChild(el('span', { class: mainClass, text: card.main }));
    if (card.desc) body.appendChild(el('span', { class: 'tcgcard__sub', text: card.desc }));
    node.appendChild(body);
    node.appendChild(el('div', { class: 'tcgcard__bottom' }, [
      el('span', { class: `tcgcard__cost${discounted ? ' tcgcard__cost--down' : ''}`, text: `${showCost}${potionText}` }),
      el('span', { class: 'tcgcard__type', text: typeLabel(id) }),
    ]));
    if (count != null) node.appendChild(el('span', { class: 'tcgcard__count', text: `残り${count}` }));
    if (badge) node.appendChild(el('span', { class: 'tcgcard__embargo', text: badge }));
    node.addEventListener('click', () => {
      if (onClick) { soundPlay(); onClick(); } else node.classList.toggle('card--peek');
    });
    return node;
  } else {
    node.appendChild(el('span', { class: 'card__icon' }));
  }
  node.appendChild(el('span', { class: 'card__name', text: card.name }));
  node.appendChild(el('span', { class: costClass, text: `コスト${showCost}${potionText}` }));
  if (count != null) node.appendChild(el('span', { class: 'card__count', text: `残り${count}` }));
  if (badge) node.appendChild(el('span', { class: 'card__count', text: badge }));
  if (card.main) node.appendChild(el('span', { class: 'card__desc', text: card.main }));
  if (card.desc) node.appendChild(el('span', { class: 'card__desc', text: card.desc }));
  node.addEventListener('click', () => {
    if (onClick) { soundPlay(); onClick(); } else node.classList.toggle('card--peek');
  });
  return node;
}
// 対局中のカード（コストは costOf で、下がっていれば見た目でわかる。サプライの印・厄よけがあれば添える）。
// id が重なった山（game.stacks）なら、絵・名前・文言は一番上の札のものを出す（買う・残り枚数は id のまま）
function gcNode(id, clickable, onClick, count) {
  if (!game) return cardNode(id, clickable, onClick, count);
  const stack = game.stacks && game.stacks[id];
  const displayId = stack && stack.length ? stack.at(-1) : id;
  const badges = [];
  if (game.embargo[id]) badges.push(`印×${game.embargo[id]}`);
  if (game.bane === id) badges.push('厄よけ');
  return cardNode(displayId, clickable, onClick, count, costOf(game, id), badges.join(' ') || null);
}
// カードの id を名前・枚数でまとめた短い文言（マットの中身など）
function counts(ids) {
  const m = new Map();
  for (const id of ids) m.set(id, (m.get(id) || 0) + 1);
  return [...m.entries()].map(([id, n]) => `${CARDS[id].name}${n > 1 ? `×${n}` : ''}`).join('・');
}

function rerender() {
  if (!game) { renderSetup(); return; }
  if (game.over) { showResult(); return; }
  if (screens.game.hidden === false) renderTurn();
}

// ==================================================================
// 人数・カードの組を選ぶ画面
// ==================================================================
const ALL_KINGDOM = kingdomPool();
function validKingdom(arr) {
  return Array.isArray(arr) && arr.length === 10 && new Set(arr).size === 10 && arr.every((id) => ALL_KINGDOM.includes(id)) ? arr : null;
}

let players = [2, 3, 4].includes(load('players', 2)) ? load('players', 2) : 2;
let mode = ['preset', 'random', 'custom'].includes(load('mode', 'preset')) ? load('mode', 'preset') : 'preset';
let presetId = PRESETS.some((p) => p.id === load('presetId', null)) ? load('presetId', null) : (PRESETS[0] && PRESETS[0].id);
let selectedSets = new Set((Array.isArray(load('sets', null)) ? load('sets', null) : []).filter((id) => SETS.some((s) => s.id === id)));
if (!selectedSets.size) for (const s of SETS) selectedSets.add(s.id);
let customPicked = (Array.isArray(load('custom', null)) ? load('custom', null) : []).filter((id) => ALL_KINGDOM.includes(id)).slice(0, 10);
let kingdom = validKingdom(load('kingdom', null)) || (PRESETS[0] ? [...PRESETS[0].cards] : randomKingdom(ALL_KINGDOM));

function persistSetup() {
  save('players', players);
  save('mode', mode);
  save('presetId', presetId);
  save('sets', [...selectedSets]);
  save('custom', customPicked);
  save('kingdom', kingdom);
}

function activeKingdom() {
  return mode === 'custom' ? (customPicked.length === 10 ? customPicked : null) : kingdom;
}

function renderSetup() {
  showScreen('setup');

  const countBox = document.getElementById('playercount');
  for (const btn of countBox.children) btn.classList.toggle('pill--accent', Number(btn.dataset.n) === players);

  const tabs = document.getElementById('modeTabs');
  for (const btn of tabs.children) btn.classList.toggle('pill--accent', btn.dataset.mode === mode);

  const pane = document.getElementById('modePane');
  clear(pane);
  if (mode === 'preset') pane.appendChild(renderPresetPane());
  else if (mode === 'random') pane.appendChild(renderRandomPane());
  else pane.appendChild(renderCustomPane());

  const preview = document.getElementById('kingdomPreview');
  clear(preview);
  const list = mode === 'custom' ? customPicked : kingdom;
  for (const id of list) preview.appendChild(cardNode(id, false));
  document.getElementById('previewLabel').textContent = mode === 'custom'
    ? `選んだカード（${customPicked.length}/10・タップで説明）`
    : '選ばれた10種（タップで説明）';

  const startBtn = document.getElementById('startBtn');
  startBtn.disabled = !activeKingdom();
}

function renderPresetPane() {
  const box = el('div', { class: 'setupSection' });
  for (const set of SETS) {
    const group = el('div', { class: 'presetGroup' }, [el('h3', { text: set.name })]);
    const row = el('div', { class: 'tabs' });
    for (const pr of PRESETS.filter((p) => p.set === set.id)) {
      row.appendChild(el('button', {
        class: `pill${presetId === pr.id ? ' pill--accent' : ''}`,
        text: pr.name,
        onclick: () => { presetId = pr.id; kingdom = [...pr.cards]; persistSetup(); renderSetup(); },
      }));
    }
    group.appendChild(row);
    box.appendChild(group);
  }
  return box;
}

function renderRandomPane() {
  const box = el('div', { class: 'setupSection' });
  const row = el('div', { class: 'chipRow' });
  for (const set of SETS) {
    row.appendChild(el('button', {
      class: `chip${selectedSets.has(set.id) ? ' chip--active' : ''}`,
      text: set.name,
      onclick: () => {
        if (selectedSets.has(set.id)) { if (selectedSets.size > 1) selectedSets.delete(set.id); }
        else selectedSets.add(set.id);
        reroll();
      },
    }));
  }
  box.appendChild(row);
  box.appendChild(el('button', { class: 'pill pill--accent', text: '引き直し', onclick: reroll }));
  return box;
}
function reroll() {
  const pool = kingdomPool([...selectedSets]);
  kingdom = randomKingdom(pool.length >= 10 ? pool : ALL_KINGDOM);
  persistSetup();
  renderSetup();
}

function renderCustomPane() {
  const box = el('div', { class: 'setupSection' });
  const grid = el('div', { class: 'customGrid' });
  for (const id of ALL_KINGDOM) {
    const picked = customPicked.includes(id);
    const node = cardNode(id, true, () => {
      if (picked) customPicked = customPicked.filter((x) => x !== id);
      else if (customPicked.length < 10) customPicked.push(id);
      persistSetup();
      renderSetup();
    });
    node.classList.toggle('card--picked', picked);
    grid.appendChild(node);
  }
  box.appendChild(grid);
  return box;
}

document.getElementById('playercount').addEventListener('click', (e) => {
  const n = e.target.dataset.n;
  if (!n) return;
  players = Number(n);
  persistSetup();
  renderSetup();
});
document.getElementById('modeTabs').addEventListener('click', (e) => {
  const m = e.target.dataset.mode;
  if (!m) return;
  mode = m;
  persistSetup();
  renderSetup();
});
document.getElementById('startBtn').addEventListener('click', () => {
  const k = activeKingdom();
  if (!k) return;
  kingdom = k;
  persistSetup();
  game = newGame(players, kingdom);
  startTurnPass();
});

// ==================================================================
// 手番を渡す画面（今この端末を見ている人と、答える人が違うときにはさむ）
// ==================================================================
function goToPass(pi, onReady) {
  document.getElementById('passLabel').textContent = `${game.players[pi].name}に渡してください`;
  showScreen('pass');
  const btn = document.getElementById('passBtn');
  const handler = () => { btn.removeEventListener('click', handler); onReady(); };
  btn.addEventListener('click', handler, { once: true });
}
function startTurnPass() {
  const pi = turnController(game);
  goToPass(pi, () => { shownPlayer = pi; run(beginTurn(game)); });
}

// ==================================================================
// 手番の画面
// ==================================================================
function renderTurn() {
  const p = currentPlayer(game);
  const t = game.turn;

  const stats = document.getElementById('stats');
  clear(stats);
  const vpText = p.tokens.vp > 0 ? ` ／ 勝利点トークン ${p.tokens.vp}` : '';
  const cofText = p.tokens.coffers > 0 ? ` ／ 財源 ${p.tokens.coffers}` : '';
  const potText = t.potions > 0 ? ` ／ 霊薬 ${t.potions}` : '';
  stats.appendChild(el('span', { text: `${p.name} ／ アクション ${t.actions} ／ 購入 ${t.buys} ／ 金 ${t.money}${vpText}${cofText}${potText}` }));
  stats.appendChild(el('span', { class: 'muted', text: `山札 ${p.deck.length}・捨て札 ${p.discard.length}` }));
  if (game.controller != null) stats.appendChild(el('span', { class: 'muted', text: `${game.players[game.controller].name}が操作中` }));

  document.getElementById('trashLabel').textContent = `廃棄置き場 ${game.trash.length} 枚`;

  const others = document.getElementById('othersRow');
  clear(others);
  game.players.forEach((op, i) => {
    if (i === game.current) return;
    const bits = [`手札 ${op.hand.length}`, `山 ${op.deck.length}`];
    if (op.tokens.vp > 0) bits.push(`勝利点 ${op.tokens.vp}`);
    if (op.tokens.coffers > 0) bits.push(`財源 ${op.tokens.coffers}`);
    for (const [name, ids] of Object.entries(op.mats)) if (ids.length) bits.push(`${name} ${ids.length}枚`);
    others.appendChild(el('div', { class: 'otherCard', text: `${op.name}：${bits.join('・')}` }));
  });

  const buttons = document.getElementById('turnButtons');
  clear(buttons);
  if (t.phase === 'action') {
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '購入フェイズへ', onclick: () => { startBuyPhase(game); renderTurn(); } }));
  } else {
    buttons.appendChild(el('button', { class: 'pill', text: '財宝をまとめて出す', onclick: () => { playAllTreasures(game); renderTurn(); } }));
    if (p.tokens.coffers > 0) {
      buttons.appendChild(el('button', { class: 'pill', text: `財源を使う（残り${p.tokens.coffers}）`, onclick: () => { spendCoffers(game, 1); renderTurn(); } }));
    }
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '手番を終える', onclick: onEndTurn }));
  }

  const playArea = document.getElementById('playArea');
  clear(playArea);
  for (const id of [...p.inPlay, ...game.playArea]) playArea.appendChild(gcNode(id, false));

  // 自分のマットは中身を、手番を終えれば相手にも代わるので隠す必要はない
  const mats = document.getElementById('matsRow');
  clear(mats);
  for (const [name, ids] of Object.entries(p.mats)) {
    if (ids.length) mats.appendChild(el('div', { class: 'otherCard', text: `${name}：${counts(ids)}` }));
  }

  const supply = document.getElementById('supply');
  clear(supply);
  // 基本カード（銅〜災い、あれば白金・新天地）を決まった並びで先に、そのあと王国カード。
  // がれきの山のように王国の外から増える山は、最後にまとめて出す
  const known = new Set([...BASIC_IDS, ...game.kingdom]);
  const supplyOrder = [
    ...BASIC_IDS.filter((id) => game.supply[id] != null),
    ...game.kingdom.filter((id) => game.supply[id] != null),
    ...Object.keys(game.supply).filter((id) => !known.has(id)),
  ];
  for (const id of supplyOrder) {
    const count = game.supply[id];
    const buyable = canBuy(game, id);
    supply.appendChild(gcNode(id, buyable, () => run(buyCard(game, id), (ok) => { if (ok) soundBuy(); backToTurn(); }), count));
  }

  // サプライ外の山（褒賞・賞品など）。買えない、タップで説明だけ
  const nonSupplyIds = Object.keys(game.nonSupply).filter((id) => game.nonSupply[id] > 0);
  document.getElementById('nonSupplyLabel').hidden = nonSupplyIds.length === 0;
  const nonSupply = document.getElementById('nonSupply');
  clear(nonSupply);
  for (const id of nonSupplyIds) nonSupply.appendChild(gcNode(id, false, null, game.nonSupply[id]));

  const hand = document.getElementById('hand');
  clear(hand);
  p.hand.forEach((id) => {
    const playableAction = t.phase === 'action' && t.actions > 0 && is(id, 'action');
    const playableTreasure = t.phase === 'buy' && is(id, 'treasure');
    const onClick = playableAction ? () => run(playAction(game, id))
      : playableTreasure ? () => run(playTreasureGen(game, id))
      : null;
    hand.appendChild(gcNode(id, !!onClick, onClick));
  });

  const log = document.getElementById('log');
  clear(log);
  for (const line of game.log.slice(-4)) log.appendChild(el('p', { text: line }));
}

function onEndTurn() {
  soundEnd();
  run(endTurn(game), () => {
    if (game.over) { showResult(); return; }
    startTurnPass();
  });
}

// ---- ジェネレータを進める（カード・購入・手番の始め/終わりのどこからでも同じように使う） ----
// onDone(戻り値) は省略すると backToTurn。問いが出れば showQuestion で答えを待つ
function run(gen, onDone) {
  pendingGen = gen;
  pendingDone = onDone || null;
  step(gen.next());
}
function step(result) {
  if (result.done) {
    const done = pendingDone;
    pendingGen = null; pendingDone = null;
    if (done) done(result.value); else backToTurn();
    return;
  }
  showQuestion(result.value);
}
// 手番の人に画面を戻す（他の人の手札を手番の人に見せない）
function backToTurn() {
  if (game.over) { showResult(); return; }
  const pi = turnController(game);
  if (shownPlayer !== pi) { goToPass(pi, () => { shownPlayer = pi; showScreen('game'); renderTurn(); }); return; }
  showScreen('game');
  renderTurn();
}

// 問いに答える（4 種類すべてここでまとめる。あとで CPU の席を足すときは、ここで CPU に答えさせる）
function showQuestion(q) {
  if (q.player !== shownPlayer) { goToPass(q.player, () => { shownPlayer = q.player; renderQuestion(q); }); return; }
  renderQuestion(q);
}
function renderQuestion(q) {
  selected = new Set();
  showScreen('choice');
  document.getElementById('choiceLabel').textContent = q.purpose;
  const grid = document.getElementById('choiceGrid');
  clear(grid);
  const buttonsBox = document.getElementById('choiceButtons');
  clear(buttonsBox);
  const confirm = document.getElementById('choiceConfirm');
  confirm.hidden = true;
  confirm.onclick = null;

  if (q.type === 'supply') {
    for (const id of q.options) grid.appendChild(gcNode(id, true, () => answer(id)));
    if (q.optional) buttonsBox.appendChild(el('button', { class: 'pill', text: '獲得しない', onclick: () => answer(null) }));
    return;
  }
  if (q.type === 'choose') {
    for (const id of (q.cards || [])) grid.appendChild(gcNode(id, false));
    for (const c of q.choices) buttonsBox.appendChild(el('button', { class: 'pill pill--accent', text: c.label, onclick: () => answer(c.value) }));
    return;
  }
  // hand: q.owner の手札のうち options の位置だけ選べる（答える人は q.player）／cards: 見せ札から min〜max 枚選ぶ
  const isHand = q.type === 'hand';
  const player = game.players[q.owner];
  const positions = isHand ? q.options : q.cards.map((_, i) => i);
  const idOf = (pos) => (isHand ? player.hand[pos] : q.cards[pos]);
  confirm.hidden = false;
  confirm.onclick = () => answer([...selected]);
  for (const pos of positions) {
    const node = gcNode(idOf(pos), true, () => {
      if (selected.has(pos)) selected.delete(pos);
      else if (selected.size < q.max) selected.add(pos);
      updatePicked();
    });
    node.dataset.pos = String(pos);
    grid.appendChild(node);
  }
  function updatePicked() {
    for (const child of grid.children) child.classList.toggle('card--picked', selected.has(Number(child.dataset.pos)));
    confirm.disabled = selected.size < q.min;
    confirm.textContent = `決定（${selected.size}/${q.max}）`;
  }
  updatePicked();
}
function answer(value) {
  step(pendingGen.next(value));
}

// ==================================================================
// 結果
// ==================================================================
function showResult() {
  showScreen('result');
  const ranking = document.getElementById('ranking');
  clear(ranking);
  for (const r of finalResults(game)) {
    const vp = game.players[r.index].tokens.vp;
    const vpText = vp > 0 ? `・うち勝利点トークン ${vp}` : '';
    ranking.appendChild(el('li', { text: `${r.name} ${r.score}点（${r.turns}手番${vpText}）` }));
  }
}
document.getElementById('restartBtn').addEventListener('click', () => {
  game = null;
  showScreen('setup');
  renderSetup();
});

renderSetup();
