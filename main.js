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
  newGame, currentPlayer, turnController, playAction, playTreasureGen, playAllTreasures, playTreasure,
  enterBuyPhase, canBuy, buyCard, beginTurn, endTurn, spendCoffers, payDebt, finalResults, allCards,
  landscapePool, canBuyEvent, buyEvent, enterNightPhase, canPlayNight, playNight, spendVillager,
  canPlayAction, shadowsInDeck, playShadow, isTreasureNow, emptyPiles, EMPTY_PILES_LIMIT,
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
let soundOn = load('sound', true);
function beep(freq, dur, gain = 0.1) {
  if (!soundOn) return;
  try {
    if (!audioCtx) { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); setAudioSession(true); }
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.frequency.value = freq;
    osc.type = 'sine';
    g.gain.setValueAtTime(gain, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
    osc.connect(g).connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + dur);
  } catch { /* 音が出せなくても遊べる */ }
}
const soundPlay = () => beep(360, 0.1);
const soundBuy = () => beep(560, 0.14);
const soundEnd = () => beep(220, 0.2);
// 夜の古い城の作戦卓、という雰囲気に合わせて柔らかく小さく
const soundDraw = () => beep(620, 0.05, 0.035); // 札を引く（連続しないよう呼び出し側で間引く）
const soundShuffle = () => { beep(220, 0.12, 0.045); setTimeout(() => beep(190, 0.14, 0.035), 90); }; // 山札を混ぜる
const soundTrash = () => beep(130, 0.2, 0.08); // 廃棄（低く短く）
const soundAttack = () => beep(170, 0.16, 0.09); // 攻撃を受けた
const soundTurnStart = () => { beep(500, 0.1, 0.05); setTimeout(() => beep(660, 0.12, 0.05), 90); }; // 自分の番が来た
const soundCutIn = () => { beep(520, 0.1, 0.08); setTimeout(() => beep(760, 0.2, 0.08), 100); }; // 高コストの購入カットイン
const soundFlip = () => beep(480, 0.07, 0.07); // パック開封でめくる
const soundFanfare = () => { // 結果画面、1位のファンファーレ
  [523, 659, 784, 1046].forEach((f, i) => setTimeout(() => beep(f, 0.22, 0.09), i * 110));
};

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
let endConfirmTurn = null; // 「何も買わずに終える？」を一度押した手番（t オブジェクトそのもの。新しい手番で自然に外れる）
let summaryOpen = false; // 「相手の手番」帯を開いているか。手番を渡すたびにたたみ直す
let humanBought = {}; // 今の対局で人が買った札の数（記録「よく買った札」用。対局ごとにリセット）

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
// 札の id を種類ごとにまとめ、コスト順（同じコストは名前順）に並べる
function groupByCost(ids) {
  const m = new Map();
  for (const id of ids) m.set(id, (m.get(id) || 0) + 1);
  return [...m.entries()].sort((a, b) => costOf(game, a[0]) - costOf(game, b[0]) || CARDS[a[0]].name.localeCompare(CARDS[b[0]].name, 'ja'));
}
// オーバーレイの土台（deckList と同じ見た目）。Esc・外側タップ・閉じるボタンで閉じる。
// extraClass: back に足すクラス（セレクタの二重起動よけ・専用の見た目に使う）
function openModal(extraClass, ariaLabel, title, bodyNode) {
  const closeBtn = el('button', { class: 'deckList__close', text: '×', 'aria-label': '閉じる' });
  const box = el('div', { class: 'deckList__box' }, [
    el('div', { class: 'deckList__head' }, [el('h2', { text: title }), closeBtn]),
    bodyNode,
  ]);
  const back = el('div', { class: `deckList ${extraClass}`, role: 'dialog', 'aria-label': ariaLabel }, [box]);
  const close = () => { back.remove(); document.removeEventListener('keydown', onKey); };
  const onKey = (e) => { if (e.key === 'Escape') close(); };
  closeBtn.addEventListener('click', close);
  back.addEventListener('click', (e) => { if (e.target === back) close(); });
  document.addEventListener('keydown', onKey);
  document.body.appendChild(back);
}
// 山札・捨て札・デッキ全体を一覧するパネル。タブで切り替え、Esc・外側タップ・閉じるボタンで閉じる
function showDeckList(p) {
  if (document.querySelector('.deckList')) return;
  const wholePlay = p === currentPlayer(game) ? game.playArea : p.inPlay; // 手番の人は played 札が playArea にある
  const TABS = [
    ['デッキ全体', [...p.hand, ...wholePlay, ...p.deck, ...p.discard, ...Object.values(p.mats).flat()]],
    ['山札', p.deck],
    ['捨て札', p.discard],
  ];
  const body = el('div', { class: 'deckList__body' });
  const tabBtns = el('div', { class: 'tabs' }, TABS.map(([label], i) => el('button', {
    class: `pill${i === 0 ? ' pill--accent' : ''}`, text: label, 'data-i': i,
  })));
  const showTab = (i) => {
    for (const btn of tabBtns.children) btn.classList.toggle('pill--accent', Number(btn.dataset.i) === i);
    clear(body);
    const grid = el('div', { class: 'cards' });
    const groups = groupByCost(TABS[i][1]);
    if (!groups.length) grid.appendChild(el('p', { class: 'screenCard__note', text: 'なし' }));
    for (const [id, n] of groups) grid.appendChild(tagCard(gcNode(id, false), `${n}枚`));
    body.appendChild(grid);
  };
  tabBtns.addEventListener('click', (e) => {
    const i = e.target.dataset.i;
    if (i != null) showTab(Number(i));
  });
  openModal('', '山札・捨て札・デッキ全体', `${p.name}の札`, el('div', {}, [tabBtns, body]));
  showTab(0);
}
// 図鑑: 全カードを拡張ごとに並べ、対局で使った・得た札だけ表向きにする。
// 約500枚あるので、開いているタブだけカードを描く（タブ切り替えのたびに作り直す）
function cardsBySet() {
  const m = new Map();
  for (const c of Object.values(CARDS)) {
    if (!m.has(c.set)) m.set(c.set, []);
    m.get(c.set).push(c.id);
  }
  return m;
}
function showCodex() {
  if (document.querySelector('.codex')) return;
  const discovered = new Set(load('discovered', []));
  const bySet = cardsBySet();
  const sets = SETS.filter((s) => bySet.has(s.id));
  const total = [...bySet.values()].reduce((n, ids) => n + ids.length, 0);
  const totalGot = [...bySet.values()].flat().filter((id) => discovered.has(id)).length;
  const body = el('div', { class: 'deckList__body' });
  const tabBtns = el('div', { class: 'tabs tabs--wrap' }, sets.map((s, i) => {
    const ids = bySet.get(s.id);
    const n = ids.filter((id) => discovered.has(id)).length;
    return el('button', { class: `pill${i === 0 ? ' pill--accent' : ''}`, text: `${s.name}（${n}/${ids.length}）`, 'data-i': i });
  }));
  const showTab = (i) => {
    for (const btn of tabBtns.children) btn.classList.toggle('pill--accent', Number(btn.dataset.i) === i);
    clear(body);
    const grid = el('div', { class: 'cards' });
    const ids = [...bySet.get(sets[i].id)].sort((a, b) => CARDS[a].name.localeCompare(CARDS[b].name, 'ja'));
    for (const id of ids) {
      const got = discovered.has(id);
      const node = cardNode(id, false);
      if (!got) { node.classList.add('is-undiscovered'); tagCard(node, '未発見'); }
      grid.appendChild(node);
    }
    body.appendChild(grid);
  };
  tabBtns.addEventListener('click', (e) => {
    const i = e.target.dataset.i;
    if (i != null) showTab(Number(i));
  });
  openModal('codex', '図鑑', `図鑑（${totalGot}/${total}）`, el('div', {}, [tabBtns, body]));
  showTab(0);
}
// 記録: 対局数・人の勝敗・最高点・よく買った札。対局の終わりに recordGameEnd() が更新する
function showRecords() {
  if (document.querySelector('.records')) return;
  const stats = load('stats', null);
  const body = el('div', { class: 'deckList__body' });
  if (!stats || stats.games === 0) {
    body.appendChild(el('p', { class: 'screenCard__note', text: 'まだ対局の記録がありません' }));
  } else {
    const lines = [
      `対局数：${stats.games}`,
      `人の勝ち数：${stats.humanWins}`,
      `最高点：${stats.bestScore}`,
    ];
    for (const lv of CPU_LEVELS) {
      const w = stats.winsByLevel[lv.id];
      if (w) lines.push(`CPU（${lv.name}）に ${w.win}勝${w.lose}敗`);
    }
    for (const t of lines) body.appendChild(el('p', { class: 'records__line', text: t }));
    const bought = Object.entries(stats.bought || {}).sort((a, b) => b[1] - a[1]).slice(0, 8);
    if (bought.length) {
      body.appendChild(el('p', { class: 'sectionLabel', text: 'よく買った札' }));
      const grid = el('div', { class: 'cards' });
      for (const [id, n] of bought) if (CARDS[id]) grid.appendChild(tagCard(cardNode(id, false), `${n}回`));
      body.appendChild(grid);
    }
  }
  openModal('records', '記録', '記録', body);
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
// 人の席の名前（設定画面で入力。空なら「n人目」）
let names = (Array.isArray(load('names', null)) ? load('names', null) : []).map((n) => (typeof n === 'string' ? n : ''));
const seatName = (s, i) => (s.type === 'human' ? ((names[i] || '').trim() || `${i + 1}人目`) : `CPU（${CPU_LEVELS.find((l) => l.id === s.level).name}）`);

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
// 財宝を自動で出す設定（既定オフ）。基本の財宝（効果のないもの）だけを対象にする
let autoPlayTreasures = load('autoPlayTreasures', false) === true;

function persistSetup() {
  save('players', players);
  save('seats', seats);
  save('names', names);
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
    if (seats[i].type === 'human') {
      const input = el('input', { class: 'seatRow__name', type: 'text', maxlength: 10, placeholder: `${i + 1}人目`, 'aria-label': `${i + 1}人目の名前` });
      input.value = names[i] || '';
      input.addEventListener('input', () => { names[i] = input.value; save('names', names); });
      row.appendChild(input);
    }
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
  box.appendChild(el('div', { class: 'chipRow' }, [
    el('button', { class: 'pill pill--accent', text: '引き直し', onclick: () => openPackReveal() }),
    // 拡張の選択もイベントなどの設定も無視して、全カードからひく
    el('button', { class: 'pill', text: '完全ランダム', onclick: () => openPackReveal(true) }),
  ]));
  return box;
}
// 組の中身だけ決める（状態は書き換えない）。reroll（即反映）と openPackReveal（演出つき）の両方から使う
// full: 完全ランダム（全拡張から、イベントなども 0〜2 枚まぜる）
function decideRandom(full = false) {
  const pool = full ? ALL_KINGDOM : kingdomPool([...selectedSets]);
  const k = randomKingdom(pool.length >= 10 ? pool : ALL_KINGDOM);
  const lpool = full ? ALL_LANDSCAPES : landscapePool([...selectedSets]);
  const l = full || landscapesOn ? randomKingdom(lpool, Math.floor(Math.random() * 3)) : [];
  return { kingdom: k, landscapes: l };
}
// 対象の拡張を変えたときなど、演出なしですぐ反映する
function reroll() {
  const { kingdom: k, landscapes: l } = decideRandom();
  kingdom = k;
  landscapes = l;
  persistSetup();
  renderSetup();
}

// ---- おまかせ：パックを開ける演出 ----
// 組を決め、裏向きの札を1枚ずつめくって見せる。タップで全部すぐ出せる。終わったら「この組で始める／もう一度ひく」。
// reduced-motion では演出をせず最初から表向きで並べる
function openPackReveal(full = false) {
  const { kingdom: k, landscapes: l } = decideRandom(full);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ids = [...k, ...l];
  const slots = ids.map((id) => {
    const front = isLandscape(id) ? gcNode(id, false) : cardNode(id, false);
    const back = el('div', { class: 'packSlot__back' }, [el('span', { class: 'packSlot__mark', text: '?' })]);
    return el('div', { class: 'packSlot' }, [front, back]);
  });
  const grid = el('div', { class: 'cards cards--fan packStage__grid' }, slots);
  const hint = el('p', { class: 'packStage__hint', text: 'タップでめくる' });
  const foot = el('div', { class: 'packStage__foot', hidden: true }, [
    el('button', { class: 'pill', text: 'もう一度ひく', onclick: () => { overlay.remove(); openPackReveal(full); } }),
    el('button', {
      class: 'pill pill--accent', text: 'この組で始める',
      onclick: () => { kingdom = k; landscapes = l; persistSetup(); overlay.remove(); startGame(); },
    }),
  ]);
  const box = el('div', { class: 'packStage__box' }, [
    el('p', { class: 'packStage__title', text: '王国パックを開ける' }),
    grid, hint, foot,
  ]);
  const overlay = el('div', { class: 'cardDetail packStage', role: 'dialog', 'aria-label': 'おまかせの組を開ける' }, [box]);
  document.body.appendChild(overlay);

  let done = false;
  function finish() {
    if (done) return;
    done = true;
    for (const s of slots) s.classList.add('is-revealed');
    hint.hidden = true;
    foot.hidden = false;
  }
  if (reduced) {
    finish();
  } else {
    slots.forEach((s, i) => {
      setTimeout(() => {
        if (done) return;
        s.classList.add('is-revealed');
        soundFlip();
        if (i === slots.length - 1) finish();
      }, 220 * (i + 1));
    });
    overlay.addEventListener('click', finish); // どこを押しても一気に全部めくる
  }
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
  if (!m || m === mode) return;
  mode = m;
  persistSetup();
  renderSetup();
  if (m === 'random') openPackReveal(); // おまかせを選んだら、その場で組を決めてパックを開ける演出を見せる
});
{
  const toggle = document.getElementById('autoTreasureToggle');
  toggle.checked = autoPlayTreasures;
  toggle.addEventListener('change', () => { autoPlayTreasures = toggle.checked; save('autoPlayTreasures', autoPlayTreasures); });
}
function startGame() {
  const k = activeKingdom();
  if (!k) return;
  kingdom = k;
  persistSetup();
  shownPlayer = null;
  prevRender = null;
  summaryOpen = false;
  humanBought = {};
  seenShuffle.clear();
  seenTrash = 0;
  game = newGame(players, kingdom, seats.map(seatName), { landscapes: activeLandscapes() });
  startTurnPass();
}
document.getElementById('startBtn').addEventListener('click', startGame);
document.getElementById('codexBtn').addEventListener('click', showCodex);
const soundBtn = document.getElementById('soundBtn');
const showSound = () => { soundBtn.textContent = soundOn ? '音 オン' : '音 オフ'; soundBtn.setAttribute('aria-pressed', String(soundOn)); };
showSound();
soundBtn.addEventListener('click', () => {
  soundOn = !soundOn;
  save('sound', soundOn);
  setAudioSession(soundOn);
  showSound();
});
document.getElementById('recordsBtn').addEventListener('click', showRecords);

// ==================================================================
// 手番を渡す画面（今この端末を見ている人と、答える人が違うときにはさむ。人どうしのときだけ出す）
// ==================================================================
function goToPass(pi, onReady) {
  summaryOpen = false; // 渡したら、まず相手の帯はたたんでおく
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
  maybeGoToPass(pi, () => { if (isHumanSeat(pi)) soundTurnStart(); run(beginTurn(game)); });
}

// ==================================================================
// 相手（CPU・交代の人）の直前の手番のまとめ。折りたたみ帯。タップで札を見て開閉できる
function renderTurnSummaries() {
  const bar = document.getElementById('turnSummaryBar');
  const toggle = document.getElementById('turnSummaryToggle');
  const panel = document.getElementById('turnSummaryPanel');
  const list = [...(game.turnSummaries || [])].slice(-4).reverse();
  bar.hidden = list.length === 0;
  if (!list.length) return;
  toggle.textContent = `${summaryOpen ? '▾' : '▸'} 相手の手番（${list.length}）`;
  toggle.onclick = () => { summaryOpen = !summaryOpen; renderTurnSummaries(); };
  panel.hidden = !summaryOpen;
  if (!summaryOpen) return;
  clear(panel);
  for (const s of list) {
    const box = el('div', { class: 'turnSummary' });
    box.appendChild(el('p', { class: 'turnSummary__name', text: s.name }));
    const row = (label, ids) => {
      if (!ids.length) return;
      box.appendChild(el('p', { class: 'turnSummary__label', text: label }));
      const cards = el('div', { class: 'cards cards--mini' });
      for (const [id, n] of groupByCost(ids)) cards.appendChild(n > 1 ? tagCard(gcNode(id, false), `${n}枚`) : gcNode(id, false));
      box.appendChild(cards);
    };
    row('使った', s.played);
    row('買った・得た', s.gained);
    row('廃棄', s.trashed);
    if (!s.played.length && !s.gained.length && !s.trashed.length) box.appendChild(el('p', { class: 'turnSummary__label', text: '何もしなかった' }));
    panel.appendChild(box);
  }
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
  renderTurnSummaries();

  const PHASE_LABEL = { action: 'アクションフェイズ', buy: '購入フェイズ', night: '夜のフェイズ' };
  const phasePill = document.getElementById('phasePill');
  phasePill.textContent = PHASE_LABEL[t.phase] || '';
  phasePill.dataset.phase = t.phase;

  const stats = document.getElementById('stats');
  clear(stats);
  stats.appendChild(el('span', { class: 'hud__name', text: p.name }));
  const medals = el('div', { class: 'medals' });
  // 前回より増えた分は animateMedalGains でチップを飛ばしてから跳ねさせる（それまでは medal--bump を付けない）
  const prevNums = prevRender && prevRender.pi === game.current ? prevRender.nums : {};
  const nums = {}; // 今回の値。次回との比較用に prevRender へ残す
  const medalGains = []; // 今回増えたメダル（要素と増えた量）
  const medal = (key, label, n) => {
    nums[key] = n;
    const elem = el('span', { class: 'medal' }, [
      el('span', { class: 'medal__n', text: String(n) }),
      el('span', { class: 'medal__label', text: label }),
    ]);
    const prevN = prevNums[key];
    if (prevN != null && n > prevN) medalGains.push({ elem, delta: n - prevN });
    return elem;
  };
  medals.appendChild(medal('actions', 'アクション', t.actions));
  medals.appendChild(medal('buys', '購入', t.buys));
  const moneyMedal = medal('money', '金貨', t.money);
  // 属州が買える 8 金から金色に、植民地も買える 11 金からさらに強く光る
  moneyMedal.classList.toggle('medal--richer', t.money >= 8);
  moneyMedal.classList.toggle('medal--richest', t.money >= 11);
  medals.appendChild(moneyMedal);
  if (p.tokens.vp > 0) medals.appendChild(medal('vp', '勝利点', p.tokens.vp));
  if (p.tokens.coffers > 0) medals.appendChild(medal('coffers', '財源', p.tokens.coffers));
  if (t.potions > 0) medals.appendChild(medal('potions', 'ポーション', t.potions));
  if (p.tokens.villagers > 0) medals.appendChild(medal('villagers', '村人', p.tokens.villagers));
  stats.appendChild(medals);
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
  } else {
    // 補助ボタン（主ボタンより小さく脇に残す）
    const secondary = [];
    if (t.phase === 'action' && p.tokens.villagers > 0) {
      secondary.push(el('button', { class: 'pill pill--sm', text: `村人を使う（残り${p.tokens.villagers}）`, onclick: () => { spendVillager(game); renderTurn(); } }));
    }
    if (t.phase === 'buy' && p.tokens.coffers > 0) {
      secondary.push(el('button', { class: 'pill pill--sm', text: `財源を使う（残り${p.tokens.coffers}）`, onclick: () => { spendCoffers(game, 1); renderTurn(); } }));
    }
    if (t.phase === 'buy' && p.tokens.debt > 0) {
      secondary.push(el('button', { class: 'pill pill--sm', text: `借金を返す（残り${p.tokens.debt}）`, onclick: () => { payDebt(game); renderTurn(); } }));
    }

    // 主ボタン（1つだけ大きく。状況で文言と動きが変わる＝MTGアリーナ風の「次へ」）
    let primary;
    if (t.phase === 'action') {
      primary = {
        text: '購入へ',
        onclick: () => run(enterBuyPhase(game), () => { if (autoPlayTreasures) autoPlayPlainTreasures(); backToTurn(); }),
      };
    } else {
      const autoPlayable = t.phase === 'buy' ? p.hand.filter((id) => isTreasureNow(game, id) && (!CARDS[id].play || CARDS[id].autoPlay)) : [];
      if (autoPlayable.length > 0) {
        const plain = autoPlayable.every((id) => !CARDS[id].play);
        const n = plain ? autoPlayable.reduce((sum, id) => sum + (CARDS[id].value || 0), 0) : null;
        primary = { text: n != null ? `財宝を出す（+${n}金）` : '財宝を出す', onclick: () => { playAllTreasures(game); renderTurn(); } };
      } else if (t.phase === 'buy' && p.hand.some((id) => is(id, 'night'))) {
        primary = { text: '夜のフェイズへ', onclick: () => { enterNightPhase(game); renderTurn(); } };
      } else {
        const nothingBought = t.bought.length === 0 && t.events.length === 0;
        if (!nothingBought) endConfirmTurn = null;
        const hasBuyable = nothingBought && (Object.keys(game.supply).some((id) => canBuy(game, id)) || game.landscapes.some((id) => canBuyEvent(game, id)));
        if (hasBuyable && endConfirmTurn !== t) {
          primary = { text: '何も買わずに終える？', onclick: () => { endConfirmTurn = t; renderTurn(); } };
        } else {
          primary = { text: '手番を終える', onclick: onEndTurn };
        }
      }
    }
    buttons.appendChild(el('button', { class: 'pill pill--accent pill--primary', text: primary.text, onclick: primary.onclick }));
    if (secondary.length) buttons.appendChild(el('div', { class: 'hud__buttons--secondary' }, secondary));
  }

  const playArea = document.getElementById('playArea');
  clear(playArea);
  const playIds = [...p.inPlay, ...game.playArea];
  const playNew = newnessMarks(prevRender ? prevRender.play : [], playIds);
  const newPlayNodes = []; // この回に新しく出た札（メダルの加算チップを飛ばす起点）
  playIds.forEach((id, i) => {
    const node = gcNode(id, false);
    if (playNew[i]) { node.classList.add('is-new-play'); newPlayNodes.push(node); }
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
      const node = gcNode(id, buyable, () => run(buyCard(game, id), (ok) => { if (ok) { soundBuy(); maybeShowBuyCutIn(id); if (isHumanSeat(game.current)) humanBought[id] = (humanBought[id] || 0) + 1; } backToTurn(); }), count);
      // 前回よりこの山の残りが減っていれば、誰かが買った合図にほのかに光らせる
      const prevCount = prevRender && prevRender.supply[id];
      if (prevCount != null && count < prevCount) node.classList.add('is-bought');
      if (count === 0) node.classList.add('is-empty');
      else if (humanControls && t.phase === 'buy' && !buyable) node.classList.add('is-unbuyable');
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
      const node = gcNode(id, buyable, () => run(buyEvent(game, id), (ok) => { if (ok) soundBuy(); backToTurn(); }));
      if (humanControls && t.phase === 'buy' && !buyable) node.classList.add('is-unbuyable');
      landscapesBox.appendChild(node);
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
  if (game.trash.length > seenTrash) soundTrash();
  seenTrash = game.trash.length;
  const trashBox = document.getElementById('trashBox');
  trashBox.querySelector('.trashBox__count').textContent = `廃棄 ${game.trash.length} 枚`;
  trashBox.querySelector('.trashBox__list').textContent = counts(game.trash);
  trashBox.title = counts(game.trash);

  // 終わりの近さ: 属州（・植民地）の残りと空いた山の数。engine の終了判定（EMPTY_PILES_LIMIT）とそろえる
  const endGauge = document.getElementById('endGauge');
  const provinceLeft = game.supply.province;
  const colonyLeft = game.supply.colony;
  const empty = emptyPiles(game);
  const near = provinceLeft <= game.players.length || (colonyLeft != null && colonyLeft <= game.players.length) || empty >= EMPTY_PILES_LIMIT - 1;
  endGauge.classList.toggle('is-near', near);
  const vpBit = colonyLeft != null ? `属州${provinceLeft}・植民地${colonyLeft}` : `属州${provinceLeft}`;
  endGauge.textContent = `${vpBit}　空${empty}/${EMPTY_PILES_LIMIT}`;

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
  // ponytail: 8 枚以上は折り返す前提で扇をやめる。本当に折り返したかは見ていない
  hand.style.setProperty('--fan', p.hand.length > 7 ? '0' : '1');
  p.hand.forEach((id, i) => {
    const playableAction = humanControls && t.phase === 'action' && canPlayAction(game, id);
    const playableTreasure = humanControls && t.phase === 'buy' && isTreasureNow(game, id);
    const playableNight = humanControls && t.phase === 'night' && canPlayNight(game, id);
    const onClick = playableAction ? () => runPlayAction(id)
      : playableTreasure ? () => run(playTreasureGen(game, id))
      : playableNight ? () => run(playNight(game, id))
      : null;
    const node = gcNode(id, !!onClick, onClick);
    node.style.setProperty('--i', String(i));
    hand.appendChild(node);
  });
  animateDraw(p, [...hand.children].filter((_, i) => handNew[i]));
  animateMedalGains(medalGains, newPlayNodes);

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
    nums,
  };
}

// メダルが増えたとき、増やした札（新しく場に出た札があればそこ、無ければ場の中央）から
// 「+2」のようなチップを該当のメダルへ飛ばし、着いたら跳ねさせる（Balatro 風）
function animateMedalGains(gains, originNodes) {
  if (!gains.length) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fast = allCpu() && spectatorSpeed === 'fast'; // CPU観戦の「速い」設定では省く
  if (reduced || fast) {
    for (const { elem } of gains) elem.classList.add('medal--bump');
    return;
  }
  let originRect = null;
  if (originNodes.length) {
    const rects = originNodes.map((n) => n.getBoundingClientRect());
    const left = Math.min(...rects.map((r) => r.left));
    const top = Math.min(...rects.map((r) => r.top));
    originRect = { x: (left + Math.max(...rects.map((r) => r.right))) / 2, y: (top + Math.max(...rects.map((r) => r.bottom))) / 2 };
  } else {
    const playArea = document.getElementById('playArea');
    const r = playArea.getBoundingClientRect();
    originRect = { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }
  gains.forEach(({ elem, delta }, i) => {
    const dest = elem.getBoundingClientRect();
    const dx = dest.left + dest.width / 2;
    const dy = dest.top + dest.height / 2;
    const chip = el('div', { class: 'coinChip', text: `+${delta}` });
    chip.style.left = `${dx}px`;
    chip.style.top = `${dy}px`;
    chip.style.setProperty('--dx', `${originRect.x - dx}px`);
    chip.style.setProperty('--dy', `${originRect.y - dy}px`);
    chip.style.animationDelay = `${i * 90}ms`;
    chip.addEventListener('animationend', () => {
      chip.remove();
      elem.classList.add('medal--bump');
      setTimeout(() => elem.classList.remove('medal--bump'), 400);
    });
    document.body.appendChild(chip);
  });
}

// 属州・植民地などの高得点札、コスト 6 以上の札を買ったとき、札が大きく横切るカットインを出す。
// 入力はふさがない（pointer-events: none）。reduced-motion では出さない。CPU 観戦の「速い」設定では短くする
function maybeShowBuyCutIn(id) {
  const card = CARDS[id];
  const isBig = card.cost >= 6 || (card.types.includes('victory') && card.points >= 6);
  if (!isBig) return;
  const fast = allCpu() && spectatorSpeed === 'fast';
  if (!fast) soundCutIn(); // 観戦の「速い」では省く（カットインの見た目を出さない場合も鳴らす）
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.buyCutIn').forEach((n) => n.remove()); // 連続して買われたら前のものは消す
  // 拡大表示（showCardDetail）と同じ見た目にするため card--peek を使い回す
  const big = gcNode(id, false);
  big.classList.remove('card--active');
  big.classList.add('card--peek', 'buyCutIn__card');
  big.tabIndex = -1;
  const wrap = el('div', { class: `cardDetail buyCutIn${fast ? ' buyCutIn--fast' : ''}` }, [
    el('div', { class: 'buyCutIn__veil' }),
    big,
  ]);
  big.addEventListener('animationend', () => wrap.remove());
  document.body.appendChild(wrap);
  setTimeout(() => wrap.remove(), fast ? 700 : 1300); // animationend が来ない場合の保険
}

// 山札・捨て札の枚数を出し、新しく引いた札を山札の位置から 1 枚ずつ飛ばす。
// この描画までに山札を混ぜていれば、先に捨て札から山札へ札が移る演出を入れ、混ぜた後に引いた札はその後に飛ばす
const seenShuffle = new Map(); // 席ごとに、演出済みの混ぜの回数
let seenTrash = 0; // 鳴らした廃棄の枚数（renderTurn のたびに増えていれば鳴らす）
function animateDraw(p, newNodes) {
  const deckPile = document.getElementById('deckPile');
  const discardPile = document.getElementById('discardPile');
  deckPile.querySelector('.pile__n').textContent = String(p.deck.length);
  discardPile.querySelector('.pile__n').textContent = String(p.discard.length);
  deckPile.classList.toggle('is-empty', p.deck.length === 0);
  // 山札の上に置いた札（引くか混ぜるまで）は、表向きで薄く出す
  const tk = p.topKnown;
  const topId = tk && tk.n === p.deck.length && p.deck.at(-1) === tk.id ? tk.id : null;
  const face = deckPile.querySelector('.pile__face');
  if ((face && face.dataset.id) !== (topId || undefined)) {
    if (face) face.remove();
    if (topId) {
      const f = cardNode(topId);
      f.classList.add('pile__face');
      f.dataset.id = topId;
      f.tabIndex = -1;
      f.setAttribute('aria-hidden', 'true');
      deckPile.prepend(f);
    }
  }
  discardPile.classList.toggle('is-empty', p.discard.length === 0);
  for (const g of document.querySelectorAll('.pileGhost')) g.remove();
  const pi = game.players.indexOf(p);
  const sh = p.shuffled;
  const shuffledNow = sh && sh.n > (seenShuffle.get(pi) || 0);
  if (sh) seenShuffle.set(pi, sh.n);
  // 音は reduced-motion に関わらず鳴らす。観戦の「速い」では省き、連続して引いてもうるさくしない
  const fast = allCpu() && spectatorSpeed === 'fast';
  if (shuffledNow) soundShuffle();
  if (!fast && newNodes.length) soundDraw();
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const deckRect = deckPile.getBoundingClientRect();
  const STEP = 120; // 1 枚ごとの間（ms）
  const SHUFFLE = 800; // 補充の演出の長さ（ms）
  // 混ぜる前に引いた札 → 補充 → 混ぜた後に引いた札 の順に並べる
  const hand = document.getElementById('hand');
  const before = [];
  const after = [];
  for (const node of newNodes) {
    const idx = [...hand.children].indexOf(node);
    (shuffledNow && idx >= sh.handLen ? after : before).push(node);
  }
  const fly = (node, delay) => {
    const r = node.getBoundingClientRect();
    node.style.setProperty('--dx', `${deckRect.left + deckRect.width / 2 - (r.left + r.width / 2)}px`);
    node.style.setProperty('--dy', `${deckRect.top + deckRect.height / 2 - (r.top + r.height / 2)}px`);
    node.style.animationDelay = `${delay}ms`;
    node.classList.add('is-new-draw');
  };
  before.forEach((node, k) => fly(node, k * STEP));
  if (!shuffledNow) return;
  const start = before.length * STEP;
  // 捨て札から山札へ、裏向きの札が何枚か流れていく
  const dr = discardPile.getBoundingClientRect();
  const piles = document.getElementById('piles');
  const pr = piles.getBoundingClientRect();
  for (let k = 0; k < 5; k++) {
    const ghost = el('div', { class: 'pileGhost' });
    ghost.style.left = `${dr.left - pr.left}px`;
    ghost.style.top = `${dr.top - pr.top}px`;
    ghost.style.width = `${dr.width}px`;
    ghost.style.height = `${dr.height}px`;
    ghost.style.setProperty('--gx', `${deckRect.left - dr.left}px`);
    ghost.style.setProperty('--gy', `${deckRect.top - dr.top}px`);
    ghost.style.animationDelay = `${start + k * 90}ms`;
    ghost.addEventListener('animationend', () => ghost.remove());
    piles.appendChild(ghost);
  }
  deckPile.style.setProperty('--shuffle-delay', `${start + 450}ms`);
  deckPile.classList.remove('is-shuffling');
  void deckPile.offsetWidth; // 続けて混ぜたときも演出をやり直す
  deckPile.classList.add('is-shuffling');
  after.forEach((node, k) => fly(node, start + SHUFFLE + k * STEP));
}

// 次に何をすればいいかの短い案内（HUD の近くに出す）
function turnHint(g, p, t) {
  if (t.phase === 'action') {
    if (p.hand.some((id) => canPlayAction(g, id))) return 'アクションを使うか、「購入へ」';
    return '使えるアクションがなければ「購入へ」';
  }
  if (t.phase === 'buy') {
    if (p.hand.some((id) => isTreasureNow(g, id))) return '財宝を出してから、買いたい札をタップ';
    if (Object.keys(g.supply).some((id) => canBuy(g, id))) return '買いたい札をタップ';
    return '買うものがなければ「手番を終える」';
  }
  if (t.phase === 'night') return '夜の札を使うか、「手番を終える」';
  return '';
}

// 「財宝を自動で出す」設定用。効果のある財宝（手で出す順番・可否に意味があるもの）は残す
function autoPlayPlainTreasures() {
  const p = currentPlayer(game);
  for (const id of [...p.hand]) if (is(id, 'treasure') && !CARDS[id].play) playTreasure(game, id);
}

// アクション札を使う。アタック札は、生成器の中で相手が被る前に鳴らす（細かい技ごとではなく、技を出した瞬間に 1 回）
function runPlayAction(id) {
  if (is(id, 'attack')) soundAttack();
  run(playAction(game, id));
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
  // 待っているあいだに「もう一度遊ぶ」で対局が変わったら、前の対局の手は打たない
  const g = game;
  if (needsPlan) {
    document.getElementById('cpuThinking').hidden = false;
    planInWorker(pi, seat.level, () => {
      if (game !== g) return;
      document.getElementById('cpuThinking').hidden = true;
      doCpuMove(pi);
    });
    return;
  }
  setTimeout(() => { if (game === g) doCpuMove(pi); }, cpuDelay());
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
  if (m.type === 'action') { runPlayAction(m.id); return; }
  if (m.type === 'shadow') { run(playShadow(game, m.id)); return; }
  if (m.type === 'villager') { spendVillager(game); backToTurn(); return; }
  if (m.type === 'buyPhase') { run(enterBuyPhase(game)); return; }
  if (m.type === 'treasure') { run(playTreasureGen(game, m.id)); return; }
  if (m.type === 'coffers') { spendCoffers(game, m.n); backToTurn(); return; }
  if (m.type === 'buy') { run(buyCard(game, m.id), (ok) => { if (ok) { soundBuy(); maybeShowBuyCutIn(m.id); } backToTurn(); }); return; }
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

// 対局の終わりに「図鑑」「記録」を更新する（CPU だけの観戦は数えない）
function recordGameEnd(results) {
  if (game.recorded) return;
  game.recorded = true; // rerender で結果画面を描き直しても二重に数えない
  if (humanCount() < 1) return;
  // 図鑑: この対局で場に出た・獲得された・買われた札をまとめて「発見」に加える
  // ponytail: ランドマーク等イベント系は「対局で使われた」まで厳密に追わず、組に入っていれば発見扱いにする
  const used = new Set(load('discovered', []));
  for (const id of game.trash) used.add(id);
  for (const id of game.landscapes) used.add(id);
  for (const pl of game.players) {
    for (const id of allCards(pl)) used.add(id);
    for (const id of pl.projects || []) used.add(id);
  }
  save('discovered', [...used]);

  // 記録: 対局数・人の勝敗・最高点・よく買った札
  const stats = load('stats', null) || { games: 0, humanWins: 0, bestScore: 0, winsByLevel: {}, bought: {} };
  stats.games += 1;
  const humanIdx = seats.map((s, i) => (s.type === 'human' ? i : -1)).filter((i) => i >= 0);
  const scoreOf = (i) => results.find((r) => r.index === i);
  const humanWin = humanIdx.some((i) => scoreOf(i).rank === 1);
  if (humanWin) stats.humanWins += 1;
  stats.bestScore = Math.max(stats.bestScore || 0, ...humanIdx.map((i) => scoreOf(i).score));
  const cpuLevels = new Set(seats.filter((s) => s.type === 'cpu').map((s) => s.level));
  for (const level of cpuLevels) {
    const w = stats.winsByLevel[level] || { win: 0, lose: 0 };
    if (humanWin) w.win += 1; else w.lose += 1;
    stats.winsByLevel[level] = w;
  }
  stats.bought = stats.bought || {};
  for (const [id, n] of Object.entries(humanBought)) stats.bought[id] = (stats.bought[id] || 0) + n;
  save('stats', stats);
}

function showResult() {
  showScreen('result');
  if (!game.recorded) soundFanfare(); // 描き直しでは鳴らさない（recordGameEnd が recorded を立てる）
  const results = finalResults(game);
  recordGameEnd(results);
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

  clear(document.getElementById('resultChart'));
  document.getElementById('resultChart').appendChild(scoreChartNode(game));
  clear(document.getElementById('resultMvp'));
  document.getElementById('resultMvp').appendChild(mvpNode(game));
}
// プレイヤーごとの線の色（表彰台と合わせた金・銀・銅 + もう1色）
const PLAYER_COLORS = ['#d8b23f', '#9aa0ab', '#a8703c', '#7fae6c'];
// 点数の推移の折れ線グラフ（SVG、ライブラリなし）。player.scoreHistory は手番ごとの得点
function scoreChartNode(g) {
  const box = el('div', { class: 'resultChart__box' });
  box.appendChild(el('p', { class: 'resultChart__title', text: '点数の推移' }));
  const W = 300, H = 120, PAD = 10;
  const series = g.players.map((p) => p.scoreHistory || []);
  const maxLen = Math.max(1, ...series.map((s) => s.length));
  const maxScore = Math.max(1, ...series.flat());
  const x = (i) => PAD + (i / Math.max(1, maxLen - 1)) * (W - PAD * 2);
  const y = (v) => H - PAD - (v / maxScore) * (H - PAD * 2);
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('class', 'resultChart__svg');
  const baseline = document.createElementNS(svg.namespaceURI, 'line');
  baseline.setAttribute('x1', PAD); baseline.setAttribute('x2', W - PAD);
  baseline.setAttribute('y1', H - PAD); baseline.setAttribute('y2', H - PAD);
  baseline.setAttribute('class', 'resultChart__axis');
  svg.appendChild(baseline);
  series.forEach((hist, pi) => {
    if (!hist.length) return;
    const color = PLAYER_COLORS[pi % PLAYER_COLORS.length];
    const d = hist.map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
    const path = document.createElementNS(svg.namespaceURI, 'path');
    path.setAttribute('d', d);
    path.setAttribute('class', 'resultChart__line');
    path.style.stroke = color;
    svg.appendChild(path);
  });
  box.appendChild(svg);
  const legend = el('div', { class: 'resultChart__legend' });
  g.players.forEach((p, pi) => {
    const item = el('span', { class: 'resultChart__legendItem' });
    item.appendChild(el('span', { class: 'resultChart__dot' }));
    item.lastChild.style.background = PLAYER_COLORS[pi % PLAYER_COLORS.length];
    item.appendChild(document.createTextNode(p.name));
    legend.appendChild(item);
  });
  box.appendChild(legend);
  return box;
}
// プレイヤーごとに、いちばん多く場に出した札を 3 枚まで見せる
function mvpNode(g) {
  const box = el('div', { class: 'resultMvp__box' });
  box.appendChild(el('p', { class: 'resultChart__title', text: '活躍した札' }));
  g.players.forEach((p, pi) => {
    // 銅貨・銀貨ばかりにならないよう、アクション札があればそれを優先する
    const all = Object.entries(p.cardPlays || {}).sort((a, b) => b[1] - a[1]);
    const actions = all.filter(([id]) => CARDS[id].types.includes('action'));
    const top = (actions.length ? actions : all).slice(0, 3);
    if (!top.length) return;
    const row = el('div', { class: 'resultMvp__row' });
    row.appendChild(el('span', { class: 'resultMvp__name', text: p.name }));
    const cards = el('div', { class: 'cards cards--mini resultMvp__cards' });
    for (const [id, n] of top) cards.appendChild(cardNode(id, false, null, null, undefined, `${n}回使用`));
    row.appendChild(cards);
    box.appendChild(row);
  });
  return box;
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
for (const id of ['deckPile', 'discardPile']) {
  const node = document.getElementById(id);
  node.addEventListener('click', () => { if (game && !game.over) showDeckList(currentPlayer(game)); });
  node.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    e.preventDefault();
    if (game && !game.over) showDeckList(currentPlayer(game));
  });
}
document.getElementById('restartBtn').addEventListener('click', () => {
  game = null;
  shownPlayer = null;
  prevRender = null;
  showScreen('setup');
  renderSetup();
});

renderSetup();
