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
import './cards-adventures.js';
import './cards-empires.js';
import './cards-nocturne.js';
import './cards-renaissance.js';
import './cards-menagerie.js';
import './cards-promo.js';
import './cards-allies.js';
import './cards-plunder.js';
import './cards-risingsun.js';
import {
  CARDS, SETS, PRESETS, BASIC_IDS, kingdomPool, randomKingdom, styleType, costOf, is, pileOf, isLandscape,
  newGame, currentPlayer, turnController, playAction, playTreasureGen, playAllTreasures,
  enterBuyPhase, canBuy, buyCard, beginTurn, endTurn, spendCoffers, payDebt, finalResults, allCards,
  landscapePool, canBuyEvent, buyEvent, enterNightPhase, canPlayNight, playNight, spendVillager,
  canPlayAction, shadowsInDeck, playShadow, isTreasureNow,
} from './engine.js';
// CPU（1台の端末で人の代わりに席に着く）。画面からはこの3つだけ使う
import { LEVELS as CPU_LEVELS, nextMove as cpuNextMove, answer as cpuAnswer, planFor as cpuPlanFor } from './cpu.js';

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

// 前回と比べて「増えた」枚を見分ける（同じ id が複数あるときは、前回より多い分だけ新しいとみなす）。
// ponytail: 札の同一性までは追わず枚数の比較だけ。入れ替わりを完全に当てたいなら id にインスタンス番号を振る必要がある
function newnessMarks(prevIds, curIds) {
  const prevCount = new Map();
  for (const id of prevIds) prevCount.set(id, (prevCount.get(id) || 0) + 1);
  const seen = new Map();
  return curIds.map((id) => {
    const n = (seen.get(id) || 0) + 1;
    seen.set(id, n);
    return n > (prevCount.get(id) || 0);
  });
}

// 種類の帯の文言（CARDS[id].types から組み立てる）
const TYPE_WORD = {
  treasure: '財宝', victory: '勝利点', curse: '呪い', action: 'アクション', attack: 'アタック', reaction: 'リアクション',
  reserve: 'リザーブ', traveller: 'トラベラー', event: 'イベント', duration: '持続',
  night: '夜行', fate: '幸運', doom: '不運', heirloom: '家宝', spirit: '精霊', zombie: '屍', boon: '恵み', hex: '呪詛', state: '状態',
  project: 'プロジェクト', artifact: 'アーティファクト', command: '命令', landmark: 'ランドマーク', way: 'ならい',
  liaison: '連携', shadow: '影', omen: '前兆', prophecy: '予言', trait: '特性', ally: '同盟', loot: '戦利品',
  augur: '占い師', clash: 'いくさ', fort: '砦', odyssey: '旅', townsfolk: '町の衆', wizard: '術者',
  castle: '城', gathering: '集め', knight: '騎士', ruins: 'がれき', shelter: '避難所', looter: '略奪者', reward: '褒賞', prize: '賞品',
};
// マット（p.mats の項目名）の日本語名
const MAT_LABEL = { tavern: '酒場マット', exile: '追放' };
// 他の人にも中身を見せるマット（それ以外は枚数だけ）
const PUBLIC_MATS = ['tavern', 'exile'];

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
let shownPlayer = null; // 今この端末に手札を見せている人（渡す画面をはさまず勝手に見せない。CPU の番では動かさない）
let pendingGen = null;   // 今進めているジェネレータ（カード・購入・手番の始め/終わりのどれか）
let pendingDone = null;  // 終わったときに呼ぶ（省略時は backToTurn）
let selected = new Set();
let prevRender = null; // 直前の renderTurn の手札・場・サプライ・数字（動きを付けるための比較用。新しい対局では null に戻す）

// ---- カードの見た目 ----
// cost を渡さなければ CARDS[id].cost（対局前の画面用）。対局中は costOf(game, id) を渡す。
// badge: 印の数・厄よけなど、右上・左上に小さく出す文言
function cardNode(id, clickable, onClick, count, cost, badge) {
  const card = CARDS[id];
  // styleType はイベント・ランドマークや夜行を知らないので、ここで上書きする
  let type = styleType(id);
  if (card.types.includes('night')) type = 'night';
  else if (isLandscape(id)) type = 'event';
  const showCost = cost != null ? cost : card.cost;
  const discounted = showCost !== card.cost;
  const potionText = card.potion ? ` ⚗${card.potion > 1 ? `×${card.potion}` : ''}` : '';
  const debtText = card.debt ? ` 借${card.debt}` : '';
  const node = el('button', { class: `card tcgcard${clickable ? ' card--active' : ''}`, 'data-type': type });
  const name = el('div', { class: 'tcgcard__name', text: card.name });
  name.style.setProperty('--len', [...card.name].length);
  node.appendChild(name);
  const art = el('div', { class: 'tcgcard__art' });
  const img = document.createElement('img');
  img.src = `./art/${id}.png`;
  img.alt = card.name;
  img.onerror = () => { img.remove(); }; // まだ絵がないカードは無地の枠のまま
  art.appendChild(img);
  node.appendChild(art);
  const body = el('div', { class: 'tcgcard__body' });
  const mainClass = card.main.includes('\n') ? 'tcgcard__main tcgcard__main--small' : 'tcgcard__main';
  const main = el('span', { class: mainClass, text: card.main });
  main.style.setProperty('--w', Math.max(...card.main.split('\n').map(textWidth)));
  body.appendChild(main);
  if (card.desc) body.appendChild(el('span', { class: 'tcgcard__sub', text: card.desc }));
  node.appendChild(body);
  node.appendChild(el('div', { class: 'tcgcard__bottom' }, [
    el('span', { class: `tcgcard__cost${discounted ? ' tcgcard__cost--down' : ''}`, text: `${showCost}${potionText}${debtText}` }),
    el('span', { class: 'tcgcard__type' }, card.types.map((t, i) => el('span', { text: (i ? '・' : '') + (TYPE_WORD[t] || t) }))),
  ]));
  if (count != null) node.appendChild(el('span', { class: 'tcgcard__count', text: `残り${count}` }));
  if (badge) node.appendChild(el('span', { class: 'tcgcard__embargo', text: badge }));
  bindCard(node, onClick);
  return node;
}
// 文言の幅（全角 1、半角 0.55）。小さい札で文字の大きさを幅に合わせるのに使う
const textWidth = (text) => [...text].reduce((w, c) => w + (c.charCodeAt(0) < 0x100 ? 0.55 : 1), 0);
// 押せる札は押すと動き、押せない札は押すと詳しく見る。長押し・右クリックはどちらでも詳しく見る
function bindCard(node, onClick) {
  let timer = null;
  let long = false;
  const stop = () => { clearTimeout(timer); timer = null; };
  node.addEventListener('pointerdown', () => {
    long = false;
    stop();
    timer = setTimeout(() => { long = true; showCardDetail(node); }, 450);
  });
  for (const ev of ['pointerup', 'pointerleave', 'pointercancel']) node.addEventListener(ev, stop);
  node.addEventListener('contextmenu', (e) => { e.preventDefault(); stop(); if (!long) showCardDetail(node); });
  node.addEventListener('click', () => {
    if (long) { long = false; return; }
    if (onClick) { soundPlay(); onClick(); } else showCardDetail(node);
  });
}
// 札を複製して画面の真ん中に大きく出す。どこを押しても閉じる
function showCardDetail(node) {
  if (document.querySelector('.cardDetail')) return;
  const big = node.cloneNode(true);
  big.classList.remove('card--active', 'card--picked');
  big.classList.add('card--peek');
  big.tabIndex = -1;
  const back = el('div', { class: 'cardDetail', role: 'dialog', 'aria-label': 'カードの詳しい説明' }, [big]);
  const close = () => { back.remove(); document.removeEventListener('keydown', onKey); };
  const onKey = (e) => { if (e.key === 'Escape') close(); };
  back.addEventListener('click', close);
  document.addEventListener('keydown', onKey);
  document.body.appendChild(back);
}
// 山に置かれた印（tokens.pile）の文言
const PILE_LABEL = { card: '+1カード', action: '+1アクション', buy: '+1購入', coin: '+1金', cost: '-2コスト', trash: '廃棄' };
// 対局中のカード（コストは costOf で、下がっていれば見た目でわかる。サプライの印・厄よけがあれば添える）。
// id が重なった山（game.stacks）なら、絵・名前・文言は一番上の札のものを出す（買う・残り枚数は id のまま）
function gcNode(id, clickable, onClick, count) {
  if (!game) return cardNode(id, clickable, onClick, count);
  const stack = game.stacks && game.stacks[id];
  const displayId = stack && stack.length ? stack.at(-1) : id;
  const badges = [];
  if (game.embargo[id]) badges.push(`印×${game.embargo[id]}`);
  if (game.bane === id) badges.push('厄よけ');
  if (game.pileVP && game.pileVP[id] > 0) badges.push(`★${game.pileVP[id]}`);
  if (game.pileDebt && game.pileDebt[id] > 0) badges.push(`借${game.pileDebt[id]}`);
  if (game.landmarkVP && game.landmarkVP[id] > 0) badges.push(`★${game.landmarkVP[id]}`);
  if (id === 'darkmarket' && game.blackMarket) badges.push(`闇の市 残り${game.blackMarket.length}枚`);
  // 特性: この山についた特性の名前を小さく出す
  if (game.traits) for (const [tid, pile] of Object.entries(game.traits)) if (pileOf(id) === pile) badges.push(`特性:${CARDS[tid].name}`);
  // 予言: ランドスケープの列で、残りの太陽トークンか「効いている」を出す
  if (is(id, 'prophecy') && game.landscapes.includes(id)) badges.push(game.sun > 0 ? `☀${game.sun}` : '効いている');
  game.players.forEach((pl, i) => {
    for (const [key, pile] of Object.entries(pl.tokens.pile || {})) {
      if (pile === pileOf(id)) badges.push(`${i + 1}人目: ${PILE_LABEL[key] || key}`);
    }
    if ((pl.projects || []).includes(id)) badges.push(`${i + 1}人目`);
  });
  return cardNode(displayId, clickable, onClick, count, costOf(game, id), badges.join(' ') || null);
}
// 札の真ん中に短い札（「購入」など）を付けて目立たせる
function tagCard(node, text) {
  node.classList.add('is-tagged');
  node.appendChild(el('span', { class: 'tcgcard__tag', text }));
  return node;
}
// カードの id を名前・枚数でまとめた短い文言（マットの中身など）
function counts(ids) {
  const m = new Map();
  for (const id of ids) m.set(id, (m.get(id) || 0) + 1);
  return [...m.entries()].map(([id, n]) => `${CARDS[id].name}${n > 1 ? `×${n}` : ''}`).join('・');
}
// 旅の印・-1金/-1カードの印の文言
function tokenBits(p) {
  const bits = [`旅の印:${p.tokens.journey ? '表' : '裏'}`];
  if (p.tokens.minusCoin) bits.push('-1金の印');
  if (p.tokens.minusCard) bits.push('-1カードの印');
  if (p.tokens.debt > 0) bits.push(`借金 ${p.tokens.debt}`);
  if (p.tokens.favors > 0) bits.push(`好意 ${p.tokens.favors}`);
  return bits;
}
// 状態・持っているアーティファクトの文言（席番号 pi）
function ownerBits(g, pi) {
  const p = g.players[pi];
  const bits = p.states.map((id) => CARDS[id].name);
  for (const [id, owner] of Object.entries(g.artifacts || {})) if (owner === pi) bits.push(CARDS[id].name);
  return bits;
}
// 恵み・呪詛の山（残り枚数のボタン。タップで捨て札の一番上の名前と入れ替えて見られる）
function pileButton(label, pile) {
  let peek = false;
  const node = el('button', { class: 'pill', text: `${label} ${pile.deck.length}枚` });
  node.addEventListener('click', () => {
    peek = !peek;
    const top = pile.discard.at(-1);
    node.textContent = peek ? `捨て札: ${top ? CARDS[top].name : 'なし'}` : `${label} ${pile.deck.length}枚`;
  });
  return node;
}

// 影の札が今使えるか（canPlayAction は手札にある札しか見ないので、一時的に手札へ入れて調べる）
function canPlayShadow(id) {
  const p = currentPlayer(game);
  p.hand.push(id);
  const ok = canPlayAction(game, id);
  p.hand.pop();
  return ok;
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
const ALL_LANDSCAPES = landscapePool();
function validKingdom(arr) {
  return Array.isArray(arr) && arr.length === 10 && new Set(arr).size === 10 && arr.every((id) => ALL_KINGDOM.includes(id)) ? arr : null;
}
function validLandscapes(arr) {
  return (Array.isArray(arr) ? arr : []).filter((id) => ALL_LANDSCAPES.includes(id)).slice(0, 2);
}

let players = [2, 3, 4].includes(load('players', 2)) ? load('players', 2) : 2;
// 席: { type: 'human' } か { type: 'cpu', level: CPU_LEVELS の id }。既定は1人目が人、ほかは CPU（ふつう）
function validSeat(s) {
  return s && (s.type === 'human' || (s.type === 'cpu' && CPU_LEVELS.some((l) => l.id === s.level)));
}
let seats = (Array.isArray(load('seats', null)) ? load('seats', null) : []).filter(validSeat);
function ensureSeats() {
  const out = [];
  for (let i = 0; i < players; i++) out.push(seats[i] || (i === 0 ? { type: 'human' } : { type: 'cpu', level: 'normal' }));
  seats = out;
}
ensureSeats();
let spectatorSpeed = ['normal', 'fast'].includes(load('spectatorSpeed', 'normal')) ? load('spectatorSpeed', 'normal') : 'normal';
const humanCount = () => seats.filter((s) => s.type === 'human').length;
const isHumanSeat = (pi) => seats[pi] && seats[pi].type === 'human';
const allCpu = () => humanCount() === 0;
const cpuDelay = () => (allCpu() && spectatorSpeed === 'fast' ? 70 : 350);
const seatName = (s, i) => (s.type === 'human' ? `${i + 1}人目` : `CPU（${CPU_LEVELS.find((l) => l.id === s.level).name}）`);

let mode = ['preset', 'random', 'custom'].includes(load('mode', 'preset')) ? load('mode', 'preset') : 'preset';
let presetId = PRESETS.some((p) => p.id === load('presetId', null)) ? load('presetId', null) : (PRESETS[0] && PRESETS[0].id);
let selectedSets = new Set((Array.isArray(load('sets', null)) ? load('sets', null) : []).filter((id) => SETS.some((s) => s.id === id)));
if (!selectedSets.size) for (const s of SETS) selectedSets.add(s.id);
let customPicked = (Array.isArray(load('custom', null)) ? load('custom', null) : []).filter((id) => ALL_KINGDOM.includes(id)).slice(0, 10);
let kingdom = validKingdom(load('kingdom', null)) || (PRESETS[0] ? [...PRESETS[0].cards] : randomKingdom(ALL_KINGDOM));
// イベントなど（サプライの横に置く札）。おすすめ・おまかせで使う landscapes と、自分で選ぶ用の customLandscapes は別に持つ
let landscapesOn = typeof load('landscapesOn', true) === 'boolean' ? load('landscapesOn', true) : true;
let landscapes = validLandscapes(load('landscapes', null));
if (!load('landscapes', null) && PRESETS[0] && PRESETS[0].landscapes) landscapes = [...PRESETS[0].landscapes];
let customLandscapes = validLandscapes(load('customLandscapes', null));

function persistSetup() {
  save('players', players);
  save('seats', seats);
  save('spectatorSpeed', spectatorSpeed);
  save('mode', mode);
  save('presetId', presetId);
  save('sets', [...selectedSets]);
  save('custom', customPicked);
  save('kingdom', kingdom);
  save('landscapesOn', landscapesOn);
  save('landscapes', landscapes);
  save('customLandscapes', customLandscapes);
}

function activeKingdom() {
  return mode === 'custom' ? (customPicked.length === 10 ? customPicked : null) : kingdom;
}
function activeLandscapes() {
  return mode === 'custom' ? customLandscapes : landscapes;
}

function renderSetup() {
  showScreen('setup');

  const countBox = document.getElementById('playercount');
  for (const btn of countBox.children) btn.classList.toggle('pill--accent', Number(btn.dataset.n) === players);

  renderSeatsBox();
  renderSpeedBox();

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

  const lands = activeLandscapes();
  document.getElementById('landscapePreviewLabel').hidden = lands.length === 0;
  const landPreview = document.getElementById('landscapePreview');
  clear(landPreview);
  for (const id of lands) landPreview.appendChild(gcNode(id, false));

  const startBtn = document.getElementById('startBtn');
  startBtn.disabled = !activeKingdom();
}

// 席ごとに「人」か「CPU（強さ）」を選ぶ
function renderSeatsBox() {
  const box = document.getElementById('seatsBox');
  clear(box);
  for (let i = 0; i < players; i++) {
    const row = el('div', { class: 'seatRow' });
    row.appendChild(el('span', { class: 'seatRow__label', text: `${i + 1}人目` }));
    const chips = el('div', { class: 'chipRow' });
    chips.appendChild(el('button', {
      class: `chip${seats[i].type === 'human' ? ' chip--active' : ''}`,
      text: '人',
      onclick: () => { seats[i] = { type: 'human' }; persistSetup(); renderSetup(); },
    }));
    for (const lv of CPU_LEVELS) {
      const active = seats[i].type === 'cpu' && seats[i].level === lv.id;
      chips.appendChild(el('button', {
        class: `chip${active ? ' chip--active' : ''}`,
        text: `CPU（${lv.name}）`,
        onclick: () => { seats[i] = { type: 'cpu', level: lv.id }; persistSetup(); renderSetup(); },
      }));
    }
    row.appendChild(chips);
    box.appendChild(row);
  }
}
// 全員 CPU のときだけ、観戦の速さを選べる
function renderSpeedBox() {
  const box = document.getElementById('speedBox');
  box.hidden = !allCpu();
  clear(box);
  if (box.hidden) return;
  const row = el('div', { class: 'seatRow' }, [el('span', { class: 'seatRow__label', text: '観戦の速さ' })]);
  const chips = el('div', { class: 'chipRow' });
  for (const [id, label] of [['normal', 'ふつう'], ['fast', '速い']]) {
    chips.appendChild(el('button', {
      class: `chip${spectatorSpeed === id ? ' chip--active' : ''}`,
      text: label,
      onclick: () => { spectatorSpeed = id; persistSetup(); renderSetup(); },
    }));
  }
  row.appendChild(chips);
  box.appendChild(row);
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
        onclick: () => { presetId = pr.id; kingdom = [...pr.cards]; landscapes = pr.landscapes ? [...pr.landscapes] : []; persistSetup(); renderSetup(); },
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
  box.appendChild(el('button', {
    class: `chip${landscapesOn ? ' chip--active' : ''}`,
    text: 'イベントなどを入れる',
    onclick: () => { landscapesOn = !landscapesOn; reroll(); },
  }));
  box.appendChild(el('button', { class: 'pill pill--accent', text: '引き直し', onclick: reroll }));
  return box;
}
function reroll() {
  const pool = kingdomPool([...selectedSets]);
  kingdom = randomKingdom(pool.length >= 10 ? pool : ALL_KINGDOM);
  const lpool = landscapePool([...selectedSets]);
  landscapes = landscapesOn ? randomKingdom(lpool, Math.floor(Math.random() * 3)) : [];
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

  box.appendChild(el('h3', { class: 'sectionLabel', text: `イベントなど（${customLandscapes.length}/2まで・任意）` }));
  const landGrid = el('div', { class: 'customGrid' });
  for (const id of ALL_LANDSCAPES) {
    const picked = customLandscapes.includes(id);
    const node = gcNode(id, true, () => {
      if (picked) customLandscapes = customLandscapes.filter((x) => x !== id);
      else if (customLandscapes.length < 2) customLandscapes.push(id);
      persistSetup();
      renderSetup();
    });
    node.classList.toggle('card--picked', picked);
    landGrid.appendChild(node);
  }
  box.appendChild(landGrid);
  return box;
}

document.getElementById('playercount').addEventListener('click', (e) => {
  const n = e.target.dataset.n;
  if (!n) return;
  players = Number(n);
  ensureSeats();
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
  shownPlayer = null;
  prevRender = null;
  game = newGame(players, kingdom, seats.map(seatName), { landscapes: activeLandscapes() });
  startTurnPass();
});

// ==================================================================
// 手番を渡す画面（今この端末を見ている人と、答える人が違うときにはさむ。人どうしのときだけ出す）
// ==================================================================
function goToPass(pi, onReady) {
  document.getElementById('passLabel').textContent = `${game.players[pi].name}に渡してください`;
  showScreen('pass');
  const btn = document.getElementById('passBtn');
  const handler = () => { btn.removeEventListener('click', handler); onReady(); };
  btn.addEventListener('click', handler, { once: true });
}
// pi が人で、人が2人以上いて、今見せている人と違うときだけ渡す画面をはさむ。CPU の番・人が1人だけのときは素通り
function maybeGoToPass(pi, onReady) {
  if (isHumanSeat(pi) && humanCount() >= 2 && shownPlayer !== pi) { goToPass(pi, () => { shownPlayer = pi; onReady(); }); return; }
  if (isHumanSeat(pi)) shownPlayer = pi;
  onReady();
}
function startTurnPass() {
  const pi = turnController(game);
  maybeGoToPass(pi, () => run(beginTurn(game)));
}

// ==================================================================
// 手番の画面
// ==================================================================
function renderTurn() {
  const p = currentPlayer(game);
  const t = game.turn;
  // 手番を操作する人が CPU のあいだは、押しても何も起きないよう手札・サプライなどを押せなくする
  const humanControls = isHumanSeat(turnController(game));
  document.getElementById('cpuThinking').hidden = true;

  const PHASE_LABEL = { action: 'アクションフェイズ', buy: '購入フェイズ', night: '夜のフェイズ' };
  const phasePill = document.getElementById('phasePill');
  phasePill.textContent = PHASE_LABEL[t.phase] || '';
  phasePill.dataset.phase = t.phase;

  const stats = document.getElementById('stats');
  clear(stats);
  stats.appendChild(el('span', { class: 'hud__name', text: p.name }));
  const medals = el('div', { class: 'medals' });
  // 前回より増えていたら medal--bump を付けて跳ねさせる（reduced-motion では CSS 側で動かさない）
  const medal = (label, n, prevN) => el('span', { class: `medal${prevN != null && n > prevN ? ' medal--bump' : ''}` }, [
    el('span', { class: 'medal__n', text: String(n) }),
    el('span', { class: 'medal__label', text: label }),
  ]);
  const prevNums = prevRender && prevRender.pi === game.current ? prevRender.nums : {};
  medals.appendChild(medal('アクション', t.actions, prevNums.actions));
  medals.appendChild(medal('購入', t.buys, prevNums.buys));
  medals.appendChild(medal('金', t.money, prevNums.money));
  if (p.tokens.vp > 0) medals.appendChild(medal('勝利点', p.tokens.vp));
  if (p.tokens.coffers > 0) medals.appendChild(medal('財源', p.tokens.coffers));
  if (t.potions > 0) medals.appendChild(medal('霊薬', t.potions));
  if (p.tokens.villagers > 0) medals.appendChild(medal('村人', p.tokens.villagers));
  stats.appendChild(medals);
  stats.appendChild(el('span', { class: 'muted', text: `山札 ${p.deck.length}・捨て札 ${p.discard.length}` }));
  stats.appendChild(el('span', { class: 'muted', text: tokenBits(p).join('・') }));
  if (ownerBits(game, game.current).length) stats.appendChild(el('span', { class: 'muted', text: ownerBits(game, game.current).join('・') }));
  if (t.phase === 'buy' && t.noBuy) stats.appendChild(el('span', { class: 'muted', text: 'この手番は買えない' }));
  if (game.controller != null) stats.appendChild(el('span', { class: 'muted', text: `${game.players[game.controller].name}が操作中` }));

  const others = document.getElementById('othersRow');
  clear(others);
  game.players.forEach((op, i) => {
    if (i === game.current) return;
    const bits = [`手札 ${op.hand.length}`, `山 ${op.deck.length}`, ...tokenBits(op), ...ownerBits(game, i)];
    if (op.tokens.vp > 0) bits.push(`勝利点 ${op.tokens.vp}`);
    if (op.tokens.coffers > 0) bits.push(`財源 ${op.tokens.coffers}`);
    if (op.tokens.villagers > 0) bits.push(`村人 ${op.tokens.villagers}`);
    // 酒場マット・追放は他の人のも中身を見せる。ほかのマットは枚数だけ
    for (const [name, ids] of Object.entries(op.mats)) {
      if (!ids.length) continue;
      bits.push(PUBLIC_MATS.includes(name) ? `${MAT_LABEL[name]}：${counts(ids)}` : `${MAT_LABEL[name] || name} ${ids.length}枚`);
    }
    others.appendChild(el('div', { class: 'otherCard', text: `${op.name}：${bits.join('・')}` }));
  });

  const buttons = document.getElementById('turnButtons');
  clear(buttons);
  if (!humanControls) {
    buttons.appendChild(el('span', { class: 'muted', text: `${p.name}の番です` }));
  } else if (t.phase === 'action') {
    if (p.tokens.villagers > 0) {
      buttons.appendChild(el('button', { class: 'pill', text: `村人を使う（残り${p.tokens.villagers}）`, onclick: () => { spendVillager(game); renderTurn(); } }));
    }
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '購入フェイズへ', onclick: () => run(enterBuyPhase(game)) }));
  } else {
    if (t.phase === 'buy') {
      buttons.appendChild(el('button', { class: 'pill', text: '財宝をまとめて出す', onclick: () => { playAllTreasures(game); renderTurn(); } }));
      if (p.tokens.coffers > 0) {
        buttons.appendChild(el('button', { class: 'pill', text: `財源を使う（残り${p.tokens.coffers}）`, onclick: () => { spendCoffers(game, 1); renderTurn(); } }));
      }
      if (p.tokens.debt > 0) {
        buttons.appendChild(el('button', { class: 'pill', text: `借金を返す（残り${p.tokens.debt}）`, onclick: () => { payDebt(game); renderTurn(); } }));
      }
      if (p.hand.some((id) => is(id, 'night'))) {
        buttons.appendChild(el('button', { class: 'pill', text: '夜のフェイズへ', onclick: () => { enterNightPhase(game); renderTurn(); } }));
      }
    }
    buttons.appendChild(el('button', { class: 'pill pill--accent', text: '手番を終える', onclick: onEndTurn }));
  }

  const playArea = document.getElementById('playArea');
  clear(playArea);
  const playIds = [...p.inPlay, ...game.playArea];
  const playNew = newnessMarks(prevRender ? prevRender.play : [], playIds);
  playIds.forEach((id, i) => {
    const node = gcNode(id, false);
    if (playNew[i]) node.classList.add('is-new-play');
    playArea.appendChild(node);
  });
  // この手番に買った札も場に並べ、「購入」の札で見分ける（本当の行き先は捨て札）
  for (const id of t.bought) playArea.appendChild(tagCard(gcNode(id, false), '購入'));

  // 自分のマットは中身を、手番を終えれば相手にも代わるので隠す必要はない
  const mats = document.getElementById('matsRow');
  clear(mats);
  for (const [name, ids] of Object.entries(p.mats)) {
    if (ids.length) mats.appendChild(el('div', { class: 'otherCard', text: `${MAT_LABEL[name] || name}：${counts(ids)}` }));
  }

  const supply = document.getElementById('supply');
  clear(supply);
  // 基本の財宝・勝利点（呪いも含む）・王国カードを見出し付きの3組にまとめ、
  // がれきの山のように王国の外から増える山は最後の組にまとめて出す
  const known = new Set([...BASIC_IDS, ...game.kingdom]);
  const basicIds = BASIC_IDS.filter((id) => game.supply[id] != null);
  const supplyGroups = [
    ['基本の財宝', basicIds.filter((id) => is(id, 'treasure'))],
    ['基本の勝利点', basicIds.filter((id) => !is(id, 'treasure'))],
    ['王国のカード', game.kingdom.filter((id) => game.supply[id] != null)],
    ['そのほか', Object.keys(game.supply).filter((id) => !known.has(id))],
  ];
  for (const [label, ids] of supplyGroups) {
    if (!ids.length) continue;
    const group = el('div', { class: 'supplyGroup' }, [el('h3', { class: 'supplyGroup__label', text: label })]);
    const row = el('div', { class: 'cards supplyGroup__row' });
    for (const id of ids) {
      const count = game.supply[id];
      const buyable = humanControls && canBuy(game, id);
      const node = gcNode(id, buyable, () => run(buyCard(game, id), (ok) => { if (ok) soundBuy(); backToTurn(); }), count);
      // 前回よりこの山の残りが減っていれば、誰かが買った合図にほのかに光らせる
      const prevCount = prevRender && prevRender.supply[id];
      if (prevCount != null && count < prevCount) node.classList.add('is-bought');
      if (count === 0) node.classList.add('is-empty');
      // CPU の手番のあいだ、その手番に買った山に印を付ける
      const nBought = humanControls ? 0 : t.bought.filter((b) => b === id).length;
      if (nBought) tagCard(node, `購入${nBought > 1 ? `×${nBought}` : ''}`);
      row.appendChild(node);
      // 森の賢者: 対局の始めに脇に置いた 3 つの恵みを、その札の横に並べる
      if (id === 'druid' && game.druidBoons) for (const b of game.druidBoons) row.appendChild(gcNode(b, false));
    }
    group.appendChild(row);
    supply.appendChild(group);
  }
  // イベント・プロジェクト・ランドマークなど（王国のカードと廃棄置き場の間に置く札）。買えれば押せる
  if (game.landscapes.length || game.boons || game.hexes) {
    const landscapesBox = el('div', { class: 'cards supplyGroup__row' });
    for (const id of game.landscapes) {
      const buyable = humanControls && t.phase === 'buy' && canBuyEvent(game, id);
      landscapesBox.appendChild(gcNode(id, buyable, () => run(buyEvent(game, id), (ok) => { if (ok) soundBuy(); backToTurn(); })));
    }
    if (game.boons) landscapesBox.appendChild(pileButton('恵みの山', game.boons));
    if (game.hexes) landscapesBox.appendChild(pileButton('呪詛の山', game.hexes));
    supply.appendChild(el('div', { class: 'supplyGroup' }, [el('h3', { class: 'supplyGroup__label', text: 'イベントなど' }), landscapesBox]));
  }
  // サプライ外の山（褒賞・賞品など）。イベントと同じく廃棄置き場の左に置く。買えない、タップで説明だけ
  const nonSupplyIds = Object.keys(game.nonSupply).filter((id) => game.nonSupply[id] > 0);
  if (nonSupplyIds.length) {
    const nonSupplyBox = el('div', { class: 'cards supplyGroup__row' });
    for (const id of nonSupplyIds) nonSupplyBox.appendChild(gcNode(id, false, null, game.nonSupply[id]));
    supply.appendChild(el('div', { class: 'supplyGroup' }, [el('h3', { class: 'supplyGroup__label', text: 'サプライ外' }), nonSupplyBox]));
  }
  // 廃棄置き場: 上のバーの真ん中に、横長の枠で枚数と中身を出す
  const trashBox = document.getElementById('trashBox');
  trashBox.querySelector('.trashBox__count').textContent = `廃棄 ${game.trash.length} 枚`;
  trashBox.querySelector('.trashBox__list').textContent = counts(game.trash);
  trashBox.title = counts(game.trash);

  // 影の札（山札にある影）: アクションフェイズに手札の横に並べる
  const shadowLabel = document.getElementById('shadowLabel');
  const shadowRow = document.getElementById('shadowRow');
  clear(shadowRow);
  const shadows = t.phase === 'action' ? shadowsInDeck(game) : [];
  shadowLabel.hidden = shadows.length === 0;
  for (const id of shadows) {
    const playable = humanControls && canPlayShadow(id);
    shadowRow.appendChild(gcNode(id, playable, playable ? () => run(playShadow(game, id)) : null));
  }

  const hand = document.getElementById('hand');
  clear(hand);
  // 手札を扇のように並べるための位置（--i/--n）と、新しく引いた札の見分け（山札から来た合図でスライドイン）
  const handNew = newnessMarks(prevRender && prevRender.pi === game.current ? prevRender.hand : [], p.hand);
  hand.style.setProperty('--n', String(p.hand.length));
  p.hand.forEach((id, i) => {
    const playableAction = humanControls && t.phase === 'action' && canPlayAction(game, id);
    const playableTreasure = humanControls && t.phase === 'buy' && isTreasureNow(game, id);
    const playableNight = humanControls && t.phase === 'night' && canPlayNight(game, id);
    const onClick = playableAction ? () => run(playAction(game, id))
      : playableTreasure ? () => run(playTreasureGen(game, id))
      : playableNight ? () => run(playNight(game, id))
      : null;
    const node = gcNode(id, !!onClick, onClick);
    node.style.setProperty('--i', String(i));
    if (handNew[i]) node.classList.add('is-new-draw');
    hand.appendChild(node);
  });

  // 次にすることの案内（HUD の近くに短く出す）
  document.getElementById('turnHint').textContent = !humanControls ? '' : turnHint(game, p, t);

  const log = document.getElementById('log');
  clear(log);
  for (const line of game.log.slice(-4)) log.appendChild(el('p', { text: line }));

  // 次回の renderTurn で「増えた・減った」を見分けるための記録
  prevRender = {
    pi: game.current,
    hand: [...p.hand],
    play: playIds,
    supply: { ...game.supply },
    nums: { actions: t.actions, buys: t.buys, money: t.money },
  };
}

// 次に何をすればいいかの短い案内（HUD の近くに出す）
function turnHint(g, p, t) {
  if (t.phase === 'action') {
    if (p.hand.some((id) => canPlayAction(g, id))) return 'アクションを使うか、「購入フェイズへ」';
    return '使えるアクションがなければ「購入フェイズへ」';
  }
  if (t.phase === 'buy') {
    if (p.hand.some((id) => isTreasureNow(g, id))) return '財宝を出してから、買いたい札をタップ';
    if (Object.keys(g.supply).some((id) => canBuy(g, id))) return '買いたい札をタップ';
    return '買うものがなければ「手番を終える」';
  }
  if (t.phase === 'night') return '夜の札を使うか、「手番を終える」';
  return '';
}

function onEndTurn() {
  soundEnd();
  run(endTurn(game), () => {
    if (game.over) { showResult(); return; }
    startTurnPass();
  });
}

// ---- CPU の番を進める ----
// つよい・さいきょうは、その CPU の最初の手番だけ狙いの札を自己対局で決める（少し止まる）。決め終われば次からは一瞬
function scheduleCpuMove(pi) {
  if (game.over) { showResult(); return; }
  const seat = seats[pi];
  const needsPlan = (seat.level === 'strong' || seat.level === 'expert') && !(game.cpuPlans && game.cpuPlans[pi]);
  if (needsPlan) {
    document.getElementById('cpuThinking').hidden = false;
    planInWorker(pi, seat.level, () => {
      document.getElementById('cpuThinking').hidden = true;
      doCpuMove(pi);
    });
    return;
  }
  setTimeout(() => doCpuMove(pi), cpuDelay());
}
// 狙いの札を決める自己対局は、画面が止まらないよう Web Worker（planner.js）で回す。使えなければこのスレッドで
let planner = null;
let planSeq = 0;
function planInWorker(pi, level, done) {
  const g = game;
  const finish = (plan, duchyAt) => {
    if (game !== g) return; // 待っているあいだに対局が変わった
    g.cpuPlans = g.cpuPlans || {};
    g.cpuPlans[pi] = Object.assign(plan, duchyAt != null ? { duchyAt } : {});
    done();
  };
  try {
    if (!planner && typeof Worker !== 'undefined') planner = new Worker('./planner.js', { type: 'module' });
  } catch { planner = null; }
  if (!planner) { setTimeout(() => { cpuPlanFor(g, pi, level); done(); }, 30); return; }
  const id = ++planSeq;
  const onMsg = (e) => {
    if (e.data.id !== id) return;
    planner.removeEventListener('message', onMsg);
    finish(e.data.plan, e.data.duchyAt);
  };
  planner.addEventListener('message', onMsg);
  planner.addEventListener('error', () => { planner = null; cpuPlanFor(g, pi, level); done(); }, { once: true });
  planner.postMessage({ id, kingdom: g.kingdom.filter((k) => k in g.supply || g.stacks[k]), landscapes: g.landscapes, players: g.players.length, colony: 'colony' in g.supply, level });
}

// CPU の次の1手を決めて実行する（simulate() と同じ組み合わせ）
function doCpuMove(pi) {
  if (game.over) { showResult(); return; }
  const level = seats[pi].level;
  const m = cpuNextMove(game, level);
  if (m.type === 'action') { run(playAction(game, m.id)); return; }
  if (m.type === 'shadow') { run(playShadow(game, m.id)); return; }
  if (m.type === 'villager') { spendVillager(game); backToTurn(); return; }
  if (m.type === 'buyPhase') { run(enterBuyPhase(game)); return; }
  if (m.type === 'treasure') { run(playTreasureGen(game, m.id)); return; }
  if (m.type === 'coffers') { spendCoffers(game, m.n); backToTurn(); return; }
  if (m.type === 'buy') { run(buyCard(game, m.id), (ok) => { if (ok) soundBuy(); backToTurn(); }); return; }
  if (m.type === 'event') { run(buyEvent(game, m.id), (ok) => { if (ok) soundBuy(); backToTurn(); }); return; }
  if (m.type === 'nightPhase') { enterNightPhase(game); backToTurn(); return; }
  if (m.type === 'night') { run(playNight(game, m.id)); return; }
  onEndTurn();
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
// 手番の人に画面を戻す（他の人の手札を手番の人に見せない）。手番を操作する人が CPU なら、続けて CPU に打たせる
function backToTurn() {
  if (game.over) { showResult(); return; }
  const pi = turnController(game);
  if (isHumanSeat(pi)) { maybeGoToPass(pi, () => { showScreen('game'); renderTurn(); }); return; }
  showScreen('game');
  renderTurn();
  scheduleCpuMove(pi);
}

// 問いに答える（4 種類すべてここでまとめる）。答える人が CPU なら、画面を出さずに CPU に答えさせる
function showQuestion(q) {
  if (!isHumanSeat(q.player)) { step(pendingGen.next(cpuAnswer(game, q, seats[q.player].level))); return; }
  maybeGoToPass(q.player, () => renderQuestion(q));
}
function renderQuestion(q) {
  selected = new Set();
  showScreen('choice');
  document.getElementById('choiceWho').textContent = `${game.players[q.player].name} が選ぶ`;
  document.getElementById('choiceLabel').textContent = q.purpose;
  const countEl = document.getElementById('choiceCount');
  const grid = document.getElementById('choiceGrid');
  clear(grid);
  grid.classList.toggle('choiceGrid--pick', q.type === 'hand' || q.type === 'cards');
  const buttonsBox = document.getElementById('choiceButtons');
  clear(buttonsBox);
  const confirm = document.getElementById('choiceConfirm');
  confirm.hidden = true;
  confirm.onclick = null;

  if (q.type === 'supply') {
    countEl.textContent = q.optional ? '1枚選ぶか、獲得しないを選んでください' : '1枚選んでください';
    for (const id of q.options) grid.appendChild(gcNode(id, true, () => answer(id)));
    if (q.optional) buttonsBox.appendChild(el('button', { class: 'pill', text: '獲得しない', onclick: () => answer(null) }));
    return;
  }
  if (q.type === 'choose') {
    countEl.textContent = '1つ選んでください';
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
    countEl.textContent = `あと${Math.max(q.min - selected.size, 0)}枚は選んでください（最大${q.max}枚）`;
  }
  updatePicked();
}
function answer(value) {
  step(pendingGen.next(value));
}

// ==================================================================
// 結果
// ==================================================================
// 点の内訳（勝利点の札・トークンなど）を短い文言の配列で返す。engine.js の score() と同じ数え方をなぞる
function scoreBreakdown(pl, g) {
  const all = allCards(pl);
  const counts = new Map();
  for (const id of all) counts.set(id, (counts.get(id) || 0) + 1);
  const lines = [];
  for (const [id, n] of counts) {
    const c = CARDS[id];
    const per = (c.points || 0) + (c.pointsFn ? c.pointsFn(all) : 0);
    if (per) lines.push(`${c.name}×${n}（${per * n}点）`);
  }
  for (const id of new Set(all)) {
    if (CARDS[id].scoreBonus) { const v = CARDS[id].scoreBonus(pl); if (v) lines.push(`${CARDS[id].name}（${v}点）`); }
  }
  for (const id of g.landscapes) {
    if (CARDS[id].score) { const v = CARDS[id].score(g, pl, all); if (v) lines.push(`${CARDS[id].name}（${v}点）`); }
  }
  for (const id of pl.states || []) { const v = CARDS[id].points || 0; if (v) lines.push(`${CARDS[id].name}（${v}点）`); }
  if (pl.tokens.vp > 0) lines.push(`勝利点トークン（${pl.tokens.vp}点）`);
  return lines;
}

function showResult() {
  showScreen('result');
  const results = finalResults(game);
  const scoreText = (r) => {
    const vp = game.players[r.index].tokens.vp;
    const vpText = vp > 0 ? `・うち勝利点トークン ${vp}` : '';
    return `${r.score}点（${r.turns}手番${vpText}）`;
  };

  // 上位3人は表彰台に、1位を中央・一番高く（CSS の order で並べ替える）
  const podium = document.getElementById('podium');
  clear(podium);
  const top = results.slice(0, 3);
  top.forEach((r, i) => {
    const rank = i + 1;
    const step = el('div', { class: 'podium__step', 'data-rank': String(rank) });
    if (rank === 1) {
      step.appendChild(el('span', { class: 'podium__crown', text: '★' }));
      step.appendChild(confettiNode());
    }
    step.appendChild(el('span', { class: 'podium__rank', text: `${rank}位` }));
    step.appendChild(el('span', { class: 'podium__name', text: r.name }));
    step.appendChild(el('span', { class: 'podium__score', text: scoreText(r) }));
    const breakdown = scoreBreakdown(game.players[r.index], game).join('・');
    if (breakdown) step.appendChild(el('span', { class: 'podium__breakdown', text: breakdown }));
    podium.appendChild(step);
  });

  const ranking = document.getElementById('ranking');
  clear(ranking);
  results.slice(3).forEach((r, i) => {
    const li = el('li', {}, [el('span', { class: 'ranking__main', text: `${i + 4}位 ${r.name} ${scoreText(r)}` })]);
    const breakdown = scoreBreakdown(game.players[r.index], game).join('・');
    if (breakdown) li.appendChild(el('span', { class: 'ranking__breakdown', text: breakdown }));
    ranking.appendChild(li);
  });
}
// 1位を祝う紙吹雪（CSS のアニメだけで散らす。reduced-motion では止まったまま見えなくてよいので display は消さない）
function confettiNode() {
  const box = el('div', { class: 'confetti' });
  for (let i = 0; i < 14; i++) {
    const piece = document.createElement('span');
    piece.className = 'confetti__piece';
    piece.style.setProperty('--x', `${Math.round(Math.random() * 200 - 100)}%`);
    piece.style.setProperty('--d', `${(Math.random() * 0.6).toFixed(2)}s`);
    piece.style.setProperty('--r', `${Math.round(Math.random() * 360)}deg`);
    box.appendChild(piece);
  }
  return box;
}
document.getElementById('restartBtn').addEventListener('click', () => {
  game = null;
  shownPlayer = null;
  prevRender = null;
  showScreen('setup');
  renderSetup();
});

renderSetup();
