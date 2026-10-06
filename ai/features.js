'use strict';
// AI の特徴量（docs/ai-design.md §2・§3）。画面・音に触らない。
// 見える情報（自分の手札・山札の中身、場、サプライ、捨て札、廃棄置き場、相手の枚数）だけから作る。
//   encode(game, me)            … 状態 base（me の席から見た）
//   buyCandidates(base)         … 買う（財源を足して買う・イベント・何も買わない）の候補
//   gainCandidates(base, q)     … 効果での獲得（supply の問い）の候補
//   postState(base, cand)       … 候補を選んだあとの状態（特徴量の上で作る。エンジンは動かさない）
// 他の人の手札・山札（枚数だけ）、自分の山札の並びは使わない。test/ai-hidden.mjs で確かめている。
import { CARDS, HOOKS, allCards, costOf, canBuy, canBuyEvent, emptyPiles, score } from '../engine.js';
import { feats } from '../cpu.js';

export const KIND = { buy: 0, gain: 1, event: 2, none: 3 };
export const KINDS = 4;

// ---- カードの性質（P 次元）----
export const TYPES = ['action', 'treasure', 'victory', 'curse', 'attack', 'duration', 'reaction', 'night', 'command', 'ruins', 'reward', 'reserve',
  'event', 'landmark', 'project', 'way', 'ally', 'trait', 'prophecy', 'shelter'];
export const PROP_NAMES = [...TYPES.map((t) => `type:${t}`), 'cost/10', 'potion', 'debt/10', 'points/10', 'treasure', 'potionValue',
  'cards/4', 'actions/4', 'buys/4', 'coins/6', 'drawTo/10', 'trash', 'curser', 'gainer', 'terminal'];
export const P = PROP_NAMES.length;
const propCache = new Map();
export function cardProps(id) {
  let v = propCache.get(id);
  if (v) return v;
  v = new Float32Array(P);
  const c = CARDS[id];
  if (c) {
    const f = feats(id);
    TYPES.forEach((t, i) => { v[i] = c.types.includes(t) ? 1 : 0; });
    let k = TYPES.length;
    v[k++] = (c.cost || 0) / 10; v[k++] = c.potion ? 1 : 0; v[k++] = (c.debt || 0) / 10; v[k++] = (c.points || 0) / 10;
    v[k++] = c.types.includes('treasure') ? (c.value ?? 1) / 3 : 0; v[k++] = c.potionValue || 0;
    v[k++] = f.cards / 4; v[k++] = f.actions / 4; v[k++] = f.buys / 4; v[k++] = f.coins / 6; v[k++] = f.drawTo / 10;
    v[k++] = f.trash ? 1 : 0; v[k++] = f.curser ? 1 : 0; v[k++] = f.gainer ? 1 : 0; v[k++] = f.terminal ? 1 : 0;
  }
  propCache.set(id, v);
  return v;
}

// ---- 公開された獲得・廃棄の記録（相手のデッキの中身を数える）----
// 対局の始め（全員の山札が公開されている）に startLedger(game) を呼ぶ。game.ledger[席] = { カード id: 枚数 }
// ponytail: 札が山に戻る・別の席に渡る効果は数えない（大使など。数が実際より多くなる）。要るときは HOOKS を足す
let ledgerOn = false;
const bump = (m, id, d) => { m[id] = (m[id] || 0) + d; if (m[id] <= 0) delete m[id]; };
export function startLedger(game) {
  if (!ledgerOn) {
    ledgerOn = true;
    HOOKS.gain.push(function* (g, got) { if (g.ledger && got.to !== 'gone') bump(g.ledger[got.pi], got.id, 1); });
    HOOKS.trash.push(function* (g, player, pi, id) { if (g.ledger) bump(g.ledger[pi], id, -1); });
  }
  game.ledger = game.players.map((p) => { const m = {}; for (const id of allCards(p)) bump(m, id, 1); return m; });
}

// ---- 見える情報だけの game ----
// viewFor（engine.js）と同じ隠し方。ただし viewFor は持続の効果（関数）が残っていると structuredClone で落ちるので、
// 読むものだけ浅く写して手札・山札を {length} にする（複製しないので速い）。同じ結果になることは test/ai-hidden.mjs が見る
export function publicView(game, me) {
  const players = game.players.map((p, i) => {
    if (i === me) return p;
    const mats = {};
    for (const k of Object.keys(p.mats)) mats[k] = k === 'tavern' || k === 'exile' ? p.mats[k] : { length: p.mats[k].length };
    return { ...p, hand: { length: p.hand.length }, deck: { length: p.deck.length }, mats, topKnown: undefined };
  });
  return { ...game, players };
}

const topOf = (g, pile) => (g.stacks && g.stacks[pile] && g.stacks[pile].length ? g.stacks[pile].at(-1) : pile);
const count = (arr) => { const m = new Map(); for (const id of arr) m.set(id, (m.get(id) || 0) + 1); return m; };
const toArr = (m) => Object.entries(m).flatMap(([id, n]) => Array(n).fill(id));

// ---- 状態 ----
export const BAGS = ['myDeck', 'myHand', 'myPlay', 'oppDeck', 'trash'];
export const SCALARS = ['turns', 'oppTurns', 'myScore', 'oppScore', 'scoreDiff', 'emptyPiles', 'provinceLeft', 'colony', 'colonyLeft', 'lateness',
  'myCards', 'myDrawPile', 'myDiscard', 'myHandSize', 'oppCards', 'oppHandSize', 'oppDrawPile',
  'myCoffers', 'myVillagers', 'myDebt', 'myVP', 'oppCoffers', 'oppVillagers', 'oppDebt', 'oppVP',
  'money', 'buys', 'actions', 'potions', 'myTurn', 'players', 'embargoes'];
export const NS = SCALARS.length;
export const SUPPLY_EXT = 4; // 残り/10・コスト/10・禁輸の印/3・勝利点トークン/10

export function encode(game, me) {
  const g = publicView(game, me);
  const n = g.players.length;
  const opp = (me + 1) % n; // ponytail: 相手 1 人（2 人対戦）。3 人以上は次の席だけを見る
  const p = g.players[me];
  const q = g.players[opp];
  const t = g.turn;
  const mine = g.current === me;
  const myAll = [...allCards(p), ...(mine ? g.playArea : [])];
  const oppMap = g.ledger ? g.ledger[opp] : null;
  // 台帳がないときは、見えている場所（捨て札・場・伏せないマット）だけ
  const oppAll = oppMap ? toArr(oppMap) : [...q.discard, ...q.inPlay, ...(q.mats.tavern || []), ...(q.mats.exile || []), ...(g.current === opp ? g.playArea : [])];
  const oppTotal = oppMap ? oppAll.length : oppAll.length + q.hand.length + q.deck.length;
  // 砦（l_donjon）は相手の手札・山札の中身を数えるので、公開の情報だけの game では点に入れない（入れると落ちる）
  const gs = { ...g, landscapes: g.landscapes.filter((id) => id !== 'l_donjon') };
  const myScore = score({ ...p, inPlay: [...p.inPlay, ...(mine ? g.playArea : [])] }, gs);
  const oppScore = score({ ...q, deck: oppAll, hand: [], discard: [], inPlay: [], mats: {} }, gs);

  const big = 'colony' in g.supply ? 'colony' : 'province';
  const full = n === 2 ? 8 : 12;
  const late = Math.max(1 - (g.supply[big] ?? full) / full, emptyPiles(g) / 3);
  const tok = (pl, k) => pl.tokens[k] || 0;
  const S = {
    turns: p.turnsTaken / 20, oppTurns: q.turnsTaken / 20, myScore: myScore / 30, oppScore: oppScore / 30, scoreDiff: (myScore - oppScore) / 30,
    emptyPiles: emptyPiles(g) / 3, provinceLeft: (g.supply.province ?? 0) / full, colony: 'colony' in g.supply ? 1 : 0, colonyLeft: (g.supply.colony ?? 0) / full, lateness: late,
    myCards: myAll.length / 40, myDrawPile: p.deck.length / 30, myDiscard: p.discard.length / 30, myHandSize: p.hand.length / 10,
    oppCards: oppTotal / 40, oppHandSize: q.hand.length / 10, oppDrawPile: q.deck.length / 30,
    myCoffers: tok(p, 'coffers') / 10, myVillagers: tok(p, 'villagers') / 10, myDebt: tok(p, 'debt') / 10, myVP: tok(p, 'vp') / 20,
    oppCoffers: tok(q, 'coffers') / 10, oppVillagers: tok(q, 'villagers') / 10, oppDebt: tok(q, 'debt') / 10, oppVP: tok(q, 'vp') / 20,
    money: mine ? t.money / 10 : 0, buys: mine ? t.buys / 4 : 0, actions: mine ? t.actions / 4 : 0, potions: mine ? t.potions / 4 : 0,
    myTurn: mine ? 1 : 0, players: n / 5, embargoes: Object.values(g.embargo || {}).reduce((a, b) => a + b, 0) / 5,
  };
  const supply = Object.keys(g.supply).map((pile) => {
    const id = topOf(g, pile);
    return { pile, id, left: g.supply[pile], cost: costOf(g, pile), embargo: (g.embargo || {})[pile] || 0, vp: (g.pileVP || {})[pile] || 0 };
  });
  for (const id of g.landscapes) supply.push({ pile: id, id, left: 1, cost: costOf(g, id), embargo: 0, vp: (g.landmarkVP || {})[id] || 0 });
  return {
    me, view: g, scalars: Float32Array.from(SCALARS, (k) => S[k]),
    bags: [count(myAll), count(p.hand), count([...p.inPlay, ...(mine ? g.playArea : [])]), count(oppAll), count(g.trash)],
    supply,
  };
}

export const supplyExt = (s) => [s.left / 10, s.cost / 10, s.embargo / 3, s.vp / 10];
export const bagWeight = (n) => Math.log1p(n);
export const CAND_EXT = 4; // コスト/10・使う財源/8・勝利点/10・属州か植民地か
export function candExt(c) {
  const id = c.id;
  return [c.cost / 10, c.coffers / 8, id ? (CARDS[id].points || 0) / 10 : 0, id === 'province' || id === 'colony' ? 1 : 0];
}

// ---- 候補 ----
// cand = { kind, pile, id（買う・獲得する札。山の一番上）, cost, coffers（先に使う財源の数）}
const mk = (kind, g, pile, coffers = 0) => ({ kind, pile, id: pile == null ? null : topOf(g, pile), cost: pile == null ? 0 : costOf(g, pile), coffers });

export function buyCandidates(base) {
  const g = base.view;
  const t = g.turn;
  const out = [];
  const me = g.players[base.me];
  const coffers = (me.tokens.coffers || 0);
  const more = (ok, pile, kind) => {
    if (ok(g, pile)) { out.push(mk(kind, g, pile)); return; }
    if (!coffers) return;
    const m0 = t.money;
    for (let k = 1; k <= coffers; k++) {
      t.money = m0 + k;
      const hit = ok(g, pile);
      t.money = m0;
      if (hit) { out.push(mk(kind, g, pile, k)); return; }
    }
  };
  if (base.me === g.current && t.phase === 'buy' && t.buys > 0) { // 買えるのは手番の人だけ（相手の手札は見えない）
    for (const pile of Object.keys(g.supply)) if (pile !== 'curse') more(canBuy, pile, KIND.buy);
    for (const id of g.landscapes) if (CARDS[id].buy) more(canBuyEvent, id, KIND.event);
  }
  out.push(mk(KIND.none, g, null));
  return out;
}

export function gainCandidates(base, q) {
  const g = base.view;
  const out = q.options.map((pile) => mk(KIND.gain, g, pile));
  if (q.optional) out.push(mk(KIND.none, g, null));
  return out;
}

// 候補を選んだあとの状態: 自分のデッキに札を 1 枚足し、サプライの山を 1 減らす。ほかの変化（お金・購入・点）は候補の値 candExt から学ぶ
export function postState(base, cand) {
  if (cand.kind !== KIND.buy && cand.kind !== KIND.gain) return base;
  const myDeck = new Map(base.bags[0]);
  myDeck.set(cand.id, (myDeck.get(cand.id) || 0) + 1);
  return {
    ...base, bags: [myDeck, ...base.bags.slice(1)],
    supply: base.supply.map((s) => (s.pile === cand.pile ? { ...s, left: s.left - 1 } : s)),
  };
}
