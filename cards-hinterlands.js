'use strict';
// 拡張「異郷」のカード（第二版の 26 種と、初版だけにある 9 種）。名前は公式日本語カード名（一部未確認）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, shuffle, receive, returnCard,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const T = ['treasure'];

// 獲得・廃棄・捨てたときに「使ってよい」カード（進路・織工）: 今ある場所から取り出して使う
function* mayPlayFrom(g, pi, id, from) {
  if (!(yield* askYesNo(g, pi, `${nm(id)}を使いますか？`, '使う', '使わない', [id]))) return;
  const i = from.lastIndexOf(id);
  if (i < 0) return;
  from.splice(i, 1);
  yield* playOutOfTurn(g, pi, id);
}
function* discardToThree(g, ti) {
  const t = g.players[ti];
  const need = t.hand.length - 3;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が 3 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'crossing', name: '岐路', cost: 2, main: '勝利点の数だけ引く', desc: '手札を見せ、勝利点カード 1 枚につき +1 カード。この手番で最初の「岐路」なら +3 アクション',
    *play(g, p) {
      drawCards(p, p.hand.filter((id) => is(id, 'victory')).length);
      g.turn.crossings = (g.turn.crossings || 0) + 1;
      if (g.turn.crossings === 1) g.turn.actions += 3;
    },
  },
  {
    id: 'pyrite', name: '愚者の黄金', types: ['treasure', 'reaction'], cost: 2, autoPlay: true, main: '1 枚目 +1 金\n2 枚目から +4 金', desc: 'この手番で最初の「愚者の黄金」なら +1 金、そうでなければ +4 金。他の人が属州を獲得したとき、手札から廃棄して金貨を山札の上に獲得してよい',
    *play(g) { g.turn.pyrites = (g.turn.pyrites || 0) + 1; g.turn.money += g.turn.pyrites === 1 ? 1 : 4; },
  },
  // ---- コスト 3 ----
  {
    id: 'grading', name: '開発', cost: 3, main: '1 枚を 2 枚に', desc: '手札を 1 枚廃棄し、ちょうどコスト +1 と、ちょうどコスト -1 のカードを 1 枚ずつ獲得して、好きな順で山札の上に置く',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id);
      const up = yield* askSupply(g, pi, `ちょうどコスト ${c + 1} を獲得（山札の上へ）`, c + 1, (x) => costOf(g, x) === c + 1);
      const down = c >= 1 ? yield* askSupply(g, pi, `ちょうどコスト ${c - 1} を獲得（山札の上へ）`, c - 1, (x) => costOf(g, x) === c - 1) : null;
      // 後に獲得したほうが上になる。上にしたいほうを選ばせる
      let order = [up, down].filter(Boolean);
      if (order.length === 2 && order[0] !== order[1]) {
        const [top] = yield* askCards(g, pi, '山札の一番上にする札を選ぶ', order, 1, 1);
        if (top === 0) order = order.reverse();
      }
      for (const x of order) yield* gain(g, pi, x, 'deck');
    },
  },
  {
    id: 'spring', name: 'オアシス', cost: 3, main: '+1 カード　+1 アクション\n+1 金', desc: '手札を 1 枚捨てる',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚を選ぶ', 1, 1)));
    },
  },
  {
    id: 'groundwork', name: '画策', cost: 3, main: '+1 カード\n+1 アクション', desc: 'この手番の片付けで、場のアクションカードを 1 枚山札の上に置いてよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; },
    *onCleanup(g, p, pi) {
      const acts = g.playArea.filter((id) => is(id, 'action'));
      const [i] = yield* askCards(g, pi, '「画策」: 山札の上に戻すアクション（なしでもよい）', acts, 0, 1);
      if (i == null) return;
      g.playArea.splice(g.playArea.indexOf(acts[i]), 1);
      putOnDeck(p, acts[i]);
    },
  },
  {
    id: 'underpass', name: '坑道', types: ['victory', 'reaction'], cost: 3, points: 2, main: '2 点', desc: '片付け以外で捨て札にしたとき、見せて金貨を獲得してよい',
    *onDiscard(g, p, pi) {
      if (yield* askYesNo(g, pi, '「坑道」を見せて金貨を獲得しますか？', '見せる', '見せない', ['underpass'])) yield* gain(g, pi, 'gold');
    },
  },
  {
    id: 'watchdog', name: '番犬', types: ['action', 'reaction'], cost: 3, main: '+2 カード', desc: '手札が 5 枚以下なら、さらに +2 カード。他の人がアタックを使うとき、先に手札から使ってよい',
    *play(g, p) { drawCards(p, 2); if (p.hand.length <= 5) drawCards(p, 2); },
    *onAttack(g, t, ti) {
      t.hand.splice(t.hand.indexOf('watchdog'), 1);
      yield* playOutOfTurn(g, ti, 'watchdog');
    },
  },
  // ---- コスト 4 ----
  {
    id: 'handyman', name: 'よろずや', cost: 4, main: '銀貨を獲得\n5 枚まで引く', desc: '銀貨を獲得する。山札の一番上を見て捨ててよい。手札が 5 枚になるまで引く。財宝以外の手札を 1 枚廃棄してよい',
    *play(g, p, pi) {
      yield* gain(g, pi, 'silver');
      const [top] = reveal(p, 1);
      if (top != null) {
        if (yield* askYesNo(g, pi, `山札の一番上は${nm(top)}。捨てますか？`, '捨てる', '戻す', [top])) yield* discardCards(g, p, [top]);
        else putOnDeck(p, top);
      }
      drawCards(p, Math.max(0, 5 - p.hand.length));
      const [i] = yield* askHand(g, pi, '廃棄する財宝以外の 1 枚（しなくてもよい）', 0, 1, (id) => !is(id, 'treasure'));
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
    },
  },
  {
    id: 'spicer', name: '香辛料商人', cost: 4, main: '財宝を廃棄して\n得をする', desc: '手札の財宝を 1 枚廃棄してよい。そうしたら「+2 カード +1 アクション」か「+1 購入 +2 金」を選ぶ',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      yield* trashCards(g, p, takeFromHand(p, [i]));
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'draw', label: '+2 カード +1 アクション' }, { value: 'coin', label: '+1 購入 +2 金' }]);
      if (v === 'draw') { drawCards(p, 2); g.turn.actions += 1; } else { g.turn.buys += 1; g.turn.money += 2; }
    },
  },
  {
    id: 'silverdealer', name: '交易人', types: ['action', 'reaction'], cost: 4, main: '廃棄して銀貨', desc: '手札を 1 枚廃棄し、そのコスト 1 につき銀貨を 1 枚獲得する。カードを獲得するとき、手札から見せて、代わりに銀貨を獲得してよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      for (let k = costOf(g, id); k > 0; k--) yield* gain(g, pi, 'silver');
    },
    *reactGain(g, got) {
      if (got.id === 'silver' || g.supply[got.id] == null) return;
      if (!(yield* askYesNo(g, got.pi, `${nm(got.id)}の代わりに銀貨を獲得しますか？（交易人）`, '銀貨にする', 'そのまま', [got.id]))) return;
      if (!(yield* relocate(g, got, 'gone'))) return;
      if (!returnCard(g, got.id)) { g.players[got.pi].discard.push(got.id); return; }
      yield* gain(g, got.pi, 'silver');
    },
  },
  {
    id: 'drifter', name: '遊牧民', cost: 4, main: '+1 購入\n+2 金', desc: 'これを獲得したとき・廃棄したとき、+2 金',
    *play(g) { g.turn.buys += 1; g.turn.money += 2; },
    *onGain(g, got) { if (got.pi === g.current) g.turn.money += 2; },
    *onTrash(g, p, pi) { if (pi === g.current) g.turn.money += 2; },
  },
  {
    id: 'pathway', name: '進路', types: ['action', 'reaction'], cost: 4, main: '+1 カード\n+1 アクション', desc: '片付け以外で、これを獲得・廃棄・捨て札にしたとき、使ってよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; },
    *onGain(g, got) {
      if (got.to === 'gone') return;
      if (!(yield* askYesNo(g, got.pi, '獲得した「進路」を使いますか？', '使う', '使わない', ['pathway']))) return;
      if (yield* relocate(g, got, 'gone')) yield* playOutOfTurn(g, got.pi, 'pathway');
    },
    *onTrash(g, p, pi) { yield* mayPlayFrom(g, pi, 'pathway', g.trash); },
    *onDiscard(g, p, pi) { yield* mayPlayFrom(g, pi, 'pathway', p.discard); },
  },
  {
    id: 'loom', name: '織工', types: ['action', 'reaction'], cost: 4, main: '銀貨 2 枚 か\nコスト 4 以下', desc: '銀貨を 2 枚か、コスト 4 以下を 1 枚獲得する。片付け以外で捨て札にしたとき、使ってよい',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'silver', label: '銀貨を 2 枚' }, { value: 'one', label: 'コスト 4 以下を 1 枚' }]);
      if (v === 'silver') { yield* gain(g, pi, 'silver'); yield* gain(g, pi, 'silver'); } else yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を 1 枚獲得', 4));
    },
    *onDiscard(g, p, pi) { yield* mayPlayFrom(g, pi, 'loom', p.discard); },
  },
  // ---- コスト 5 ----
  {
    id: 'mapmaker', name: '地図職人', cost: 5, main: '+1 カード\n+1 アクション', desc: '山札の上 4 枚を見て、好きな枚数捨て、残りを好きな順に戻す',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const seen = reveal(p, 4);
      const idx = yield* askCards(g, pi, '捨てる札を選ぶ（好きな枚数）', seen, 0, seen.length);
      yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)));
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    },
  },
  {
    id: 'bargainer', name: '値切り屋', cost: 5, main: '+2 金', desc: 'この手番、カードを買うたびに、それより安い勝利点以外のカードを 1 枚獲得する',
    *play(g) { g.turn.money += 2; },
    *whenBuy(g, id, pi) {
      const c = costOf(g, id);
      if (c <= 0) return;
      yield* gain(g, pi, yield* askSupply(g, pi, `${nm(id)}より安い、勝利点以外を 1 枚獲得`, c - 1, (x) => !is(x, 'victory')));
    },
  },
  {
    id: 'causeway', name: '街道', cost: 5, main: '+1 カード\n+1 アクション', desc: 'この手番のあいだ、すべてのカードのコストが 1 下がる',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.costDown += 1; },
  },
  {
    id: 'hatago', name: '宿屋', cost: 5, main: '+2 カード\n+2 アクション', desc: '手札を 2 枚捨てる。これを獲得したとき、捨て札のアクションを好きな枚数、山札に混ぜてよい',
    *play(g, p, pi) {
      drawCards(p, 2); g.turn.actions += 2;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2)));
    },
    *onGain(g, got) {
      const p = g.players[got.pi];
      const acts = p.discard.filter((id) => is(id, 'action'));
      const idx = yield* askCards(g, got.pi, '山札に混ぜるアクションを選ぶ（好きな枚数）', acts, 0, acts.length);
      if (!idx.length) return;
      for (const id of idx.map((i) => acts[i])) p.discard.splice(p.discard.indexOf(id), 1) && p.deck.push(id);
      shuffle(p.deck, g);
      if (got.to === 'discard' && p.deck.includes('hatago') && !p.discard.includes('hatago')) got.to = 'deck';
    },
  },
  {
    id: 'warden', name: '辺境伯', types: ['action', 'attack'], cost: 5, main: '+3 カード\n+1 購入', desc: '他の人は 1 枚引いてから、手札が 3 枚になるまで捨てる',
    *play(g, p) {
      drawCards(p, 3); g.turn.buys += 1;
      yield* attackOthers(g, function* (ti) { drawCards(g.players[ti], 1); yield* discardToThree(g, ti); });
    },
  },
  {
    id: 'stable', name: '厩舎', cost: 5, main: '財宝を捨てて\n+3 カード', desc: '手札の財宝を 1 枚捨ててよい。そうしたら +3 カード +1 アクション',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '捨てる財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      yield* discardCards(g, p, takeFromHand(p, [i]));
      drawCards(p, 3); g.turn.actions += 1;
    },
  },
  {
    id: 'brute', name: '狂戦士', types: ['action', 'attack'], cost: 5, main: '安いカードを獲得', desc: 'これより安いカードを 1 枚獲得する。他の人は手札が 3 枚になるまで捨てる。これを獲得したとき、場にアクションがあれば使う',
    *play(g, p, pi) {
      const c = costOf(g, 'brute');
      if (c > 0) yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下を 1 枚獲得`, c - 1));
      yield* attackOthers(g, (ti) => discardToThree(g, ti));
    },
    *onGain(g, got) {
      if (got.pi !== g.current || !g.playArea.some((id) => is(id, 'action'))) return;
      if (yield* relocate(g, got, 'gone')) yield* playOutOfTurn(g, got.pi, 'brute');
    },
  },
  {
    id: 'stewpot', name: '大釜', types: ['treasure', 'attack'], cost: 5, value: 2, autoPlay: true, main: '+2 金　+1 購入', desc: 'この手番にアクションを 3 回獲得したら、他の人は呪いを獲得する',
    *play(g) { g.turn.buys += 1; },
  },
  {
    id: 'fleamarket', name: 'スーク', cost: 5, main: '+1 購入\n+7 金 - 手札', desc: '+7 金。ただし手札 1 枚につき -1 金（0 より下にはならない）。これを獲得したとき、手札を 2 枚まで廃棄する',
    *play(g, p) { g.turn.buys += 1; g.turn.money += Math.max(0, 7 - p.hand.length); },
    *onGain(g, got) {
      const p = g.players[got.pi];
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, got.pi, '廃棄するカード（2 枚まで）', 0, 2)));
    },
  },
  {
    id: 'wheeler', name: '車大工', cost: 5, main: '+1 カード\n+1 アクション', desc: '手札を 1 枚捨ててよい。そうしたら、そのコスト以下のアクションカードを 1 枚獲得する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '捨てる 1 枚（しなくてもよい）', 0, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* discardCards(g, p, [id]);
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${costOf(g, id)} 以下のアクションを獲得`, costOf(g, id), (x) => is(x, 'action')));
    },
  },
  {
    id: 'charmhut', name: '魔女の小屋', types: ['action', 'attack'], cost: 5, main: '+4 カード', desc: '手札を 2 枚見せて捨てる。2 枚ともアクションなら、他の人は呪いを獲得する',
    *play(g, p, pi) {
      drawCards(p, 4);
      const ids = takeFromHand(p, yield* askHand(g, pi, '見せて捨てる 2 枚を選ぶ', 2, 2));
      yield* discardCards(g, p, ids);
      const both = ids.length === 2 && ids.every((id) => is(id, 'action'));
      yield* attackOthers(g, function* (ti) { if (both) yield* gain(g, ti, 'curse'); });
    },
  },
  // ---- コスト 6 ----
  {
    id: 'gatevillage', name: '国境の村', cost: 6, main: '+1 カード\n+2 アクション', desc: 'これを獲得したとき、これより安いカードを 1 枚獲得する',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onGain(g, got) {
      const c = costOf(g, 'gatevillage');
      yield* gain(g, got.pi, yield* askSupply(g, got.pi, `コスト ${c - 1} 以下を 1 枚獲得`, c - 1));
    },
  },
  {
    id: 'fields', name: '農地', types: ['victory'], cost: 6, points: 2, main: '2 点', desc: 'これを獲得したとき、手札を 1 枚廃棄し、ちょうどコスト +2 の（農地以外の）カードを 1 枚獲得する',
    *onGain(g, got) {
      const p = g.players[got.pi];
      const [i] = yield* askHand(g, got.pi, '「農地」: 廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id) + 2;
      yield* gain(g, got.pi, yield* askSupply(g, got.pi, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c && x !== 'fields'));
    },
  },
];

function* brigandRaid(g, pi) {
  yield* eachOther(g, function* (ti) {
    const t = g.players[ti];
    const shown = reveal(t, 2);
    if (!shown.some((id) => is(id, 'treasure'))) {
      yield* discardCards(g, t, shown, true);
      yield* gain(g, ti, 'copper');
      return;
    }
    const idx = shown.map((id, i) => (id === 'silver' || id === 'gold' ? i : -1)).filter((i) => i >= 0);
    if (idx.length) {
      const pick = idx.length === 1 || shown[idx[0]] === shown[idx[1]] ? idx[0]
        : idx[(yield* askCards(g, pi, `${t.name}の財宝から奪う 1 枚`, idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
      const [id] = shown.splice(pick, 1);
      yield* trashCards(g, t, [id]);
      g.trash.splice(g.trash.lastIndexOf(id), 1);
      log(g, `${g.players[pi].name}が${nm(id)}を奪った。`);
      yield* receive(g, pi, id);
    }
    yield* discardCards(g, t, shown, true);
  });
}

const firstEdition = [
  {
    id: 'lady', name: '公爵夫人', cost: 2, main: '+2 金', desc: '全員が山札の一番上を見て、捨てるか戻すかを決める。公領を獲得したとき、公爵夫人を 1 枚獲得してよい',
    *play(g) {
      g.turn.money += 2;
      const n = g.players.length;
      for (let k = 0; k < n; k++) {
        const ti = (g.current + k) % n;
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) continue;
        if (yield* askYesNo(g, ti, `山札の一番上は${nm(id)}。捨てますか？`, '捨てる', '戻す', [id])) yield* discardCards(g, t, [id], true);
        else putOnDeck(t, id);
      }
    },
  },
  {
    id: 'omen', name: '神託', types: ['action', 'attack'], cost: 3, main: '+2 カード', desc: '全員の山札の上 2 枚をめくり、それぞれ捨てるか、その人の好きな順で戻すかをあなたが決める。そのあと +2 カード',
    *play(g, p, pi) {
      const look = function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 2);
        if (!shown.length) return;
        if (yield* askYesNo(g, pi, `${t.name}の山札の上: 捨てさせますか？`, '捨てる', '戻す', shown)) yield* discardCards(g, t, shown, true);
        else yield* putBackInOrder(g, ti, shown);
      };
      yield* look(pi);
      yield* attackOthers(g, look);
      drawCards(p, 2);
    },
  },
  {
    id: 'outlaw', name: '義賊', types: ['action', 'attack'], cost: 4, main: '+1 金', desc: '使ったとき・買ったとき: 他の人は山札の上 2 枚をめくり、銀貨か金貨があればあなたが 1 枚奪う。財宝がなかった人は銅貨を獲得する',
    *play(g, p, pi) {
      g.turn.money += 1;
      yield* attackOthers(g, function* () {}); // 水濠などを見せる機会（奪うのは下でまとめて）
      yield* brigandRaid(g, pi);
    },
    *onBuy(g, pi) { yield* brigandRaid(g, pi); },
  },
  {
    id: 'tent', name: '遊牧民の野営地', cost: 4, main: '+1 購入\n+2 金', desc: 'これを獲得したとき、山札の上に置く',
    *play(g) { g.turn.buys += 1; g.turn.money += 2; },
    *onGain(g, got) { if (got.to !== 'deck') yield* relocate(g, got, 'deck'); },
  },
  {
    id: 'silkway', name: 'シルクロード', types: ['victory'], cost: 4, main: '勝利点 4 枚\nごとに 1 点', desc: '持っている勝利点カード 4 枚ごとに 1 点',
    pointsFn: (all) => Math.floor(all.filter((id) => is(id, 'victory')).length / 4),
  },
  {
    id: 'hiddengold', name: '埋蔵金', types: T, cost: 5, value: 3, main: '+3 金', desc: 'これを獲得したとき、銅貨を 2 枚獲得する',
    *onGain(g, got) { yield* gain(g, got.pi, 'copper'); yield* gain(g, got.pi, 'copper'); },
  },
  {
    id: 'legation', name: '大使館', cost: 5, main: '+5 カード', desc: '手札を 3 枚捨てる。これを獲得したとき、他の人は銀貨を 1 枚ずつ獲得する',
    *play(g, p, pi) {
      drawCards(p, 5);
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚を選ぶ', 3, 3)));
    },
    *onGain(g, got) {
      const n = g.players.length;
      for (let k = 1; k < n; k++) yield* gain(g, (got.pi + k) % n, 'silver');
    },
  },
  {
    id: 'dirtymoney', name: '不正利得', types: T, cost: 5, value: 1, main: '+1 金', desc: '銅貨を 1 枚手札に獲得してよい。これを獲得したとき、他の人は呪いを獲得する',
    *play(g, p, pi) { if (yield* askYesNo(g, pi, '銅貨を手札に獲得しますか？', '獲得する', 'しない')) yield* gain(g, pi, 'copper', 'hand'); },
    *onGain(g, got) {
      const n = g.players.length;
      for (let k = 1; k < n; k++) yield* gain(g, (got.pi + k) % n, 'curse');
    },
  },
  {
    id: 'magistrate', name: '官吏', cost: 5, main: '+3 金', desc: '手札を 1 枚山札の上に置く。これを獲得したとき、場の財宝をすべて好きな順に山札の上に置く',
    *play(g, p, pi) {
      g.turn.money += 3;
      const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚を選ぶ', 1, 1);
      if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]);
    },
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      const tr = g.playArea.filter((id) => is(id, 'treasure'));
      g.playArea = g.playArea.filter((id) => !is(id, 'treasure'));
      yield* putBackInOrder(g, got.pi, tr);
    },
  },
].map((c) => ({ ...c, set: 'hinterlands1' }));

// 愚者の黄金: 他の人が属州を獲得したら、手札の愚者の黄金を廃棄して金貨を山札の上に（1 枚ずつ問う）
// 公爵夫人: 公領を獲得したとき、公爵夫人を獲得してよい
// 大釜: この手番に 3 回目のアクションを獲得したら、場の大釜 1 枚につき他の人は呪い
HOOKS.gain.push(function* (g, got) {
  const n = g.players.length;
  if (got.id === 'province') {
    for (let k = 1; k < n; k++) {
      const pi = (got.pi + k) % n;
      const p = g.players[pi];
      while (p.hand.includes('pyrite') && (yield* askYesNo(g, pi, `${g.players[got.pi].name}が属州を獲得。「愚者の黄金」を廃棄して金貨を山札の上に獲得しますか？`, '廃棄する', 'しない', ['pyrite']))) {
        yield* trashCards(g, p, takeFromHand(p, [p.hand.indexOf('pyrite')]));
        yield* gain(g, pi, 'gold', 'deck');
      }
    }
  }
  if (got.id === 'duchy' && g.supply.lady > 0 && (yield* askYesNo(g, got.pi, '「公爵夫人」も獲得しますか？', '獲得する', 'しない', ['lady']))) yield* gain(g, got.pi, 'lady');
  if (got.pi === g.current && is(got.id, 'action')) {
    g.turn.actionGains = (g.turn.actionGains || 0) + 1;
    if (g.turn.actionGains === 3) {
      for (const id of g.playArea) if (id === 'stewpot') yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    }
  }
});

defineCards({ id: 'hinterlands', name: '異郷' }, kingdom, [
  { id: 'introduction', name: 'はじめての異郷', cards: ['gatevillage', 'mapmaker', 'crossing', 'bargainer', 'hatago', 'warden', 'spring', 'groundwork', 'silverdealer', 'loom'] },
  { id: 'faircrossing', name: '街道の商い', cards: ['fields', 'pyrite', 'causeway', 'handyman', 'spicer', 'stable', 'underpass', 'drifter', 'fleamarket', 'wheeler'] },
  { id: 'wilds', name: '荒れ地', cards: ['grading', 'brute', 'stewpot', 'watchdog', 'pathway', 'charmhut', 'crossing', 'spring', 'warden', 'causeway'] },
  { id: 'highwayrobbery', name: '街道の追いはぎ（基本と混ぜる）', cards: ['warehouse', 'archive', 'moneylender', 'command', 'workshop', 'causeway', 'hatago', 'warden', 'wheeler', 'underpass'] },
]);
defineCards({ id: 'hinterlands1', name: '異郷（初版）' }, firstEdition, [
  { id: 'hinterlandsclassic', name: '初版の異郷', cards: ['lady', 'omen', 'outlaw', 'tent', 'silkway', 'hiddengold', 'legation', 'dirtymoney', 'magistrate', 'crossing'] },
]);
