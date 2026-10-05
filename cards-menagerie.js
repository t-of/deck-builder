'use strict';
// 拡張「移動動物園」のカード（王国 30 種・馬）、イベント 20 種、習性 19 種。名前は本家と別の言い回し。
// 追放: player.mats.exile。同じ札を獲得したとき、追放の同じ札をすべて捨て札にしてよい。
// 習性（way）: アクションを使うとき、札の効果の代わりに習性の効果で使ってよい（engine の playAction）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, treasureEffect, later, returnCard, returnToPile, currentPlayer,
  takeFromSupply, kingdomPool, shuffle, emptyPiles, pileOf, supplyOptions, playTreasureGen,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const exileOf = (p) => (p.mats.exile = p.mats.exile || []);
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
// サプライから 1 枚を追放する
function exileFromSupply(g, p, id) {
  const c = id && takeFromSupply(g, id);
  if (!c) return null;
  exileOf(p).push(c);
  log(g, `${p.name}が${nm(c)}を追放した。`);
  return c;
}
function* horses(g, pi, n, to = 'discard') { for (let k = 0; k < n; k++) yield* gain(g, pi, 'pony', to); }
// 場以外の札を今すぐ使う（手札・山札・捨て札などから取り出した札）
function* playNow(g, pi, id) {
  g.playArea.push(id);
  log(g, `${g.players[pi].name}が${nm(id)}を使用。`);
  if (is(id, 'action')) yield* resolve(g, id); else yield* treasureEffect(g, id);
}

const pony = {
  id: 'pony', name: '馬', cost: 3, notSupply: true, main: '+2 カード\n+1 アクション', desc: 'これを馬の山に戻す',
  *play(g, p) { drawCards(p, 2); g.turn.actions += 1; returnToPile(g, 'pony'); },
};

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'nightcat', name: '黒猫', types: ['action', 'attack', 'reaction'], cost: 2, main: '+2 カード', desc: '自分の手番でなければ、他の人は呪いを獲得する。他の人が勝利点カードを獲得したとき、手札から使ってよい',
    *play(g, p, pi) {
      drawCards(p, 2);
      if (pi === g.current) return;
      const n = g.players.length;
      for (let k = 1; k < n; k++) yield* gain(g, (pi + k) % n, 'curse');
    },
  },
  { id: 'sled', name: 'そり', types: ['action', 'reaction'], cost: 2, main: '馬を 2 枚獲得', desc: 'カードを獲得したとき、これを捨てて、獲得した札を手札か山札の上に置いてよい', *play(g, p, pi) { yield* horses(g, pi, 2); } },
  { id: 'provisions', name: '配給品', types: ['treasure'], cost: 2, value: 1, autoPlay: true, main: '+1 金', desc: '使うと馬を 1 枚、山札の上に獲得する', *play(g, p, pi) { yield* horses(g, pi, 1, 'deck'); } },
  // ---- コスト 3 ----
  {
    id: 'caravan2', name: 'ラクダの隊列', cost: 3, main: 'サプライから追放', desc: 'サプライの勝利点以外を 1 枚追放する。獲得したとき、サプライの金貨を 1 枚追放する',
    *play(g, p, pi) { exileFromSupply(g, p, yield* askSupply(g, pi, '追放する札（勝利点以外）', 99, (id) => !is(id, 'victory'))); },
    *onGain(g, got) { exileFromSupply(g, g.players[got.pi], 'gold'); },
  },
  {
    id: 'goatkeeper', name: 'ヤギ飼い', cost: 3, main: '+1 アクション', desc: '手札を 1 枚廃棄してよい。右の人が前の手番に廃棄した枚数だけ +カード',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1);
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
      drawCards(p, g.players[(pi - 1 + g.players.length) % g.players.length].lastTrashed || 0);
    },
  },
  {
    id: 'scrapiron', name: 'がらくた', cost: 3, main: '廃棄して選ぶ', desc: '手札を 1 枚廃棄し、そのコスト 1 につき、+1 カード / +1 アクション / +1 購入 / +1 金 / 銀貨を獲得 / 馬を獲得 からちがうものを 1 つずつ',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      let left = [{ value: 'c', label: '+1 カード' }, { value: 'a', label: '+1 アクション' }, { value: 'b', label: '+1 購入' }, { value: 'm', label: '+1 金' }, { value: 's', label: '銀貨を獲得' }, { value: 'h', label: '馬を獲得' }];
      for (let k = Math.min(6, costOf(g, id)); k > 0; k--) {
        const v = yield* askChoose(g, pi, `選ぶ（あと ${k}）`, left);
        left = left.filter((c) => c.value !== v);
        if (v === 'c') drawCards(p, 1); else if (v === 'a') g.turn.actions += 1; else if (v === 'b') g.turn.buys += 1;
        else if (v === 'm') g.turn.money += 1; else if (v === 's') yield* gain(g, pi, 'silver'); else yield* horses(g, pi, 1);
      }
    },
  },
  { id: 'herddog', name: '牧羊犬', types: ['action', 'reaction'], cost: 3, main: '+2 カード', desc: 'カードを獲得したとき、手札から使ってよい', *play(g, p) { drawCards(p, 2); } },
  {
    id: 'snowvillage', name: '雪深い村', cost: 3, main: '+1 カード　+4 アクション\n+1 購入', desc: 'この手番、このあと得る +アクションはすべて無効になる',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 4; g.turn.buys += 1;
      // これより後の +アクションを無視する（減るのはそのまま）
      const t = g.turn;
      let a = t.actions;
      Object.defineProperty(t, 'actions', { get: () => a, set: (v) => { if (v < a) a = v; }, configurable: true, enumerable: true });
    },
  },
  { id: 'hoardpile', name: '備蓄品', types: ['treasure'], cost: 3, value: 3, autoPlay: true, main: '+3 金　+1 購入', desc: '使うと、これを追放する',
    *play(g, p) { g.turn.buys += 1; const at = g.playArea.lastIndexOf('hoardpile'); if (at >= 0) exileOf(p).push(...g.playArea.splice(at, 1)); } },
  // ---- コスト 4 ----
  {
    id: 'bountyman', name: '賞金稼ぎ', cost: 4, main: '+1 アクション', desc: '手札を 1 枚追放する。追放に同じ札がなかったら +3 金',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '追放する 1 枚', 1, 1));
      if (!id) return;
      const first = !exileOf(p).includes(id);
      exileOf(p).push(id);
      if (first) g.turn.money += 3;
    },
  },
  {
    id: 'archbishop', name: '枢機卿', types: ['action', 'attack'], cost: 4, main: '+2 金', desc: '他の人は山札の上 2 枚をめくり、コスト 3〜6 の 1 枚を追放し、残りを捨てる',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 2);
        const idx = shown.map((id, i) => (costOf(g, id) >= 3 && costOf(g, id) <= 6 ? i : -1)).filter((i) => i >= 0);
        if (idx.length) {
          const pick = idx.length === 1 ? idx[0] : idx[(yield* askCards(g, ti, '追放する 1 枚', idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
          exileOf(t).push(...shown.splice(pick, 1));
        }
        yield* discardCards(g, t, shown, true);
      });
    },
  },
  {
    id: 'horsemen', name: '騎兵隊', cost: 4, main: '馬を 2 枚獲得', desc: '獲得したとき +2 カード +1 購入。購入フェイズならアクションフェイズに戻る',
    *play(g, p, pi) { yield* horses(g, pi, 2); },
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      drawCards(g.players[got.pi], 2); g.turn.buys += 1;
      if (g.turn.phase === 'buy') { g.turn.phase = 'action'; log(g, 'アクションフェイズに戻った。'); }
    },
  },
  {
    id: 'stablehand', name: '馬丁', cost: 4, main: 'コスト 4 以下を獲得', desc: 'それがアクションなら馬、財宝なら銀貨を獲得する。勝利点なら +1 カード +1 アクション',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4);
      if (!(yield* gain(g, pi, id))) return;
      if (is(id, 'action')) yield* horses(g, pi, 1);
      if (is(id, 'treasure')) yield* gain(g, pi, 'silver');
      if (is(id, 'victory')) { drawCards(p, 1); g.turn.actions += 1; }
    },
  },
  {
    id: 'hostel', name: '旅籠', cost: 4, main: '+1 カード\n+2 アクション', desc: '獲得したとき、財宝を好きな枚数見せて捨て、同じ枚数の馬を獲得してよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onGain(g, got) {
      const p = g.players[got.pi];
      const idx = yield* askHand(g, got.pi, '捨てる財宝（1 枚につき馬）', 0, p.hand.length, (id) => is(id, 'treasure'));
      yield* discardCards(g, p, takeFromHand(p, idx));
      yield* horses(g, got.pi, idx.length);
    },
  },
  {
    id: 'commons', name: '村有緑地', types: ['action', 'duration', 'reaction'], cost: 4, main: '+1 カード\n+2 アクション', desc: '今か次の手番の始めに +1 カード +2 アクション。片付け以外で捨て札にしたとき、使ってよい',
    *play(g, p, pi) {
      const fx = function* () { drawCards(p, 1); g.turn.actions += 2; };
      if (pi !== g.current || (yield* askYesNo(g, pi, 'いつ受けますか？', '今', '次の手番の始め'))) yield* fx();
      else later(g, 'commons', fx);
    },
    *onDiscard(g, p, pi) {
      if (!(yield* askYesNo(g, pi, '捨てた「村有緑地」を使いますか？', '使う', '使わない', ['commons']))) return;
      const k = p.discard.lastIndexOf('commons');
      if (k >= 0) { p.discard.splice(k, 1); yield* playOutOfTurn(g, pi, 'commons'); }
    },
  },
  // ---- コスト 5 ----
  {
    id: 'riverboat', name: '艀', types: ['action', 'duration'], cost: 5, main: '+3 カード\n+1 購入', desc: '今か次の手番の始めに +3 カード +1 購入',
    *play(g, p, pi) {
      const fx = function* () { drawCards(p, 3); g.turn.buys += 1; };
      if (yield* askYesNo(g, pi, 'いつ受けますか？', '今', '次の手番の始め')) yield* fx(); else later(g, 'riverboat', fx);
    },
  },
  {
    id: 'witchmeet', name: '魔女の集会', types: ['action', 'attack'], cost: 5, main: '+1 アクション\n+2 金', desc: '他の人はサプライの呪いを 1 枚追放する。できなければ、追放している呪いをすべて捨て札にする',
    *play(g) {
      g.turn.actions += 1; g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (!exileFromSupply(g, t, 'curse')) {
          const ex = exileOf(t);
          const cs = ex.filter((id) => id === 'curse');
          t.mats.exile = ex.filter((id) => id !== 'curse');
          yield* discardCards(g, t, cs, true);
        }
      });
    },
  },
  {
    id: 'evict', name: '強制退去', cost: 5, main: '追放して獲得', desc: '手札を 1 枚追放し、それとちがう名前でコスト +2 以下の札を獲得する',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '追放する 1 枚', 1, 1));
      if (!id) return;
      exileOf(p).push(id);
      const max = costOf(g, id) + 2;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下（ちがう名前）を獲得`, max, (x) => x !== id));
    },
  },
  { id: 'falconer', name: '鷹匠', types: ['action', 'reaction'], cost: 5, main: '安い札を手札に', desc: 'これより安い札を手札に獲得する。誰かが種類を 2 つ以上持つ札を獲得したとき、手札から使ってよい',
    *play(g, p, pi) { const c = costOf(g, 'falconer'); if (c > 0) yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下を手札に獲得`, c - 1), 'hand'); } },
  { id: 'angler', name: '漁師', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: '自分の手番、捨て札がなければコストが 3 下がる',
    costAdjust: (g) => (g.players && g.players[g.current] && !g.players[g.current].discard.length ? 3 : 0),
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1; } },
  {
    id: 'warder', name: '門番', types: ['action', 'duration', 'attack'], cost: 5, main: '次の手番に\n+3 金', desc: '次の手番の始めまで、他の人が追放にないアクションか財宝を獲得すると、それを追放する',
    *play(g) {
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.warder = (g.players[ti].tokens.warder || 0) + 1; });
      later(g, 'warder', function* () { for (const ti of hit) g.players[ti].tokens.warder -= 1; g.turn.money += 3; });
    },
  },
  {
    id: 'huntlodge', name: '狩猟小屋', cost: 5, main: '+1 カード\n+2 アクション', desc: '手札をすべて捨ててよい。そうしたら +5 カード',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 2;
      if (yield* askYesNo(g, pi, '手札をすべて捨てて 5 枚引きますか？', '引き直す', 'しない')) { yield* discardCards(g, p, p.hand.splice(0)); drawCards(p, 5); }
    },
  },
  { id: 'kiln', name: '炉', cost: 5, main: '+2 金', desc: 'この手番、次に札を使うとき、先に同じ札を獲得してよい', *play(g) { g.turn.money += 2; g.turn.kiln = (g.turn.kiln || 0) + 1; } },
  { id: 'livery', name: '貸し馬屋', cost: 5, main: '+3 金', desc: 'この手番、コスト 4 以上を獲得するたびに馬を獲得する', *play(g) { g.turn.money += 3; g.turn.livery = (g.turn.livery || 0) + 1; } },
  {
    id: 'ringleader', name: '首謀者', types: ['action', 'duration'], cost: 5, main: '次の手番に\nアクションを 3 回', desc: '次の手番の始めに、手札のアクションを 1 枚 3 回使ってよい',
    *play(g, p, pi) {
      later(g, 'ringleader', function* () {
        const [i] = yield* askHand(g, pi, '3 回使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
        if (i == null) return;
        const [id] = takeFromHand(p, [i]);
        g.playArea.push(id);
        for (let k = 0; k < 3; k++) yield* resolve(g, id);
      });
    },
  },
  { id: 'corral', name: 'パドック', cost: 5, main: '+2 金\n馬を 2 枚', desc: '空のサプライの山 1 つにつき +1 アクション', *play(g, p, pi) { g.turn.money += 2; yield* horses(g, pi, 2); g.turn.actions += emptyPiles(g); } },
  {
    id: 'refuge', name: '聖域', cost: 5, main: '+1 カード　+1 アクション\n+1 購入', desc: '手札を 1 枚追放してよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1;
      const [i] = yield* askHand(g, pi, '追放する 1 枚（しなくてもよい）', 0, 1);
      if (i != null) exileOf(p).push(...takeFromHand(p, [i]));
    },
  },
  // ---- コスト 6〜7 ----
  { id: 'warhorse', name: 'デストリエ', cost: 6, main: '+2 カード\n+1 アクション', desc: '自分の手番、この手番に獲得した札 1 枚につきコストが 1 下がる',
    costAdjust: (g) => (g.turn ? g.turn.gained.length : 0),
    *play(g, p) { drawCards(p, 2); g.turn.actions += 1; } },
  { id: 'traveler2', name: '行人', cost: 6, main: '+3 カード', desc: '銀貨を獲得してよい。このコストは、この手番に最後に獲得したほかの札と同じになる',
    costAdjust: (g) => { const last = g.turn && [...g.turn.gained].reverse().find((id) => id !== 'traveler2'); return last ? 6 - costOf(g, last) : 0; },
    *play(g, p, pi) { drawCards(p, 3); if (yield* askYesNo(g, pi, '銀貨を獲得しますか？', '獲得する', 'しない')) yield* gain(g, pi, 'silver'); } },
  {
    id: 'beastfair', name: '動物見本市', cost: 7, main: '+4 金', desc: '空のサプライの山 1 つにつき +1 購入。お金の代わりに、手札のアクションを 1 枚廃棄して買ってもよい',
    altCost: (g) => g.players[g.current].hand.some((id) => is(id, 'action')),
    *payAlt(g, p, pi) { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄するアクション（動物見本市の代わりに）', 1, 1, (id) => is(id, 'action')))); },
    *play(g) { g.turn.money += 4; g.turn.buys += emptyPiles(g); },
  },
];

// ---- イベント ----
const E = ['event'];
const events = [
  { id: 'm_delay', name: '遅延', types: E, cost: 0, main: 'アクションを次の手番に', desc: '手札のアクションを 1 枚脇に置いてよい。次の手番の始めにそれを使う',
    *buy(g, p, pi) {
      const [i] = yield* askHand(g, pi, '脇に置くアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      (p.mats.delay = p.mats.delay || []).push(id);
      p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.delay.indexOf(id); if (k < 0) return; pp.mats.delay.splice(k, 1); yield* playNow(gg, ppi, id); });
    } },
  { id: 'm_despair', name: '絶望', types: E, cost: 0, once: true, main: '呪いで +1 購入 +2 金', desc: '1 手番に 1 度: 呪いを獲得してよい。そうしたら +1 購入 +2 金',
    *buy(g, p, pi) { if ((yield* askYesNo(g, pi, '呪いを獲得しますか？', '獲得する', 'しない')) && (yield* gain(g, pi, 'curse'))) { g.turn.buys += 1; g.turn.money += 2; } } },
  { id: 'm_gamble', name: '博打', types: E, cost: 2, main: '+1 購入', desc: '山札の一番上をめくる。財宝かアクションなら使ってよい。そうでなければ捨てる',
    *buy(g, p, pi) {
      g.turn.buys += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if ((is(id, 'treasure') || is(id, 'action')) && (yield* askYesNo(g, pi, `${nm(id)}を使いますか？`, '使う', '捨てる', [id]))) yield* playNow(g, pi, id);
      else yield* discardCards(g, p, [id], true);
    } },
  { id: 'm_pursue', name: '追求', types: E, cost: 2, main: '+1 購入', desc: '名前を 1 つ言い、山札の上 4 枚をめくる。その名前の札は山札の上に戻し、残りを捨てる',
    *buy(g, p, pi) {
      g.turn.buys += 1;
      const names = [...new Set([...p.deck, ...p.discard, ...p.hand])];
      if (!names.length) return;
      const [k] = yield* askCards(g, pi, '名前を選ぶ', names, 1, 1);
      const shown = reveal(p, 4);
      yield* discardCards(g, p, shown.filter((id) => id !== names[k ?? 0]), true);
      for (const id of shown.filter((x) => x === names[k ?? 0])) putOnDeck(p, id);
    } },
  { id: 'm_ride', name: '乗馬', types: E, cost: 2, main: '馬を獲得', desc: '', *buy(g, p, pi) { yield* horses(g, pi, 1); } },
  { id: 'm_toil', name: '苦労', types: E, cost: 2, main: '+1 購入', desc: '手札のアクションを 1 枚使ってよい',
    *buy(g, p, pi) { g.turn.buys += 1; const [i] = yield* askHand(g, pi, '使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action')); if (i != null) yield* playNow(g, pi, takeFromHand(p, [i])[0]); } },
  { id: 'm_enhance', name: '増大', types: E, cost: 3, main: '格上げ', desc: '手札の勝利点以外を 1 枚廃棄してよい。そうしたら、そのコスト +2 以下を獲得する',
    *buy(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する札（勝利点以外・しなくてもよい）', 0, 1, (x) => !is(x, 'victory')));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 2;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得`, max));
    } },
  { id: 'm_march', name: '進軍', types: E, cost: 3, main: '捨て札のアクションを使う', desc: '捨て札を見て、アクションを 1 枚使ってよい',
    *buy(g, p, pi) {
      const acts = p.discard.filter((id) => is(id, 'action'));
      const [i] = yield* askCards(g, pi, '使うアクション（なしでもよい）', acts, 0, 1);
      if (i == null) return;
      p.discard.splice(p.discard.indexOf(acts[i]), 1);
      yield* playNow(g, pi, acts[i]);
    } },
  { id: 'm_transport', name: '輸送', types: E, cost: 3, main: 'アクションを追放\nか山札へ', desc: 'サプライのアクションを 1 枚追放するか、追放しているアクションを 1 枚山札の上に置く',
    *buy(g, p, pi) {
      const ex = exileOf(p).filter((id) => is(id, 'action'));
      if (ex.length && (yield* askYesNo(g, pi, 'どちらにしますか？', '追放から山札の上へ', 'サプライから追放'))) {
        const [i] = yield* askCards(g, pi, '山札の上に置く札', ex, 1, 1);
        const id = ex[i ?? 0];
        p.mats.exile.splice(p.mats.exile.indexOf(id), 1);
        putOnDeck(p, id);
        return;
      }
      exileFromSupply(g, p, yield* askSupply(g, pi, '追放するアクション', 99, (id) => is(id, 'action')));
    } },
  { id: 'm_banish', name: '放逐', types: E, cost: 4, main: '同じ札をまとめて追放', desc: '手札の同じ名前の札を好きな枚数追放する',
    *buy(g, p, pi) {
      const [i] = yield* askHand(g, pi, '追放する札の名前（1 枚選ぶ）', 0, 1);
      if (i == null) return;
      const id = p.hand[i];
      const same = p.hand.map((x, k) => (x === id ? k : -1)).filter((k) => k >= 0);
      const n = yield* askChoose(g, pi, `${nm(id)}を何枚追放しますか？`, same.map((_, k) => ({ value: k + 1, label: `${k + 1} 枚` })), [id]);
      exileOf(p).push(...takeFromHand(p, same.slice(0, n)));
    } },
  { id: 'm_bargain', name: '特価品', types: E, cost: 4, main: 'コスト 5 以下', desc: 'コスト 5 以下の勝利点以外を獲得する。他の人は馬を獲得する',
    *buy(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下（勝利点以外）を獲得', 5, (id) => !is(id, 'victory'))); yield* eachOther(g, (ti) => horses(g, ti, 1)); } },
  { id: 'm_invest', name: '投資', types: E, cost: 4, main: 'アクションを追放', desc: 'サプライのアクションを 1 枚追放する。それが追放にあるあいだ、他の人が同じ札を獲得するか投資するたびに +2 カード',
    *buy(g, p, pi) {
      const id = exileFromSupply(g, p, yield* askSupply(g, pi, '投資するアクション', 99, (x) => is(x, 'action')));
      if (!id) return;
      (p.tokens.invest = p.tokens.invest || []).push(id);
      // 他の人がすでに同じ札に投資していれば、その人は +2 カード
      g.players.forEach((q, k) => { if (k !== pi && (q.tokens.invest || []).includes(id) && exileOf(q).includes(id)) drawCards(q, 2); });
    } },
  { id: 'm_seize', name: '今を生きる', types: E, cost: 4, main: '追加の手番', desc: '1 ゲームに 1 度: この手番のあとに追加の手番を行う',
    canBuy: (g) => !g.players[g.current].tokens.seized,
    *buy(g, p) { p.tokens.seized = true; if (!g.extraTurn) g.turn.seize = true; } },
  { id: 'm_trade', name: '商売', types: E, cost: 5, main: '獲得した種類だけ金貨', desc: 'この手番に獲得したちがう名前の札 1 種につき金貨を獲得する',
    *buy(g, p, pi) { for (let k = new Set(g.turn.gained).size; k > 0; k--) yield* gain(g, pi, 'gold'); } },
  { id: 'm_demand', name: '要求', types: E, cost: 5, main: '馬とコスト 4 以下を\n山札の上に', desc: '', *buy(g, p, pi) { yield* horses(g, pi, 1, 'deck'); yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を山札の上に獲得', 4), 'deck'); } },
  { id: 'm_stampede', name: '暴走', types: E, cost: 5, main: '馬 5 枚を山札に', desc: '場の札が 5 枚以下なら、馬を 5 枚山札の上に獲得する', *buy(g, p, pi) { if (g.playArea.length <= 5) yield* horses(g, pi, 5, 'deck'); } },
  { id: 'm_reap', name: '刈り入れ', types: E, cost: 7, main: '次の手番に金貨', desc: '金貨を獲得して脇に置く。次の手番の始めにそれを使う',
    *buy(g, p) {
      const c = takeFromSupply(g, 'gold');
      if (!c) return;
      g.turn.gained.push(c);
      (p.mats.reap = p.mats.reap || []).push(c);
      p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.reap.indexOf('gold'); if (k < 0) return; pp.mats.reap.splice(k, 1); yield* playNow(gg, ppi, 'gold'); });
    } },
  { id: 'm_enclave', name: '包領', types: E, cost: 8, main: '金貨を獲得\n公領を追放', desc: '金貨を獲得し、サプライの公領を 1 枚追放する', *buy(g, p, pi) { yield* gain(g, pi, 'gold'); exileFromSupply(g, p, 'duchy'); } },
  { id: 'm_league', name: '同盟', types: E, cost: 10, main: '基本の札を 1 枚ずつ', desc: '属州・公領・屋敷・金貨・銀貨・銅貨を 1 枚ずつ獲得する', *buy(g, p, pi) { for (const id of ['province', 'duchy', 'estate', 'gold', 'silver', 'copper']) yield* gain(g, pi, id); } },
  { id: 'm_populate', name: '植民', types: E, cost: 10, main: 'アクションを 1 枚ずつ', desc: 'サプライのアクションの山から 1 枚ずつ獲得する',
    *buy(g, p, pi) { for (const id of Object.keys(g.supply)) if (is(g.stacks[id] ? (g.stacks[id].at(-1) || id) : id, 'action') && g.supply[id] > 0) yield* gain(g, pi, id); } },
];

// ---- 習性（アクションを使うとき、代わりにこの効果で使ってよい） ----
const W = ['way'];
const way = (id, name, main, use, desc = '') => ({ id, name, types: W, cost: 0, main, desc, use });
const ways = [
  way('w_butterfly', 'チョウの習性', '山に戻して格上げ', function* (g, p, pi, card) {
    if (!returnToPile(g, card)) return;
    const c = costOf(g, card) + 1;
    yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c));
  }, 'その札を山に戻してよい。そうしたら、ちょうどコスト +1 の札を獲得する'),
  way('w_camel', 'ラクダの習性', '金貨を追放', function* (g, p) { exileFromSupply(g, p, 'gold'); }),
  way('w_chameleon', 'カメレオンの習性', '札の効果で\n+カードと+金を入れ替え', function* (g, p, pi, card) {
    // この札の効果のあいだだけ、+カード は +金、+金 は +カード になる
    const t = g.turn;
    const proxy = new Proxy(t, { set(o, k, v) { if (k === 'money' && v > o.money) { const d = v - o.money; o.swapCardsCoins = null; drawCards(p, d); o.swapCardsCoins = o; return true; } o[k] = v; return true; } });
    t.swapCardsCoins = t;
    g.turn = proxy;
    try { yield* resolve(g, card); } finally { g.turn = t; t.swapCardsCoins = null; }
  }, 'この札の効果で得る +カード は +金 に、+金 は +カード になる'),
  way('w_frog', 'カエルの習性', '+1 アクション\n山札の上に戻る', function* (g, p, pi, card) { g.turn.actions += 1; (g.turn.frog = g.turn.frog || []).push(card); }, 'この手番、これを場から捨てるとき山札の上に置く'),
  way('w_goat', 'ヤギの習性', '1 枚廃棄', function* (g, p, pi) { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1))); }),
  way('w_horse', '馬の習性', '+2 カード　+1 アクション\n山に戻す', function* (g, p, pi, card) { drawCards(p, 2); g.turn.actions += 1; returnToPile(g, card); }),
  way('w_mole', 'モグラの習性', '+1 アクション\n手札を捨てて +3 カード', function* (g, p) { g.turn.actions += 1; yield* discardCards(g, p, p.hand.splice(0), true); drawCards(p, 3); }),
  way('w_monkey', 'サルの習性', '+1 購入　+1 金', function* (g) { g.turn.buys += 1; g.turn.money += 1; }),
  way('w_mouse', 'ハツカネズミの習性', '脇の札として使う', function* (g, p, pi) { if (g.mouseCard) { log(g, `${nm(g.mouseCard)}として使う。`); yield* resolve(g, g.mouseCard); } }, '対局の始めに脇に置いたコスト 2〜3 のアクションとして使う'),
  way('w_mule', '騾馬の習性', '+1 アクション　+1 金', function* (g) { g.turn.actions += 1; g.turn.money += 1; }),
  way('w_otter', 'カワウソの習性', '+2 カード', function* (g, p) { drawCards(p, 2); }),
  way('w_owl', 'フクロウの習性', '6 枚まで引く', function* (g, p) { drawCards(p, Math.max(0, 6 - p.hand.length)); }),
  way('w_ox', '雄牛の習性', '+2 アクション', function* (g) { g.turn.actions += 2; }),
  way('w_pig', '豚の習性', '+1 カード　+1 アクション', function* (g, p) { drawCards(p, 1); g.turn.actions += 1; }),
  way('w_rat', 'ドブネズミの習性', '財宝を捨てて複製', function* (g, p, pi, card) {
    const [i] = yield* askHand(g, pi, '捨てる財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
    if (i == null) return;
    yield* discardCards(g, p, takeFromHand(p, [i]));
    yield* gain(g, pi, card in g.supply ? card : pileOf(card));
  }, '財宝を 1 枚捨ててよい。そうしたら、この札と同じ札を獲得する'),
  way('w_seal', 'アザラシの習性', '+1 金\n獲得を山札に', function* (g) { g.turn.money += 1; g.turn.topdeckGains = true; }),
  way('w_sheep', '羊の習性', '+2 金', function* (g) { g.turn.money += 2; }),
  way('w_squirrel', 'リスの習性', '手番の終わりに\n+2 カード', function* (g) { g.turn.extraDraw = (g.turn.extraDraw || 0) + 2; }),
  way('w_turtle', 'ウミガメの習性', '次の手番に使う', function* (g, p, pi, card) {
    const at = g.playArea.lastIndexOf(card);
    if (at < 0) return;
    (p.mats.turtle = p.mats.turtle || []).push(...g.playArea.splice(at, 1));
    p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.turtle.indexOf(card); if (k < 0) return; pp.mats.turtle.splice(k, 1); yield* playNow(gg, ppi, card); });
  }, 'これを脇に置き、次の手番の始めに使う'),
  way('w_worm', 'ミミズの習性', '屋敷を追放', function* (g, p) { exileFromSupply(g, p, 'estate'); }),
];

// ---- 決まり ----
const HORSE_USERS = ['sled', 'provisions', 'scrapiron', 'horsemen', 'stablehand', 'hostel', 'livery', 'corral', 'm_ride', 'm_bargain', 'm_demand', 'm_stampede'];
HOOKS.setup.push((g) => {
  if ([...g.kingdom, ...g.landscapes].some((id) => HORSE_USERS.includes(id))) g.nonSupply.pony = 30;
  if (g.landscapes.includes('w_mouse')) {
    const pool = kingdomPool().filter((id) => !(id in g.supply) && is(id, 'action') && (CARDS[id].cost === 2 || CARDS[id].cost === 3) && CARDS[id].play);
    g.mouseCard = pool.length ? shuffle(pool, g)[0] : null;
  }
});
HOOKS.gain.push(function* (g, got) {
  const p = g.players[got.pi];
  const n = g.players.length;
  // 門番の印: 追放にないアクション・財宝を獲得したら追放
  if (p.tokens.warder > 0 && (is(got.id, 'action') || is(got.id, 'treasure')) && !exileOf(p).includes(got.id) && got.to !== 'gone' && got.to !== 'trash') {
    if (yield* relocate(g, got, 'gone')) { exileOf(p).push(got.id); log(g, `${p.name}の${nm(got.id)}は門番で追放された。`); return; }
  }
  // 追放の同じ札を捨て札にしてよい
  const ex = exileOf(p);
  if (ex.includes(got.id) && (yield* askYesNo(g, got.pi, `追放している${nm(got.id)}をすべて捨て札にしますか？`, '捨て札にする', 'しない', [got.id]))) {
    const same = ex.filter((id) => id === got.id);
    p.mats.exile = ex.filter((id) => id !== got.id);
    p.discard.push(...same);
  }
  // 投資: 他の人がその札を獲得したら +2 カード
  for (let k = 0; k < n; k++) {
    const q = g.players[k];
    if (k !== got.pi && (q.tokens.invest || []).includes(got.id) && exileOf(q).includes(got.id)) drawCards(q, 2);
  }
  // 貸し馬屋
  if (got.pi === g.current && g.turn.livery && costOf(g, got.id) >= 4 && got.id !== 'pony') for (let k = 0; k < g.turn.livery; k++) yield* horses(g, got.pi, 1);
  // 牧羊犬: 獲得したとき手札から使ってよい
  while (p.hand.includes('herddog') && (yield* askYesNo(g, got.pi, '「牧羊犬」を手札から使いますか？', '使う', '使わない', ['herddog']))) {
    p.hand.splice(p.hand.indexOf('herddog'), 1);
    yield* playOutOfTurn(g, got.pi, 'herddog');
  }
  // そり: 捨てて、獲得した札を手札か山札の上へ
  if (p.hand.includes('sled') && got.to !== 'gone' && got.to !== 'trash' && got.to !== 'hand'
    && (yield* askYesNo(g, got.pi, `「そり」を捨てて、${nm(got.id)}を手札か山札の上に置きますか？`, 'する', 'しない', ['sled', got.id]))) {
    yield* discardCards(g, p, takeFromHand(p, [p.hand.indexOf('sled')]), true);
    yield* relocate(g, got, (yield* askYesNo(g, got.pi, 'どこに置きますか？', '手札', '山札の上')) ? 'hand' : 'deck');
  }
  // 黒猫: 他の人が勝利点を獲得したとき手札から使ってよい
  if (is(got.id, 'victory')) {
    for (let k = 1; k < n; k++) {
      const oi = (got.pi + k) % n;
      const o = g.players[oi];
      if (o.hand.includes('nightcat') && (yield* askYesNo(g, oi, `${p.name}が勝利点を獲得した。「黒猫」を使いますか？`, '使う', '使わない', ['nightcat']))) {
        o.hand.splice(o.hand.indexOf('nightcat'), 1);
        yield* playOutOfTurn(g, oi, 'nightcat');
      }
    }
  }
  // 鷹匠: 誰かが種類を 2 つ以上持つ札を獲得したとき、手札から使ってよい
  if (CARDS[got.id].types.length >= 2) {
    for (let k = 0; k < n; k++) {
      const oi = (got.pi + k) % n;
      const o = g.players[oi];
      if (o.hand.includes('falconer') && (yield* askYesNo(g, oi, `${nm(got.id)}が獲得された。「鷹匠」を使いますか？`, '使う', '使わない', ['falconer']))) {
        o.hand.splice(o.hand.indexOf('falconer'), 1);
        yield* playOutOfTurn(g, oi, 'falconer');
      }
    }
  }
});
// 炉: 次に札を使うとき、先に同じ札を獲得してよい
function* kilnCopy(g, id) {
  if (!(g.turn.kiln > 0) || id === 'kiln') return;
  g.turn.kiln -= 1;
  const pile = id in g.supply ? id : pileOf(id);
  if (g.supply[pile] > 0 && (yield* askYesNo(g, g.current, `炉: ${nm(id)}をもう 1 枚獲得しますか？`, '獲得する', 'しない', [id]))) yield* gain(g, g.current, pile);
}
HOOKS.play.push(kilnCopy);
HOOKS.treasure.push(kilnCopy);
// カエルの習性: 片付けで山札の上に
HOOKS.endTurn.push(function* (g) {
  const p = currentPlayer(g);
  for (const id of g.turn.frog || []) { const at = g.playArea.indexOf(id); if (at >= 0) putOnDeck(p, g.playArea.splice(at, 1)[0]); }
});

defineCards({ id: 'menagerie', name: '移動動物園' }, [pony, ...kingdom, ...events, ...ways], [
  { id: 'introtohorses', name: 'はじめての馬', cards: ['sled', 'provisions', 'scrapiron', 'horsemen', 'stablehand', 'hostel', 'livery', 'corral', 'herddog', 'snowvillage'], landscapes: ['m_ride', 'w_sheep'] },
  { id: 'exiles', name: '追放者たち', cards: ['caravan2', 'bountyman', 'archbishop', 'witchmeet', 'evict', 'warder', 'refuge', 'hoardpile', 'goatkeeper', 'huntlodge'], landscapes: ['m_banish', 'w_otter'] },
  { id: 'wildlife', name: '野のいきもの', cards: ['nightcat', 'commons', 'riverboat', 'falconer', 'angler', 'kiln', 'ringleader', 'warhorse', 'traveler2', 'beastfair'], landscapes: ['m_toil', 'w_mule'] },
]);
