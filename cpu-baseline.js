'use strict';
// CPU（画面・音に触らない）。2 つの関数だけを画面から使う:
//   nextMove(game, level)   … 手番の人が次にすること { type: 'action'|'shadow'|'villager'|'buyPhase'|'treasure'|'coffers'|'buy'|'event'|'night'|'nightPhase'|'end', id? }
//   answer(game, q, level)  … エンジンの問い q への答え（q.player がこの CPU のとき）
// level: 'weak'（よわい: ほぼでたらめ）/ 'normal'（ふつう: お金と勝利点だけ買う）/ 'strong'（つよい: 王国カードも考えて使う・買う）
// CPU は他の人の手札や山札の順は見ない（自分の手札と、場・サプライなど公開の情報だけを使う）。
import {
  CARDS, is, costOf, canBuy, canBuyEvent, canPlayAction, canPlayNight, shadowsInDeck, currentPlayer, allCards, emptyPiles, pileOf,
  newGame, beginTurn, playAction, playShadow, spendVillager, enterBuyPhase, playTreasureGen, spendCoffers, buyCard, buyEvent,
  enterNightPhase, playNight, endTurn, finalResults, turnController, isTreasureNow,
} from './engine.js';

export const LEVELS = [
  { id: 'weak', name: 'よわい' },
  { id: 'normal', name: 'ふつう' },
  { id: 'strong', name: 'つよい' },
  { id: 'expert', name: 'さいきょう' },
];
const SMART = (level) => level === 'strong' || level === 'expert';

const rnd = (n) => Math.floor(Math.random() * n);
const pick = (arr) => arr[rnd(arr.length)];
const topOf = (game, id) => (game.stacks[id] && game.stacks[id].length ? game.stacks[id].at(-1) : id);

// ---- カードの読み取り（main の「+N カード」などの文言から） ----
const featCache = new Map();
function feats(id) {
  if (featCache.has(id)) return featCache.get(id);
  const c = CARDS[id];
  const text = `${c.main || ''} ${c.desc || ''}`;
  const num = (re) => { const m = text.match(re); return m ? Number(m[1]) : 0; };
  const f = {
    cards: num(/\+(\d+) カード/), actions: num(/\+(\d+) アクション/), buys: num(/\+(\d+) 購入/), coins: num(/\+(\d+) 金/),
    drawTo: num(/(\d+) 枚まで引く/) || num(/(\d+) 枚になるまで引く/),
    trash: /廃棄/.test(text), attack: c.types.includes('attack'), curser: /災い|呪い/.test(text) && c.types.includes('attack'),
    gainer: /獲得/.test(text),
  };
  if (f.drawTo) f.cards = Math.max(f.cards, f.drawTo - 4);
  f.terminal = c.types.includes('action') && f.actions === 0;
  featCache.set(id, f);
  return f;
}

// 終盤の度合い（0 = 序盤、1 = いつ終わってもおかしくない）
function lateness(game) {
  const n = game.players.length;
  const full = n === 2 ? 8 : 12;
  const big = 'colony' in game.supply ? 'colony' : 'province';
  const left = game.supply[big] ?? full;
  const byPiles = emptyPiles(game) / 3;
  return Math.max(1 - left / full, byPiles);
}

// 今の点（勝利点トークンなども含む）
function scoreOf(game, pi) {
  const p = game.players[pi];
  const all = allCards(p);
  return all.reduce((a, id) => a + (CARDS[id].points || 0) + (CARDS[id].pointsFn ? CARDS[id].pointsFn(all) : 0), p.tokens.vp || 0);
}

// 自分のデッキの様子
function deckInfo(game, pi) {
  const p = game.players[pi];
  const all = pi === game.current ? [...allCards(p), ...game.playArea] : allCards(p); // 手番中は場の札も自分の札
  let money = 0;
  let terminals = 0;
  let villages = 0;
  let junk = 0;
  for (const id of all) {
    const c = CARDS[id];
    if (c.types.includes('treasure')) money += c.value || 1;
    if (c.types.includes('action')) { const f = feats(id); money += f.coins; if (f.terminal) terminals += 1; if (f.actions >= 2) villages += 1; }
    if (id === 'curse' || c.types.includes('ruins') || (c.types.includes('victory') && !c.types.includes('action') && !c.types.includes('treasure'))) junk += 1;
  }
  return { size: all.length, money, density: money / Math.max(1, all.length), terminals, villages, junk, all };
}

// ---- カードの値打ち（獲得・手に残す基準） ----
export function cardValue(game, pi, id) {
  id = topOf(game, id);
  const c = CARDS[id];
  if (!c) return 0;
  const late = lateness(game);
  if (id === 'curse') return -8;
  if (c.types.includes('ruins')) return -1;
  const points = (c.points || 0) + (c.pointsFn ? c.pointsFn(allCards(game.players[pi])) : 0);
  const pureVictory = c.types.includes('victory') && !c.types.includes('action') && !c.types.includes('treasure');
  if (pureVictory) return points * (0.4 + 1.6 * late) - (1 - late) * 1.5;
  let v = 0;
  if (c.types.includes('treasure')) v += (c.value || 0) * 1.3 + (c.potionValue ? 2 : 0);
  if (c.types.includes('action') || c.types.includes('night')) {
    const f = feats(id);
    // +アクションは、終点の札（+アクションのない札）が村より多いときだけ値打ちがある
    const info = deckInfo(game, pi);
    const needVillage = info.terminals > info.villages + 1;
    const act = f.actions >= 1 ? 0.6 + (f.actions - 1) * (needVillage ? 1.1 : 0.1) : 0;
    const draw = f.cards * (f.actions >= 1 ? 1.1 : 1.0);
    v += draw + act + f.buys * 0.3 + f.coins * 1.1 + (f.curser ? 3 * (1 - late) : 0) + (f.attack ? 0.4 : 0);
    if (f.terminal && info.terminals >= 1 + info.villages + Math.floor(info.size / 10)) v -= 1.5; // 終点が多すぎるとぶつかる
  }
  // 文言から読めない効果（獲得・廃棄など）は、コストで補う
  const f0 = c.types.includes('action') ? feats(id) : null;
  if (!f0 || (f0.cards + f0.coins + f0.actions + f0.buys) === 0) v = Math.max(v, costOf(game, id) * 0.5 + (c.potion ? 1.5 : 0) + (c.debt ? c.debt * 0.3 : 0));
  v += points * late * 1.5;
  if (id === 'copper') v = 1.3 - late * 0.3 - 0.8;
  return v;
}

// 捨てたい・廃棄したい度合い（大きいほど要らない）
function junkScore(game, pi, id) {
  const c = CARDS[id];
  const late = lateness(game);
  if (id === 'curse') return 10;
  if (c.types.includes('ruins')) return 8;
  if (c.types.includes('shelter') && !c.types.includes('action')) return 6;
  const pureVictory = c.types.includes('victory') && !c.types.includes('action') && !c.types.includes('treasure');
  if (pureVictory) return late > 0.6 ? 2 : 7 - (c.points || 0);
  if (id === 'copper') return deckInfo(game, pi).money > 12 ? 5 : 2;
  return Math.max(0, 5 - cardValue(game, pi, id));
}

// ---- 問いへの答え ----
const BAD_DIR = /捨て(?!札から)|廃棄|渡す|追放|手放|戻す（しなくてもよい）|山に戻す/;
const GOOD_TO_OTHER = /獲得させる|させる 1 枚|捨てさせる/;
function wantedDirection(q, game) {
  const s = q.purpose || '';
  // 他の人の手番に、自分の札を山札の上に置かされる（役人など）→ 要らない札を置く
  if (/山札の上に置く/.test(s) && game && q.player !== game.current) return 'junk';
  if (/獲得させる/.test(s)) return 'worstForThem'; // 相手に渡る札は安いものを
  if (/捨てさせる|廃棄する 1 枚（.*財宝|財宝から廃棄/.test(s) && q.player !== q.owner) return 'bestOfTheirs';
  if (/の財宝から/.test(s)) return 'bestOfTheirs';
  if (/見逃す|手札に入れない/.test(s)) return 'mostCommon';
  if (/当てる|名前を選ぶ|名前を 1 つ/.test(s)) return 'mostCommon';
  if (BAD_DIR.test(s)) return 'junk';
  return 'best';
}

function rankIds(game, pi, ids, dir) {
  const p = game.players[pi];
  const counts = {};
  for (const id of allCards(p)) counts[id] = (counts[id] || 0) + 1;
  const score = (id) => {
    if (dir === 'junk') return junkScore(game, pi, id);
    if (dir === 'worstForThem') return -cardValue(game, pi, id);
    if (dir === 'mostCommon') return counts[id] || 0;
    return cardValue(game, pi, id);
  };
  return ids.map((id, i) => ({ i, s: score(id) })).sort((a, b) => b.s - a.s);
}

function answerPick(game, q, ids, positions, level) {
  const pi = q.player;
  const n = positions.length;
  if (level === 'weak') {
    const k = q.min + rnd(Math.min(q.max - q.min, 2) + 1);
    return [...positions].sort(() => Math.random() - 0.5).slice(0, k);
  }
  const dir = wantedDirection(q, game);
  const ranked = rankIds(game, q.owner ?? pi, ids, dir);
  // 選ばなくてもよいとき: 要らない札・良い札だけを選ぶ
  let k = q.min;
  if (q.max > q.min) {
    if (dir === 'junk') k = Math.max(q.min, Math.min(q.max, ranked.filter((r) => r.s >= (/捨て/.test(q.purpose) ? 5 : 5.5)).length));
    else if (dir === 'best') k = Math.max(q.min, Math.min(q.max, ranked.filter((r) => r.s > 0.5).length));
    else k = Math.max(q.min, Math.min(q.max, 1));
  }
  k = Math.min(k, n);
  return ranked.slice(0, k).map((r) => positions[r.i]);
}

// choose の選択肢の文言に点をつける
function labelScore(game, pi, label, q) {
  const s = String(label);
  let v = 0;
  const num = (re) => { const m = s.match(re); return m ? Number(m[1]) : 0; };
  v += num(/\+(\d+) カード/) * 1.2 + num(/\+(\d+) 金/) * 1.1 + num(/\+(\d+) 購入/) * 0.5;
  v += num(/\+(\d+) アクション/) * (currentPlayer(game).hand.some((id) => is(id, 'action')) ? 0.9 : 0.2);
  if (/金貨を獲得/.test(s)) v += 3;
  if (/銀貨を獲得|銀貨 4 枚/.test(s)) v += 1.6;
  if (/災い|呪い/.test(s)) v -= 4;
  if (/^(しない|使わない|見せない|そのまま|戻さない|捨てない|パス|受けない|取り替えない|やめる|払わない)$/.test(s)) v += 0.3;
  else if (/^(使う|見せる|獲得する|呼び出す|取り替える|受ける|載せる|引く|する|戻す|山札の上へ|はい)/.test(s)) v += 1;
  if (/廃棄して|廃棄する/.test(s) && !/金/.test(s)) v += 0.4;
  if (/ふつうに使う/.test(s)) v += 1.5; // 習性は基本使わない
  if (/借金/.test(s)) v -= num(/借金 (\d+)/) * 0.5;
  if (q.purpose && /関所越え/.test(q.purpose)) return /パス/.test(s) ? 1 : -num(/借金 (\d+)/);
  return v;
}

function answerChoose(game, q, level) {
  const ch = q.choices;
  if (level === 'weak') return pick(ch).value;
  // 数を選ぶ（何枚・何金など）: 過払いは余ったお金があれば全部、ほかは多いほう
  if (ch.every((c) => typeof c.value === 'number')) {
    if (/余分に払い/.test(q.purpose)) return Math.max(...ch.map((c) => c.value));
    if (/入札/.test(q.purpose)) return 0;
    if (/財源をいくつ/.test(q.purpose)) return Math.max(...ch.map((c) => c.value));
    return Math.max(...ch.map((c) => c.value));
  }
  // 衛兵などの「廃棄・捨てる・戻す」: 札の要らなさで決める
  if (q.cards && q.cards.length === 1 && ch.some((c) => c.value === 'trash')) {
    const j = junkScore(game, q.player, q.cards[0]);
    const want = j >= 6 ? 'trash' : j >= 4 ? 'discard' : 'keep';
    const hit = ch.find((c) => c.value === want) || ch.find((c) => c.value === 'keep');
    if (hit) return hit.value;
  }
  // はい・いいえの問いで、対象の札がはっきり要らない／欲しい場合
  const yes = ch.find((c) => c.value === true);
  if (yes && ch.length === 2) {
    const s = q.purpose || '';
    if (/脇に置きますか/.test(s) && q.cards && q.cards[0]) return currentPlayer(game).hand.length >= 5 || game.turn.actions === 0; // 書庫
    if (/捨てますか|捨てさせますか/.test(s) && q.cards && q.cards[0]) {
      const j = junkScore(game, q.owner ?? q.player, q.cards[0]);
      return q.player === q.owner ? j >= 4 : j < 4; // 自分の札は要らなければ捨てる。相手の札は良い札なら捨てさせる
    }
  }
  const scored = ch.map((c) => ({ c, s: labelScore(game, q.player, c.label, q) }));
  scored.sort((a, b) => b.s - a.s);
  return scored[0].c.value;
}

export function answer(game, q, level = 'strong') {
  if (q.type === 'hand') {
    const owner = game.players[q.owner ?? q.player];
    return answerPick(game, q, q.options.map((i) => owner.hand[i]), q.options, level);
  }
  if (q.type === 'cards') return answerPick(game, q, q.cards, q.cards.map((_, i) => i), level);
  if (q.type === 'supply') {
    if (level === 'weak') return q.optional && Math.random() < 0.2 ? null : pick(q.options);
    const dir = wantedDirection(q, game);
    if (/印を置く|借金を 2 つ置く|指定する/.test(q.purpose)) {
      return [...q.options].sort((a, b) => costOf(game, b) - costOf(game, a))[0];
    }
    const ranked = rankIds(game, q.player, q.options, dir === 'junk' ? 'worstForThem' : dir);
    const best = q.options[ranked[0].i];
    if (q.optional && dir === 'best' && ranked[0].s <= 0) return null;
    return best;
  }
  if (q.type === 'choose') return answerChoose(game, q, level);
  return undefined;
}

// 効果が「+N カード」などだけで書かれた札（はっきり強さが読める札）の効果
const PLAIN = /^(\s*\+\d+ (カード|アクション|購入|金)\s*)+$/;
function plainFx(id) {
  const c = CARDS[id];
  if (!c || !c.types.includes('action') || !PLAIN.test(c.main || '')) return null;
  const desc = c.desc || '';
  // 1 回きり・手番を飛ばす札は狙わない
  if (/これを廃棄する|手番を飛ばす|サプライに戻す|山に戻す。/.test(desc)) return null;
  const f = feats(id);
  const curse = c.types.includes('attack') && /災い|呪い/.test(desc);
  const discard = c.types.includes('attack') && /手札が [2-4] 枚になるまで捨てる/.test(desc);
  const m = desc.match(/^手札を (\d+) 枚捨てる/);
  const cost = m ? Number(m[1]) : 0; // 引いたあと必ず捨てる分
  const power = (f.cards - cost) * 1.0 + f.coins * 1.05 + (f.actions >= 1 ? 0.9 : 0) + Math.max(0, f.actions - 1) * 0.2 + f.buys * 0.2 + (curse ? 2.2 : 0) + (discard ? 0.7 : 0);
  return { id, terminal: f.actions === 0, power, curse };
}
// 対局の始めに、狙いの札を 1 つ決める（コスト 5 以下で、効果の読める札のうち一番強いもの）
function targetCard(game) {
  if (game.cpuTarget !== undefined) return game.cpuTarget;
  let best = null;
  for (const pile of Object.keys(game.supply)) {
    const id = topOf(game, pile);
    const fx = plainFx(id);
    if (!fx || CARDS[id].potion || CARDS[id].debt || CARDS[id].cost > 5) continue;
    // +カードの多い終点（鍛冶屋など）か、+アクションのある札が強い。+金だけの終点はそこそこ
    const score = fx.power + (fx.terminal && fx.power < 3 ? -0.8 : 0);
    if (!best || score > best.score) best = { ...fx, pile, score };
  }
  game.cpuTarget = best && best.score >= 2.8 ? best : null;
  return game.cpuTarget;
}

// ---- 手番で次にすること ----
function actionOrder(game, ids) {
  // +アクションのある札を先に（その中では +カードの多いもの）、そのあと引く札、ほかの札
  return [...ids].sort((a, b) => {
    const fa = feats(a);
    const fb = feats(b);
    const va = (fa.actions > 0 ? 100 : 0) + fa.cards * 3 + fa.coins;
    const vb = (fb.actions > 0 ? 100 : 0) + fb.cards * 3 + fb.coins;
    return vb - va;
  });
}

function buyChoice(game, level) {
  const pi = game.current;
  const buyable = Object.keys(game.supply).filter((id) => canBuy(game, id));
  if (!buyable.length) return null;
  if (level === 'weak') {
    const opts = buyable.filter((id) => id !== 'curse' && (costOf(game, id) >= 2 || Math.random() < 0.3));
    return opts.length && Math.random() < 0.85 ? pick(opts) : null;
  }
  const money = game.turn.money - (currentPlayer(game).tokens.debt || 0);
  const late = lateness(game);
  const n = game.players.length;
  const full = n === 2 ? 8 : 12;
  const colony = 'colony' in game.supply;
  const provLeft = game.supply.province;
  const has = (id) => buyable.includes(id);
  const info = deckInfo(game, pi);
  // 勝利点。つよい以上は、最後・最後から 2 枚目の属州で負けないように考える
  if (SMART(level) && has('province') && money >= 8 && !colony) {
    const me = scoreOf(game, pi);
    const best = Math.max(...game.players.map((q, i) => (i === pi ? -99 : scoreOf(game, i))));
    if (provLeft === 1 && me + 6 <= best) return has('duchy') && money >= 5 && me + 3 > best - 6 ? 'duchy' : null; // 最後を取っても負けるなら取らない
    // 最後から 2 枚目: 取ったあと相手が最後の 1 枚を取ると負ける（相手のほうが点が上）なら、公領にしておく
    if (provLeft === 2 && best > me && has('duchy')) return 'duchy';
  }
  if (colony && has('colony') && money >= 11) return 'colony';
  if (has('province') && money >= 8) return 'province';
  // 公領を買い始める時期（属州の残り）。さいきょうは自己対局で決めた値を使う
  const plan0 = SMART(level) && game.cpuPlans ? game.cpuPlans[pi] : null;
  const duchyAt = plan0 && plan0.duchyAt != null ? plan0.duchyAt : (full === 8 ? 4 : 5);
  if (has('duchy') && money >= 5 && provLeft <= duchyAt) return 'duchy';
  if (has('estate') && money >= 2 && provLeft <= 2) return 'estate';
  // 王国カード（つよい・さいきょう）: 対局の始めに自己対局で決めた「狙いの札と枚数」を買う
  if (SMART(level)) {
    const plan = planFor(game, pi, level);
    // 村（+アクション2以上）と引く札（+カード2以上）の組はエンジン: 組み上がるまでは、お金を温存せず最優先で買う
    const isEngine = plan.some((p) => !p.event && feats(topOf(game, p.pile)).actions >= 2)
      && plan.some((p) => !p.event && feats(topOf(game, p.pile)).cards >= 2);
    for (const { pile, limit, event } of plan) {
      if (event) {
        // イベント・プロジェクト: 買える回数（limit）まで、ほかに買う札がないお金で
        game.cpuEvents = game.cpuEvents || {};
        const key = `${pi}:${pile}`;
        if ((game.cpuEvents[key] || 0) < limit && canBuyEvent(game, pile) && money < 8) { game.cpuEvents[key] = (game.cpuEvents[key] || 0) + 1; return `event:${pile}`; }
        continue;
      }
      if (!has(pile)) continue;
      const mine = info.all.filter((id) => pileOf(id) === pile || id === pile).length;
      const cost = costOf(game, pile);
      if (mine >= limit || money < cost) continue;
      if (isEngine && mine < 2) return pile; // 最初の 2 枚は組み上げ優先。そのあとはお金とのかねあい
      if (cost >= 5 ? money < 8 : money < 6) return pile;
    }
  }
  if (colony && has('platinum') && money >= 9) return 'platinum';
  if (has('gold') && money >= 6) return 'gold';
  if (has('silver') && money >= 3) return 'silver';
  if (has('potion') && money >= 4 && SMART(level) && Object.keys(game.supply).some((id) => CARDS[topOf(game, id)].potion)) return 'potion';
  return null;
}

// 次にすることを 1 つ返す。画面・シミュレーションは、これを実行してまた呼ぶ
export function nextMove(game, level = 'strong') {
  const p = currentPlayer(game);
  const t = game.turn;
  if (t.phase === 'action') {
    const acts = p.hand.filter((id) => canPlayAction(game, id));
    const shadows = shadowsInDeck(game).filter((id) => { p.hand.push(id); const ok = canPlayAction(game, id); p.hand.pop(); return ok; });
    if (level === 'weak') {
      if (acts.length && Math.random() < 0.8) return { type: 'action', id: pick(acts) };
      return { type: 'buyPhase' };
    }
    if (level === 'normal') {
      // ふつう: 引く札・お金の札だけ使う（使える間）
      const draws = actionOrder(game, acts).filter((id) => feats(id).cards > 0 || feats(id).coins > 0 || feats(id).actions > 0);
      if (draws.length) return { type: 'action', id: draws[0] };
      return { type: 'buyPhase' };
    }
    if (acts.length) return { type: 'action', id: actionOrder(game, acts)[0] };
    if (shadows.length) return { type: 'shadow', id: actionOrder(game, shadows)[0] };
    if (p.tokens.villagers > 0 && t.actions === 0 && p.hand.some((id) => is(id, 'action'))) return { type: 'villager' };
    return { type: 'buyPhase' };
  }
  if (t.phase === 'buy') {
    const limited = t.handPlayLimit != null && (t.handPlays || 0) >= t.handPlayLimit; // 船出の手番は手札から 3 枚まで
    const tr = limited ? [] : p.hand.filter((id) => isTreasureNow(game, id));
    if (tr.length) return { type: 'treasure', id: tr[0] };
    if (t.buys > 0) {
      const id = buyChoice(game, level);
      if (!id && SMART(level) && (p.tokens.coffers || 0) > 0) {
        // 財源を足すと属州・金に届くなら使う
        const need = [8, 6].find((c) => t.money < c && t.money + p.tokens.coffers >= c);
        if (need) return { type: 'coffers', n: need - t.money };
      }
      if (id && id.startsWith('event:')) return { type: 'event', id: id.slice(6) };
      if (id) return { type: 'buy', id };
    }
    if (p.hand.some((id) => is(id, 'night'))) return { type: 'nightPhase' };
    return { type: 'end' };
  }
  if (t.phase === 'night') {
    const nights = p.hand.filter((id) => canPlayNight(game, id));
    if (nights.length && (level !== 'weak' || Math.random() < 0.7)) return { type: 'night', id: nights[0] };
    return { type: 'end' };
  }
  return { type: 'end' };
}

// ---- 自己対局 ----
// levels[i] の CPU どうしで 1 局打つ。plans[i] があれば、その人の狙いの札はそれに決める（考え直さない）
export function simulate(kingdom, landscapes, levels, plans = [], inner = false) {
  const g = newGame(levels.length, kingdom, levels.map((l, i) => `${l}${i + 1}`), { landscapes });
  g.cpuPlans = {};
  g.cpuPlanning = inner; // 自己対局の中では、決まっていない CPU は考え直さずに BM で打つ
  plans.forEach((pl, i) => { if (pl) g.cpuPlans[i] = pl; });
  const run = (gen) => {
    let st = gen.next();
    for (let k = 0; !st.done; k++) {
      if (k > 3000) throw new Error('問いが終わらない');
      st = gen.next(answer(g, st.value, levels[st.value.player]));
    }
    return st.value;
  };
  for (let turns = 0; !g.over; turns++) {
    if (turns > 300) return null; // 終わらない対局は数えない
    run(beginTurn(g));
    const lv = levels[turnController(g)];
    for (let steps = 0; steps < 400; steps++) {
      const m = nextMove(g, lv);
      if (m.type === 'action') run(playAction(g, m.id));
      else if (m.type === 'shadow') run(playShadow(g, m.id));
      else if (m.type === 'villager') spendVillager(g);
      else if (m.type === 'buyPhase') run(enterBuyPhase(g));
      else if (m.type === 'treasure') run(playTreasureGen(g, m.id));
      else if (m.type === 'coffers') spendCoffers(g, m.n);
      else if (m.type === 'buy') { if (!run(buyCard(g, m.id))) break; }
      else if (m.type === 'event') run(buyEvent(g, m.id));
      else if (m.type === 'nightPhase') enterNightPhase(g);
      else if (m.type === 'night') run(playNight(g, m.id));
      else break;
    }
    run(endTurn(g));
  }
  return g;
}

// 狙いの札の候補（サプライの、勝利点・基本の財宝以外。借金・ポーションの札は除く）
function candidates(game) {
  const out = [];
  for (const pile of Object.keys(game.supply)) {
    const id = topOf(game, pile);
    const c = CARDS[id];
    if (!c || ['copper', 'silver', 'gold', 'platinum', 'potion', 'curse'].includes(id)) continue;
    if (c.types.includes('victory') && !c.types.includes('action') && !c.types.includes('treasure')) continue;
    if (c.types.includes('ruins') || c.potion || c.debt || c.cost > 7) continue;
    const terminal = c.types.includes('action') && feats(id).terminal;
    for (const limit of terminal ? [1, 2, 3] : [2, 6]) out.push([{ pile, limit }]);
  }
  // イベント・プロジェクト（1 回だけ・借金や 0 金のものは除く）
  for (const id of game.landscapes) {
    const c = CARDS[id];
    if (!c.buy || c.debt || c.cost === 0 || c.cost > 8) continue;
    out.push([{ pile: id, limit: 1, event: true }]);
  }
  return out;
}

// 狙いの札と枚数を自己対局で決める（その対局で 1 回だけ。結果は game.cpuPlans に残す）
export function planFor(game, pi, level) {
  game.cpuPlans = game.cpuPlans || {};
  if (game.cpuPlans[pi]) return game.cpuPlans[pi];
  if (game.cpuPlanning) return []; // 自己対局の中では考え直さない（決めていなければ BM）
  game.cpuPlanning = true;
  const n = level === 'expert' ? 8 : 6;
  const kingdom = game.kingdom.filter((id) => id in game.supply || game.stacks[id]);
  const landscapes = game.landscapes;
  // rival があれば、相手もその狙いで打つつよい CPU（なければ ふつう）
  const score = (plan, games = n, rival = null) => {
    let win = 0;
    let played = 0;
    for (let k = 0; k < games; k++) {
      const me = k % 2;
      const other = rival ? 'strong' : 'normal';
      const levels = me === 0 ? ['strong', other] : [other, 'strong'];
      const plans = me === 0 ? [plan, rival] : [rival, plan];
      let sg;
      try { sg = simulate(kingdom, landscapes, levels, plans, true); } catch { sg = null; }
      if (!sg) continue;
      played++;
      const r = finalResults(sg);
      const top = r.filter((x) => x.rank === 1);
      if (top.some((x) => x.index === me)) win += top.length === 1 ? 1 : 0.5;
    }
    return played ? win / played : 0;
  };
  // 効果の読める札の見積もり（targetCard）で選んだ札は、自己対局の数が少なくてぶれるぶんを少し足しておく
  const guess = targetCard(game);
  let results = candidates(game).map((plan) => ({ plan, s: score(plan) + (guess && plan[0].pile === guess.pile ? 0.1 : 0) }));
  results.sort((a, b) => b.s - a.s);
  // さいきょう: 上位 6 つをもっと多く試し直し、上位 3 つの組み合わせも試す
  if (level === 'expert' && results.length) {
    // 1 段目の一番を相手にして、上位を試し直す（強い相手にも勝てる狙いを選ぶ）
    const rival = results[0].plan;
    // 村（+アクション2以上）・引く札（+カード2以上）は単独では成績が悪く上位 6 に残らないことがあるが、
    // 組ませる相手がいれば強い（エンジン）ので、1 つずつは必ず試し直す候補に入れておく
    const solo = (r) => r.plan.length === 1 && !r.plan[0].event;
    // 山ごとに一番良い枚数だけ残す（村・引く札の候補を山の種類で見るため）
    const bestByPile = (pred) => {
      const byPile = new Map();
      for (const r of results) {
        if (!solo(r) || !pred(r)) continue;
        const pile = r.plan[0].pile;
        if (!byPile.has(pile) || byPile.get(pile).s < r.s) byPile.set(pile, r);
      }
      return [...byPile.values()].sort((a, b) => b.s - a.s);
    };
    const villages = bestByPile((r) => feats(topOf(game, r.plan[0].pile)).actions >= 2).slice(0, 2);
    const draws = bestByPile((r) => feats(topOf(game, r.plan[0].pile)).cards >= 2).slice(0, 2);
    const village = villages[0];
    const draw = draws[0];
    let shortlist = results.slice(0, 6);
    for (const r of [...villages, ...draws]) if (r && !shortlist.includes(r)) shortlist = [...shortlist, r];
    const top = shortlist.map((r) => ({ plan: r.plan, s: r.plan === rival ? 0.5 : score(r.plan, 24, rival) }));
    const tops = [...top].sort((a, b) => b.s - a.s).slice(0, 3);
    for (let a = 0; a < tops.length; a++) for (let b = a + 1; b < tops.length; b++) {
      if (tops[a].plan[0].pile === tops[b].plan[0].pile) continue;
      const plan = [tops[a].plan[0], tops[b].plan[0]];
      top.push({ plan, s: score(plan, 24, rival) });
    }
    // 村・引く札は単独では弱くて上位 3 に残らないことが多いが、組ませて初めて強い（エンジン）ので、
    // 上位 2 つずつの組はいつも試す（片方しか上位に残らなくても）
    for (const v of villages) for (const d of draws) {
      if (v.plan[0].pile === d.plan[0].pile) continue;
      const plan = [v.plan[0], d.plan[0]];
      if (top.some((r) => r.plan.length === 2 && r.plan.every((x) => plan.some((y) => y.pile === x.pile)))) continue;
      top.push({ plan, s: score(plan, 24, rival) });
    }
    results = top.sort((a, b) => b.s - a.s);
    // 村＋引く札の組（エンジン）は、単独で決めた枚数では足りないことが多いので、枚数も試し直す
    if (results[0] && results[0].plan.length === 2) {
      const [a, b] = results[0].plan;
      const villagePart = !a.event && feats(topOf(game, a.pile)).actions >= 2 ? a : !b.event && feats(topOf(game, b.pile)).actions >= 2 ? b : null;
      const drawPart = !a.event && feats(topOf(game, a.pile)).cards >= 2 ? a : !b.event && feats(topOf(game, b.pile)).cards >= 2 ? b : null;
      if (villagePart && drawPart && villagePart !== drawPart) {
        const base0 = results[0];
        for (const vl of [2, 3, 4]) for (const dl of [2, 3, 4]) {
          if (vl === villagePart.limit && dl === drawPart.limit) continue;
          const plan = [{ pile: villagePart.pile, limit: vl }, { pile: drawPart.pile, limit: dl }];
          const sc = score(plan, 24, rival);
          if (sc > base0.s) results.push({ plan, s: sc });
        }
        results.sort((a2, b2) => b2.s - a2.s);
      }
    }
    // 公領を買い始める時期も試す（ふつうは属州の残り 4 枚から）
    const base = results[0];
    if (base && base.plan.length) {
      for (const d of [2, 3, 5, 6]) {
        const plan = Object.assign([...base.plan], { duchyAt: d });
        const sc = score(plan, 24, rival);
        if (sc > base.s) results.unshift({ plan, s: sc });
      }
      results.sort((a, b) => b.s - a.s);
    }
  }
  const best = results[0];
  game.cpuPlans[pi] = best && (level === 'expert' ? best.s >= 0.5 : best.s > 0.5) ? best.plan : [];
  game.cpuPlanning = false;
  return game.cpuPlans[pi];
}
