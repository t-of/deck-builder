'use strict';

// ルール・状態は engine.js（画面・音を持たない）。ここは見た目と入力だけ。
import {
  CARDS, KINGDOM_IDS, newGame, currentPlayer, playCard, playTreasure, playAllTreasures,
  buyCard, endTurn, resolveAttackDiscard, finalResults,
} from './engine.js';

// localStorage はほかのアプリと共有される（同じ t-of.github.io のため）。
// キーは必ず 'deck-builder.' で始める。対局中の状態は保存しないが、見た目（テーマ）は保存する。
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

// ---- 見た目: 'simple'（線と面だけ）/ 'pixel'（RPG 風のドット絵。絵は pixel-cards.js）/ 'card'（トレーディングカード風。絵は card-art.js） ----
const themeBtn = document.getElementById('themeBtn');
const THEMES = ['simple', 'pixel', 'card'];
const THEME_LABEL = { simple: '見た目: シンプル', pixel: '見た目: ドット絵', card: '見た目: カード' };
const THEME_COLOR = { simple: '#2b2320', pixel: '#14162b', card: '#0f2e1e' };
let theme = THEMES.includes(load('theme', 'simple')) ? load('theme', 'simple') : 'simple';
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
  if (game) renderTurn();
});
applyTheme();
if (document.fonts) document.fonts.load(`16px ${PIXEL_FONT}`).then(() => { if (game) renderTurn(); }, () => {});

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

const CARD_ORDER = ['copper', 'silver', 'gold', 'estate', 'duchy', 'province', ...KINGDOM_IDS];

const screens = {
  setup: document.getElementById('setup'),
  pass: document.getElementById('pass'),
  game: document.getElementById('game'),
  choice: document.getElementById('choiceOverlay'),
  attackMoat: document.getElementById('attackMoat'),
  result: document.getElementById('result'),
};
function showScreen(name) {
  for (const [k, node] of Object.entries(screens)) node.hidden = k !== name;
}

let game = null;
let pendingGen = null;
let selected = new Set();

// ---- 人数選び ----
document.getElementById('playercount').addEventListener('click', (e) => {
  const n = e.target.dataset.n;
  if (!n) return;
  game = newGame(Number(n));
  goToPass(() => { showScreen('game'); renderTurn(); });
});

function goToPass(onReady) {
  document.getElementById('passLabel').textContent = `${currentPlayer(game).name}に渡してください`;
  showScreen('pass');
  const btn = document.getElementById('passBtn');
  const handler = () => { btn.removeEventListener('click', handler); onReady(); };
  btn.addEventListener('click', handler, { once: true });
}

// ---- 手番の画面 ----
function renderTurn() {
  const p = currentPlayer(game);
  const t = game.turn;

  const stats = document.getElementById('stats');
  clear(stats);
  stats.appendChild(el('span', { text: `${p.name} ／ アクション ${t.actions} ／ 購入 ${t.buys} ／ 金 ${t.money}` }));
  stats.appendChild(el('span', { class: 'muted', text: `山札 ${p.deck.length}・捨て札 ${p.discard.length}` }));

  const others = document.getElementById('othersRow');
  clear(others);
  game.players.forEach((op, i) => {
    if (i === game.current) return;
    others.appendChild(el('div', { class: 'otherCard', text: `${op.name}：手札 ${op.hand.length}・山 ${op.deck.length}` }));
  });

  const buttons = document.getElementById('turnButtons');
  clear(buttons);
  if (t.phase === 'action') {
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '購入フェイズへ', onclick: () => { game.turn.phase = 'buy'; renderTurn(); } }));
  } else {
    buttons.appendChild(el('button', { class: 'pill', text: '財宝をまとめて出す', onclick: () => { playAllTreasures(game); renderTurn(); } }));
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '手番を終える', onclick: onEndTurn }));
  }

  const playArea = document.getElementById('playArea');
  clear(playArea);
  for (const id of game.playArea) playArea.appendChild(cardNode(id, false));

  const supply = document.getElementById('supply');
  clear(supply);
  for (const id of CARD_ORDER) {
    const count = game.supply[id];
    const card = CARDS[id];
    const buyable = t.phase === 'buy' && count > 0 && t.buys > 0 && t.money >= card.cost;
    supply.appendChild(cardNode(id, buyable, () => { if (buyCard(game, id)) { soundBuy(); renderTurn(); } }, count));
  }

  const hand = document.getElementById('hand');
  clear(hand);
  p.hand.forEach((id) => {
    const card = CARDS[id];
    const playableAction = t.phase === 'action' && t.actions > 0 && card.type.startsWith('action');
    const playableTreasure = t.phase === 'buy' && card.type === 'treasure';
    const onClick = playableAction ? () => startCardEffect(id) : playableTreasure ? () => { playTreasure(game, id); renderTurn(); } : null;
    hand.appendChild(cardNode(id, !!onClick, onClick));
  });

  const log = document.getElementById('log');
  clear(log);
  for (const line of game.log.slice(-4)) log.appendChild(el('p', { text: line }));

  if (game.over) { showResult(); return; }
  if (game.attack) { runAttackQueue(); }
}

// 見た目「カード」の種類の帯・数値の書式（engine.js の desc 文字列を見た目用に整えるだけ。ルールには触らない）
const TYPE_LABEL = { treasure: '財宝', victory: '勝利点', action: 'アクション', 'action-attack': 'アクション－アタック', 'action-reaction': 'アクション－リアクション' };
function descLines(card) {
  if (!card.desc) return [];
  return card.desc.split(/[ 。]/).filter(Boolean).map((text) => ({ text, strong: /^[+]?\d/.test(text) }));
}

function cardNode(id, clickable, onClick, count) {
  const card = CARDS[id];
  // 押せないカードもタップで説明が開けるよう button の disabled にはしない
  const node = el('button', { class: `card${clickable ? ' card--active' : ''}`, 'data-type': card.type });
  if (theme === 'pixel' && window.PixelCards) {
    node.style.borderColor = window.PixelCards.frameColor(card.type);
    const icon = el('span', { class: 'card__icon' });
    const canvas = document.createElement('canvas');
    canvas.width = 32; canvas.height = 32;
    window.PixelCards.draw(canvas.getContext('2d'), id);
    icon.appendChild(canvas);
    node.appendChild(icon);
  } else if (theme === 'card' && window.CardArt) {
    node.classList.add('tcgcard');
    node.appendChild(el('div', { class: 'tcgcard__top' }, [
      el('span', { class: 'tcgcard__cost', text: String(card.cost) }),
      el('span', { class: 'tcgcard__name', text: card.name }),
    ]));
    const art = el('div', { class: 'tcgcard__art' });
    art.innerHTML = window.CardArt.render(id);
    node.appendChild(art);
    node.appendChild(el('div', { class: 'tcgcard__type', text: TYPE_LABEL[card.type] || card.type }));
    const body = el('div', { class: 'tcgcard__body' });
    if (card.points) body.appendChild(el('span', { class: 'tcgcard__stat', text: `${card.points}点` }));
    if (card.value) body.appendChild(el('span', { class: 'tcgcard__stat', text: `${card.value}金` }));
    for (const line of descLines(card)) body.appendChild(el('span', { class: line.strong ? 'tcgcard__line tcgcard__line--strong' : 'tcgcard__line', text: line.text }));
    node.appendChild(body);
    if (count != null) node.appendChild(el('span', { class: 'tcgcard__count', text: `残り${count}` }));
    node.addEventListener('click', () => {
      if (onClick) { soundPlay(); onClick(); } else node.classList.toggle('card--peek');
    });
    return node;
  } else {
    node.appendChild(el('span', { class: 'card__icon' }));
  }
  node.appendChild(el('span', { class: 'card__name', text: card.name }));
  node.appendChild(el('span', { class: 'card__cost', text: `コスト${card.cost}` }));
  if (count != null) node.appendChild(el('span', { class: 'card__count', text: `残り${count}` }));
  if (card.desc) node.appendChild(el('span', { class: 'card__desc', text: card.desc }));
  if (card.points) node.appendChild(el('span', { class: 'card__desc', text: `${card.points}点` }));
  if (card.value) node.appendChild(el('span', { class: 'card__desc', text: `${card.value}金` }));
  node.addEventListener('click', () => {
    if (onClick) { soundPlay(); onClick(); } else node.classList.toggle('card--peek');
  });
  return node;
}

function onEndTurn() {
  soundEnd();
  endTurn(game);
  if (game.over) { showResult(); return; }
  goToPass(() => { showScreen('game'); renderTurn(); });
}

// ---- カード効果の選択（ジェネレータを進める） ----
function startCardEffect(cardId) {
  pendingGen = playCard(game, cardId);
  stepGenerator(pendingGen.next());
}
function stepGenerator(step) {
  if (step.done) { pendingGen = null; renderTurn(); return; }
  showChoice(step.value);
}
function showChoice(req) {
  selected = new Set();
  showScreen('choice');
  document.getElementById('choiceLabel').textContent = req.purpose;
  const grid = document.getElementById('choiceGrid');
  clear(grid);
  const confirm = document.getElementById('choiceConfirm');

  if (req.type === 'select-supply') {
    for (const id of req.options) {
      grid.appendChild(cardNode(id, true, () => { finishChoice(id); }));
    }
    confirm.hidden = true;
    return;
  }

  // select-hand: options があれば選べる位置を絞る（例: 鉱脈は財宝だけ）
  const p = currentPlayer(game);
  const indices = req.options || p.hand.map((_, i) => i);
  confirm.hidden = false;
  confirm.disabled = selected.size < req.min;
  confirm.onclick = () => finishChoice([...selected]);
  for (const i of indices) {
    const node = cardNode(p.hand[i], true, () => {
      if (selected.has(i)) selected.delete(i);
      else if (selected.size < req.max) selected.add(i);
      node2Update();
    });
    node.dataset.idx = String(i);
    grid.appendChild(node);
  }
  function node2Update() {
    for (const child of grid.children) {
      child.classList.toggle('card--picked', selected.has(Number(child.dataset.idx)));
    }
    confirm.disabled = selected.size < req.min;
    confirm.textContent = `決定（${selected.size}枚）`;
  }
  node2Update();
}
function finishChoice(answer) {
  showScreen('game');
  stepGenerator(pendingGen.next(answer));
}

// ---- 攻撃（傭兵） ----
function runAttackQueue() {
  if (!game.attack || game.attack.queue.length === 0) {
    // 攻撃した人に端末を戻す（最後に攻撃を受けた人に手札を見せない）
    game.attack = null;
    goToPass(renderTurn);
    return;
  }
  const idx = game.attack.queue[0];
  const target = game.players[idx];
  document.getElementById('passLabel').textContent = `${target.name}に渡してください（アタック）`;
  showScreen('pass');
  const btn = document.getElementById('passBtn');
  const handler = () => { btn.removeEventListener('click', handler); showAttackTarget(idx); };
  btn.addEventListener('click', handler, { once: true });
}
function showAttackTarget(idx) {
  const target = game.players[idx];
  const hasMoat = target.hand.includes('moat');
  if (hasMoat) {
    showScreen('attackMoat');
    document.getElementById('attackMoatLabel').textContent = `${target.name}は水濠を持っています。見せてアタックを防ぎますか？`;
    document.getElementById('moatYes').onclick = () => { game.log.push(`${target.name}が水濠を見せて防いだ。`); advanceAttack(); };
    document.getElementById('moatNo').onclick = () => { attackDiscard(idx); };
  } else {
    attackDiscard(idx);
  }
}
function attackDiscard(idx) {
  const target = game.players[idx];
  const need = target.hand.length - 3;
  if (need <= 0) { advanceAttack(); return; }
  selected = new Set();
  showScreen('choice');
  document.getElementById('choiceLabel').textContent = `${target.name}：手札が3枚になるまで捨てる（${need}枚選ぶ）`;
  const grid = document.getElementById('choiceGrid');
  clear(grid);
  const confirm = document.getElementById('choiceConfirm');
  confirm.hidden = false;
  confirm.disabled = true;
  confirm.onclick = () => {
    resolveAttackDiscard(target, [...selected]);
    advanceAttack();
  };
  target.hand.forEach((id, i) => {
    const node = cardNode(id, true, () => {
      if (selected.has(i)) selected.delete(i);
      else if (selected.size < need) selected.add(i);
      for (const child of grid.children) child.classList.toggle('card--picked', selected.has(Number(child.dataset.idx)));
      confirm.disabled = selected.size !== need;
      confirm.textContent = `決定（${selected.size}/${need}）`;
    });
    node.dataset.idx = String(i);
    grid.appendChild(node);
  });
}
function advanceAttack() {
  game.attack.queue.shift();
  showScreen('game');
  runAttackQueue();
}

// ---- 結果 ----
function showResult() {
  showScreen('result');
  const ranking = document.getElementById('ranking');
  clear(ranking);
  for (const r of finalResults(game)) {
    ranking.appendChild(el('li', { text: `${r.name} ${r.score}点（${r.turns}手番）` }));
  }
}
document.getElementById('restartBtn').addEventListener('click', () => {
  game = null;
  showScreen('setup');
});
