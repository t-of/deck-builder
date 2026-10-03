'use strict';
// 拡張「収穫祭＆ギルド」のカード（第二版の合本 26 種＋恩賞 6 種、初版だけにある 8 種＋賞品 5 種）。カード名は公式日本語版に合わせた。
// 財源（コイントークン）: player.tokens.coffers。購入フェイズに spendCoffers でお金にする。
// 過払い（overpay）: 買うときに余分に払った分の効果。サプライ外の山: game.nonSupply。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, treasureEffect, allCards, kingdomPool, shuffle, currentPlayer,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const coffers = (g, p, n) => { p.tokens.coffers = (p.tokens.coffers || 0) + n; log(g, `${p.name}が財源を ${n} 得た（${p.tokens.coffers}）。`); };
const T = ['treasure'];

// 手札以外（山札など）のアクションをその場で使う
function* playFromNowhere(g, pi, id) {
  g.playArea.push(id);
  log(g, `${g.players[pi].name}が${nm(id)}を使用。`);
  if (is(id, 'action')) yield* resolve(g, id);
  else yield* treasureEffect(g, id);
}
function* discardToThree(g, ti) {
  const t = g.players[ti];
  const need = t.hand.length - 3;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が 3 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
// 手札の 1 枚を 2 回（n 回）使う
function* playTimes(g, p, pi, purpose, pred, n) {
  const [i] = yield* askHand(g, pi, purpose, 0, 1, pred);
  if (i == null) return;
  const [id] = takeFromHand(p, [i]);
  g.playArea.push(id);
  log(g, `${p.name}が${nm(id)}を ${n} 回使う。`);
  const before = p.nextTurn.length;
  for (let k = 0; k < n; k++) {
    if (is(id, 'action')) yield* resolve(g, id); else yield* treasureEffect(g, id);
  }
  return p.nextTurn.length > before;
}
const drawFour = { value: 'card', label: '+2 カード' };
function* chooseTwo(g, p, pi, all, apply) {
  const a = yield* askChoose(g, pi, '1 つめを選ぶ', all);
  const b = yield* askChoose(g, pi, '2 つめを選ぶ', all.filter((c) => c.value !== a));
  for (const v of [a, b]) yield* apply(v);
}

// ---- 恩賞（一騎討ちで手に入る。サプライ外、各 2 枚） ----
const rewards = [
  {
    id: 'coronet', name: '宝冠', types: ['action', 'treasure', 'reward'], cost: 0, notSupply: true, main: '2 回使う', desc: '恩賞でないアクションを手札から 1 枚 2 回使ってよい。恩賞でない財宝を手札から 1 枚 2 回使ってよい',
    *play(g, p, pi) {
      if (g.turn.phase === 'action') {
        if (yield* playTimes(g, p, pi, '2 回使うアクション（なしでもよい）', (id) => is(id, 'action') && !is(id, 'reward'), 2)) g.turn.stay.push('coronet');
      }
      yield* playTimes(g, p, pi, '2 回使う財宝（なしでもよい）', (id) => is(id, 'treasure') && !is(id, 'reward'), 2);
    },
  },
  {
    id: 'courser', name: '駿馬', types: ['action', 'reward'], cost: 0, notSupply: true, main: '2 つ選ぶ', desc: '+2 カード / +2 アクション / +2 金 / 銀貨を 4 枚獲得 から、ちがうものを 2 つ',
    *play(g, p, pi) {
      yield* chooseTwo(g, p, pi, [drawFour, { value: 'action', label: '+2 アクション' }, { value: 'coin', label: '+2 金' }, { value: 'silver', label: '銀貨を 4 枚獲得' }], function* (v) {
        if (v === 'card') drawCards(p, 2);
        else if (v === 'action') g.turn.actions += 2;
        else if (v === 'coin') g.turn.money += 2;
        else for (let k = 0; k < 4; k++) yield* gain(g, pi, 'silver');
      });
    },
  },
  {
    id: 'demesne', name: '御料地', types: ['action', 'victory', 'reward'], cost: 0, notSupply: true, main: '+2 アクション　+2 購入\n金貨を獲得', desc: '持っている金貨 1 枚につき 1 点',
    pointsFn: (all) => all.filter((id) => id === 'gold').length,
    *play(g, p, pi) { g.turn.actions += 2; g.turn.buys += 2; yield* gain(g, pi, 'gold'); },
  },
  {
    id: 'guardsman', name: 'ハスカール', types: ['action', 'reward'], cost: 0, notSupply: true, main: 'アクションの種類\nだけ引く', desc: '場にあるアクションのちがう名前 1 種につき +1 カード',
    *play(g, p) { drawCards(p, new Set(g.playArea.filter((id) => is(id, 'action'))).size); },
  },
  {
    id: 'turnip', name: '大きなかぶ', types: ['treasure', 'reward'], cost: 0, notSupply: true, autoPlay: true, main: '+2 財源\n財源の数だけ +金', desc: '+2 財源。そのあと財源 1 つにつき +1 金',
    *play(g, p) { coffers(g, p, 2); g.turn.money += p.tokens.coffers; },
  },
  {
    id: 'renown', name: '名声', types: ['action', 'reward'], cost: 0, notSupply: true, main: '+1 購入', desc: 'この手番のあいだ、カードのコストが 2 下がる',
    *play(g) { g.turn.buys += 1; g.turn.costDown += 2; },
  },
];

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'smallvillage', name: '村落', cost: 2, main: '+1 カード\n+1 アクション', desc: '1 枚捨てて +1 アクションにしてよい。もう 1 枚捨てて +1 購入にしてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      for (const [label, fn] of [['+1 アクション', () => { g.turn.actions += 1; }], ['+1 購入', () => { g.turn.buys += 1; }]]) {
        const [i] = yield* askHand(g, pi, `1 枚捨てて ${label}（しなくてもよい）`, 0, 1);
        if (i == null) continue;
        yield* discardCards(g, p, takeFromHand(p, [i]));
        fn();
      }
    },
  },
  {
    id: 'chandler', name: '蝋燭職人', cost: 2, main: '+1 アクション　+1 購入\n+1 財源', desc: '',
    *play(g, p) { g.turn.actions += 1; g.turn.buys += 1; coffers(g, p, 1); },
  },
  {
    id: 'mason', name: '石工', cost: 2, main: '1 枚を安い 2 枚に', desc: '手札を 1 枚廃棄し、それより安いカードを 2 枚獲得する。過払い: 払った額と同じコストのアクションを 2 枚獲得',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id);
      if (c <= 0) return;
      for (let k = 0; k < 2; k++) yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下を獲得（${k + 1}/2）`, c - 1));
    },
    *overpay(g, pi, x) {
      for (let k = 0; k < 2; k++) yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${x} のアクションを獲得（${k + 1}/2）`, x, (id) => is(id, 'action') && costOf(g, id) === x));
    },
  },
  {
    id: 'shoer', name: '装蹄師', cost: 2, main: '+1 カード　+1 アクション\n+1 購入', desc: '過払い: 1 金につき、この手番の終わりに +1 カード',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; },
    *overpay(g, pi, x) { g.turn.extraDraw = (g.turn.extraDraw || 0) + x; },
  },
  // ---- コスト 3 ----
  {
    id: 'sideshow', name: '移動動物園', cost: 3, main: '+1 アクション', desc: '手札を見せる。同じ名前の札がなければ +3 カード、あれば +1 カード',
    *play(g, p) { g.turn.actions += 1; drawCards(p, new Set(p.hand).size === p.hand.length ? 3 : 1); },
  },
  {
    id: 'clinic', name: '診療所', cost: 3, main: '+1 カード', desc: '手札を 1 枚廃棄してよい。過払い: 1 金につき 1 回、これを使う',
    *play(g, p, pi) {
      drawCards(p, 1);
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1);
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
    },
    *overpay(g, pi, x) { for (let k = 0; k < x; k++) yield* resolve(g, 'clinic'); },
  },
  {
    id: 'notions', name: '店', cost: 3, main: '+1 カード\n+1 金', desc: '場に同じ札がないアクションを、手札から 1 枚使ってよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.money += 1;
      const [i] = yield* askHand(g, pi, '使うアクション（場にないもの・なしでもよい）', 0, 1, (id) => is(id, 'action') && !g.playArea.includes(id));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* playFromNowhere(g, pi, id);
    },
  },
  // ---- コスト 4 ----
  {
    id: 'redo', name: '再建', cost: 4, main: '2 回: 廃棄して\nコスト +1 を獲得', desc: '2 回行う: 手札を 1 枚廃棄し、ちょうどコスト +1 のカードを 1 枚獲得する',
    *play(g, p, pi) {
      for (let k = 0; k < 2; k++) {
        const [i] = yield* askHand(g, pi, `廃棄する 1 枚を選ぶ（${k + 1}/2）`, 1, 1);
        if (i == null) return;
        const [id] = takeFromHand(p, [i]);
        yield* trashCards(g, p, [id]);
        const c = costOf(g, id) + 1;
        yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c));
      }
    },
  },
  {
    id: 'apprentice', name: '魔女娘', types: ['action', 'attack'], cost: 4, main: '+2 カード', desc: '手札を 2 枚捨てる。他の人は「厄よけ」の札を見せなければ呪いを獲得する（厄よけ: 対局ごとに決まるコスト 2〜3 の山）',
    *play(g, p, pi) {
      drawCards(p, 2);
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2)));
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (g.bane && t.hand.includes(g.bane)) { log(g, `${t.name}が厄よけの${nm(g.bane)}を見せた。`); return; }
        yield* gain(g, ti, 'curse');
      });
    },
  },
  {
    id: 'counselor', name: '助言者', cost: 4, main: '+1 アクション', desc: '山札の上 3 枚をめくる。左の人が 1 枚選んで捨て、残りは手札に入れる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const shown = reveal(p, 3);
      if (!shown.length) return;
      const li = (pi + 1) % g.players.length;
      const [i] = yield* askCards(g, li, `${p.name}のめくった札から、捨てさせる 1 枚を選ぶ`, shown, 1, 1);
      yield* discardCards(g, p, shown.splice(i ?? 0, 1));
      p.hand.push(...shown);
    },
  },
  {
    id: 'forerunner', name: '伝令官', cost: 4, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくり、アクションなら使う。過払い: 1 金につき、捨て札から 1 枚を山札の上に置く',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (is(id, 'action')) yield* playFromNowhere(g, pi, id); else putOnDeck(p, id);
    },
    *overpay(g, pi, x) {
      const p = g.players[pi];
      for (let k = 0; k < x && p.discard.length; k++) {
        const [i] = yield* askCards(g, pi, `捨て札から山札の上に置く 1 枚（${k + 1}/${x}）`, [...p.discard], 1, 1);
        putOnDeck(p, p.discard.splice(i ?? 0, 1)[0]);
      }
    },
  },
  {
    id: 'square', name: '広場', cost: 4, main: '+1 カード\n+2 アクション', desc: '手札の財宝を 1 枚捨ててよい。そうしたら +1 財源',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 2;
      const [i] = yield* askHand(g, pi, '捨てる財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      yield* discardCards(g, p, takeFromHand(p, [i]));
      coffers(g, p, 1);
    },
  },
  {
    id: 'farmhand', name: '耕作者', cost: 4, main: '+1 カード\n+2 アクション', desc: 'これを獲得したとき、手札のアクションか財宝を 1 枚脇に置き、次の手番の始めに使ってよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onGain(g, got) {
      const p = g.players[got.pi];
      const [i] = yield* askHand(g, got.pi, '次の手番の始めに使う札（なしでもよい）', 0, 1, (id) => is(id, 'action') || is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      (p.mats.farmhand = p.mats.farmhand || []).push(id);
      p.nextTurn.push(function* (gg, pp, ppi) {
        const k = pp.mats.farmhand.indexOf(id);
        if (k < 0) return;
        pp.mats.farmhand.splice(k, 1);
        yield* playFromNowhere(gg, ppi, id);
      });
    },
  },
  // ---- コスト 5 ----
  {
    id: 'expo', name: '品評会', types: ['victory'], cost: 6, main: '種類 5 つごとに 2 点', desc: '持っているカードのちがう名前 5 種ごとに 2 点',
    pointsFn: (all) => 2 * Math.floor(new Set(all).size / 5),
  },
  {
    id: 'cornhorn', name: '豊穣の角笛', types: T, cost: 5, main: '場の種類の数\nまでを獲得', desc: '場のちがう名前（これも含む）の数までのコストのカードを 1 枚獲得する。それが勝利点なら、これを廃棄する',
    *play(g, p, pi) {
      const n = new Set(g.playArea).size;
      const id = yield* askSupply(g, pi, `コスト ${n} 以下を 1 枚獲得`, n);
      if (!(yield* gain(g, pi, id))) return;
      if (is(id, 'victory')) {
        const at = g.playArea.lastIndexOf('cornhorn');
        if (at >= 0) yield* trashCards(g, p, g.playArea.splice(at, 1));
      }
    },
  },
  {
    id: 'huntparty', name: '狩猟団', cost: 5, main: '+1 カード\n+1 アクション', desc: '手札を見せ、手札にない名前の札が出るまで山札をめくる。その札を手札に入れ、ほかは捨てる',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      const other = [];
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        if (!p.hand.includes(id)) { p.hand.push(id); break; }
        other.push(id);
      }
      yield* discardCards(g, p, other, true);
    },
  },
  {
    id: 'clown', name: '道化師', types: ['action', 'attack'], cost: 5, main: '+2 金', desc: '他の人は山札の一番上を捨てる。勝利点なら呪いを獲得。そうでなければ、同じ札をその人かあなたが獲得（あなたが決める）',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        yield* discardCards(g, t, [id]);
        if (is(id, 'victory')) { yield* gain(g, ti, 'curse'); return; }
        if (!(g.supply[id] > 0)) return;
        const me = yield* askYesNo(g, pi, `${t.name}が${nm(id)}を捨てた。同じ札を誰が獲得する？`, '自分', t.name, [id]);
        yield* gain(g, me ? pi : ti, id);
      });
    },
  },
  {
    id: 'breadmaker', name: 'パン屋', cost: 5, main: '+1 カード　+1 アクション\n+1 財源', desc: 'このカードを使う対局では、はじめに全員が財源を 1 つ持つ',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; coffers(g, p, 1); },
  },
  {
    id: 'meatseller', name: '肉屋', cost: 5, main: '+2 財源', desc: '手札を 1 枚廃棄してよい。そうしたら財源を好きなだけ使い、そのコスト＋使った数以下のカードを 1 枚獲得する',
    *play(g, p, pi) {
      coffers(g, p, 2);
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const have = p.tokens.coffers || 0;
      const k = yield* askChoose(g, pi, `財源をいくつ使いますか？（${have} 持っている）`, Array.from({ length: have + 1 }, (_, j) => ({ value: j, label: `${j}` })));
      p.tokens.coffers -= k;
      const max = costOf(g, id) + k;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を 1 枚獲得`, max));
    },
  },
  {
    id: 'wanderer', name: '熟練工', cost: 5, main: '指定した以外を\n3 枚手札に', desc: 'カードの名前を 1 つ言い、それ以外の札が 3 枚出るまで山札をめくる。その 3 枚を手札に入れ、ほかは捨てる',
    *play(g, p, pi) {
      const mine = [...new Set(allCards(p))];
      const [k] = yield* askCards(g, pi, '手札に入れない札の名前を選ぶ', mine, 1, 1);
      const named = mine[k ?? 0];
      const got = [];
      const other = [];
      while (got.length < 3) {
        const id = takeTop(p);
        if (id == null) break;
        (id === named ? other : got).push(id);
      }
      p.hand.push(...got);
      yield* discardCards(g, p, other, true);
    },
  },
  {
    id: 'guildhall', name: '商人ギルド', cost: 5, main: '+1 購入\n+1 金', desc: '場にあるあいだ、カードを買うたびに +1 財源',
    *play(g) { g.turn.buys += 1; g.turn.money += 1; },
    *whenBuy(g, id, pi) { coffers(g, g.players[pi], 1); },
  },
  {
    id: 'stargazer', name: '予言者', types: ['action', 'attack'], cost: 5, main: '金貨を獲得', desc: '他の人は呪いを獲得する。獲得した人は 1 枚引く',
    *play(g, p, pi) {
      yield* gain(g, pi, 'gold');
      yield* attackOthers(g, function* (ti) { if (yield* gain(g, ti, 'curse')) drawCards(g.players[ti], 1); });
    },
  },
  {
    id: 'funfair', name: '謝肉祭', cost: 5, main: '種類ごとに 1 枚\n手札に', desc: '山札の上 4 枚をめくり、ちがう名前ごとに 1 枚を手札に入れ、残りを捨てる',
    *play(g, p) {
      const shown = reveal(p, 4);
      const keep = [];
      const rest = [];
      for (const id of shown) (keep.includes(id) ? rest : keep).push(id);
      p.hand.push(...keep);
      yield* discardCards(g, p, rest, true);
    },
  },
  {
    id: 'ferry', name: '渡し守', cost: 5, main: '+2 カード\n+1 アクション', desc: '手札を 1 枚捨てる。これを獲得したとき、この対局で決まった「渡し守の山」（コスト 3〜4）の札も 1 枚獲得する',
    *play(g, p, pi) {
      drawCards(p, 2); g.turn.actions += 1;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚を選ぶ', 1, 1)));
    },
    *onGain(g, got) { if (g.ferryPile) yield* gain(g, got.pi, g.ferryPile); },
  },
  {
    id: 'mugger', name: '野盗', types: ['action', 'attack'], cost: 5, main: '+2 財源', desc: '他の人は手札が 3 枚になるまで捨てる。この対局では、アクションフェイズにカードを獲得すると +1 カード',
    *play(g, p) {
      coffers(g, p, 2);
      yield* attackOthers(g, (ti) => discardToThree(g, ti));
    },
  },
  {
    id: 'duel', name: '一騎討ち', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: '手札の属州を 1 枚脇に置いてよい。そうしたら好きな恩賞を 1 枚手札に獲得する（属州は片付けで捨てる）',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1;
      const avail = rewards.map((c) => c.id).filter((id) => g.nonSupply[id] > 0);
      if (!p.hand.includes('province') || !avail.length) return;
      if (!(yield* askYesNo(g, pi, '属州を脇に置いて恩賞をもらいますか？', '置く', '置かない', ['province']))) return;
      g.playArea.push(...takeFromHand(p, [p.hand.indexOf('province')]));
      const [k] = yield* askCards(g, pi, '手札に獲得する恩賞を選ぶ', avail, 1, 1);
      yield* gain(g, pi, avail[k ?? 0], 'hand');
    },
  },
];

// ---- 初版だけ ----
const prizes = [
  {
    id: 'goldbag', name: '金貨袋', types: ['action', 'prize'], cost: 0, notSupply: true, main: '+1 アクション', desc: '金貨を 1 枚、山札の上に獲得する',
    *play(g, p, pi) { g.turn.actions += 1; yield* gain(g, pi, 'gold', 'deck'); },
  },
  {
    id: 'crown', name: '王冠', types: ['treasure', 'prize'], cost: 0, notSupply: true, value: 2, autoPlay: true, main: '+2 金', desc: '残っているアクション 1 回につき +1 金',
    *play(g) { g.turn.money += g.turn.actions; },
  },
  {
    id: 'retinue', name: '郎党', types: ['action', 'attack', 'prize'], cost: 0, notSupply: true, main: '+2 カード', desc: '屋敷を獲得する。他の人は呪いを獲得し、手札が 3 枚になるまで捨てる',
    *play(g, p, pi) {
      drawCards(p, 2);
      yield* gain(g, pi, 'estate');
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); yield* discardToThree(g, ti); });
    },
  },
  {
    id: 'hime', name: '王女', types: ['action', 'prize'], cost: 0, notSupply: true, main: '+1 購入', desc: '場にあるあいだ、カードのコストが 2 下がる',
    *play(g) { g.turn.buys += 1; g.turn.costDown += 2; },
  },
  {
    id: 'steed', name: '名馬', types: ['action', 'prize'], cost: 0, notSupply: true, main: '2 つ選ぶ', desc: '+2 カード / +2 アクション / +2 金 / 銀貨を 4 枚獲得して山札を捨て札に から、ちがうものを 2 つ',
    *play(g, p, pi) {
      yield* chooseTwo(g, p, pi, [drawFour, { value: 'action', label: '+2 アクション' }, { value: 'coin', label: '+2 金' }, { value: 'silver', label: '銀貨 4 枚＋山札を捨て札に' }], function* (v) {
        if (v === 'card') drawCards(p, 2);
        else if (v === 'action') g.turn.actions += 2;
        else if (v === 'coin') g.turn.money += 2;
        else { for (let k = 0; k < 4; k++) yield* gain(g, pi, 'silver'); p.discard.push(...p.deck.splice(0)); }
      });
    },
  },
];

const firstEdition = [
  {
    id: 'diviner', name: '占い師', types: ['action', 'attack'], cost: 3, main: '+2 金', desc: '他の人は勝利点か呪いが出るまで山札をめくり、それを山札の上に置く。ほかにめくった札は捨てる',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const other = [];
        for (let id = takeTop(t); id != null; id = takeTop(t)) {
          if (is(id, 'victory') || is(id, 'curse')) { putOnDeck(t, id); break; }
          other.push(id);
        }
        yield* discardCards(g, t, other, true);
      });
    },
  },
  {
    id: 'healer', name: '医者', cost: 3, main: '指定した札を廃棄', desc: '名前を 1 つ言い、山札の上 3 枚をめくる。その名前の札を廃棄し、残りを好きな順に戻す。過払い: 1 金につき、山札の一番上を廃棄・捨てる・戻すのどれか',
    *play(g, p, pi) {
      const mine = [...new Set(allCards(p))];
      const [k] = yield* askCards(g, pi, '廃棄する札の名前を選ぶ', mine, 1, 1);
      const named = mine[k ?? 0];
      const shown = reveal(p, 3);
      yield* trashCards(g, p, shown.filter((id) => id === named));
      yield* putBackInOrder(g, pi, shown.filter((id) => id !== named));
    },
    *overpay(g, pi, x) {
      const p = g.players[pi];
      for (let k = 0; k < x; k++) {
        const [id] = reveal(p, 1);
        if (id == null) return;
        const v = yield* askChoose(g, pi, `山札の一番上は${nm(id)}`, [{ value: 'trash', label: '廃棄' }, { value: 'discard', label: '捨てる' }, { value: 'keep', label: '戻す' }], [id]);
        if (v === 'trash') yield* trashCards(g, p, [id]); else if (v === 'discard') yield* discardCards(g, p, [id]); else putOnDeck(p, id);
      }
    },
  },
  {
    id: 'gem', name: '名品', types: T, cost: 3, value: 1, main: '+1 金', desc: '過払い: 1 金につき銀貨を 1 枚獲得する',
    *overpay(g, pi, x) { for (let k = 0; k < x; k++) yield* gain(g, pi, 'silver'); },
  },
  {
    id: 'countryside', name: '農村', cost: 4, main: '+2 アクション', desc: 'アクションか財宝が出るまで山札をめくり、それを手札に入れる。ほかは捨てる',
    *play(g, p) {
      g.turn.actions += 2;
      const other = [];
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        if (is(id, 'action') || is(id, 'treasure')) { p.hand.push(id); break; }
        other.push(id);
      }
      yield* discardCards(g, p, other, true);
    },
  },
  {
    id: 'horsedealer', name: '馬商人', types: ['action', 'reaction'], cost: 4, main: '+1 購入\n+3 金', desc: '手札を 2 枚捨てる。他の人がアタックを使ったとき、手札から脇に置いてよい。次の手番の始めに +1 カードし、これを手札に戻す',
    *play(g, p, pi) {
      g.turn.buys += 1; g.turn.money += 3;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2)));
    },
    *onAttack(g, t) {
      t.hand.splice(t.hand.indexOf('horsedealer'), 1);
      (t.mats.horsedealer = t.mats.horsedealer || []).push('horsedealer');
      t.nextTurn.push(function* (gg, pp) {
        drawCards(pp, 1);
        const k = pp.mats.horsedealer.indexOf('horsedealer');
        if (k >= 0) pp.hand.push(...pp.mats.horsedealer.splice(k, 1));
      });
    },
  },
  {
    id: 'tourney', name: '馬上槍試合', cost: 4, main: '+1 アクション', desc: '全員が手札の属州を見せてよい。あなたが見せたら、それを捨て、賞品か公領を山札の上に獲得する。誰も見せなければ +1 カード +1 金',
    *play(g, p, pi) {
      g.turn.actions += 1;
      let me = false;
      let other = false;
      const n = g.players.length;
      for (let k = 0; k < n; k++) {
        const ti = (pi + k) % n;
        const t = g.players[ti];
        if (!t.hand.includes('province')) continue;
        if (!(yield* askYesNo(g, ti, '「馬上槍試合」: 手札の属州を見せますか？', '見せる', '見せない', ['province']))) continue;
        if (k === 0) me = true; else other = true;
      }
      if (me) {
        yield* discardCards(g, p, takeFromHand(p, [p.hand.indexOf('province')]));
        const avail = [...prizes.map((c) => c.id).filter((id) => g.nonSupply[id] > 0), ...(g.supply.duchy > 0 ? ['duchy'] : [])];
        if (avail.length) {
          const [k] = yield* askCards(g, pi, '山札の上に獲得する賞品（か公領）を選ぶ', avail, 1, 1);
          yield* gain(g, pi, avail[k ?? 0], 'deck');
        }
      }
      if (!other) { drawCards(p, 1); g.turn.money += 1; }
    },
  },
  {
    id: 'collector', name: '収税吏', types: ['action', 'attack'], cost: 4, main: '財宝を格上げ', desc: '手札の財宝を 1 枚廃棄してよい。手札が 5 枚以上の他の人は同じ札を 1 枚捨てる。そのコスト +3 以下の財宝を山札の上に獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length >= 5 && t.hand.includes(id)) yield* discardCards(g, t, takeFromHand(t, [t.hand.indexOf(id)]));
      });
      const max = costOf(g, id) + 3;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下の財宝を山札の上に獲得`, max, (x) => is(x, 'treasure')), 'deck');
    },
  },
  {
    id: 'reaping', name: '収穫', cost: 5, main: '種類の数だけ +金', desc: '山札の上 4 枚をめくって捨てる。ちがう名前 1 種につき +1 金',
    *play(g, p) {
      const shown = reveal(p, 4);
      g.turn.money += new Set(shown).size;
      yield* discardCards(g, p, shown, true);
    },
  },
].map((c) => ({ ...c, set: 'guilds1' }));

// ---- 対局の準備 ----
function pickPile(g, pred) {
  const pool = kingdomPool().filter((id) => !(id in g.supply) && !(id in g.nonSupply) && pred(id));
  return pool.length ? shuffle(pool)[0] : null;
}
const pileSize = (g, id) => (is(id, 'victory') ? (g.players.length === 2 ? 8 : 12) : 10);
HOOKS.setup.push((g) => {
  const k = g.kingdom;
  if (k.includes('breadmaker')) for (const p of g.players) p.tokens.coffers = 1;
  if (k.includes('duel')) for (const c of rewards) g.nonSupply[c.id] = 2;
  if (k.includes('tourney')) for (const c of prizes) g.nonSupply[c.id] = 1;
  if (k.includes('apprentice')) {
    const bane = pickPile(g, (id) => CARDS[id].cost === 2 || CARDS[id].cost === 3);
    if (bane) { g.bane = bane; g.supply[bane] = pileSize(g, bane); g.kingdom.push(bane); log(g, `厄よけの山は${nm(bane)}。`); }
  }
  if (k.includes('ferry')) {
    const f = pickPile(g, (id) => CARDS[id].cost === 3 || CARDS[id].cost === 4);
    if (f) { g.ferryPile = f; g.nonSupply[f] = pileSize(g, f); log(g, `渡し守の山は${nm(f)}。`); }
  }
});
// 野盗: アクションフェイズにカードを獲得したら +1 カード
HOOKS.gain.push(function* (g, got) {
  if (g.kingdom.includes('mugger') && g.turn.phase === 'action') drawCards(g.players[got.pi], 1);
});

defineCards({ id: 'guilds', name: '収穫祭＆ギルド' }, [...kingdom, ...rewards], [
  { id: 'harvestfeast', name: '収穫の宴', cards: ['smallvillage', 'chandler', 'sideshow', 'redo', 'counselor', 'square', 'cornhorn', 'huntparty', 'clown', 'expo'] },
  { id: 'guildmasters', name: '親方たち', cards: ['mason', 'shoer', 'clinic', 'forerunner', 'farmhand', 'breadmaker', 'meatseller', 'wanderer', 'guildhall', 'stargazer'] },
  { id: 'fairday', name: 'お祭りの日', cards: ['funfair', 'ferry', 'mugger', 'duel', 'notions', 'apprentice', 'smallvillage', 'chandler', 'cornhorn', 'expo'] },
  { id: 'bountiful', name: '実りの年（基本と混ぜる）', cards: ['warehouse', 'market', 'moneylender', 'workshop', 'fair', 'cornhorn', 'huntparty', 'breadmaker', 'square', 'stargazer'] },
]);
defineCards({ id: 'guilds1', name: '収穫祭＆ギルド（初版）' }, [...firstEdition, ...prizes.map((c) => ({ ...c, set: 'guilds1' }))], [
  { id: 'guildsclassic', name: '初版の収穫祭', cards: ['diviner', 'healer', 'gem', 'countryside', 'horsedealer', 'tourney', 'collector', 'reaping', 'sideshow', 'smallvillage'] },
]);
