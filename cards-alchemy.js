'use strict';
// 拡張「錬金術」のカード（12 種とポーション）。名前は公式日本語カード名。
// potion: コストのうちポーションの数。potionValue: 出すと得られるポーションの数。
import {
  CARDS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askYesNo, attackOthers, resolve, reveal, putBackInOrder,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;

const basics = [
  { id: 'potion', name: 'ポーション', types: ['treasure'], cost: 4, potionValue: 1, notSupply: true, main: '+1 ポーション', desc: 'コストにポーションがあるカードを買うのに使う' },
];

const kingdom = [
  {
    id: 'transform', name: '変成', cost: 0, potion: 1, main: '廃棄して化ける', desc: '手札を 1 枚廃棄する。アクションなら公領、財宝なら変成、勝利点なら金貨を獲得する（種類が複数ならそれぞれ）',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      if (is(id, 'action')) yield* gain(g, pi, 'duchy');
      if (is(id, 'treasure')) yield* gain(g, pi, 'transform');
      if (is(id, 'victory')) yield* gain(g, pi, 'gold');
    },
  },
  {
    id: 'vinerack', name: 'ブドウ園', types: ['victory'], cost: 0, potion: 1, main: 'アクション 3 枚\nごとに 1 点', desc: '持っているアクションカード 3 枚ごとに 1 点',
    pointsFn: (all) => Math.floor(all.filter((id) => is(id, 'action')).length / 3),
  },
  {
    id: 'herbpicker', name: '薬草商', cost: 2, main: '+1 購入\n+1 金', desc: '片付けのとき、場の財宝を 1 枚山札の上に置いてよい',
    *play(g) { g.turn.buys += 1; g.turn.money += 1; },
    *onCleanup(g, p, pi) {
      const tr = g.playArea.filter((id) => is(id, 'treasure'));
      const [i] = yield* askCards(g, pi, '「薬草商」: 山札の上に戻す財宝（なしでもよい）', tr, 0, 1);
      if (i == null) return;
      g.playArea.splice(g.playArea.indexOf(tr[i]), 1);
      putOnDeck(p, tr[i]);
    },
  },
  {
    id: 'druggist', name: '薬師', cost: 2, potion: 1, main: '+1 カード\n+1 アクション', desc: '山札の上 4 枚をめくり、銅貨とポーションを手札に入れる。残りは好きな順に戻す',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const shown = reveal(p, 4);
      const take = shown.filter((id) => id === 'copper' || id === 'potion');
      p.hand.push(...take);
      yield* putBackInOrder(g, pi, shown.filter((id) => !take.includes(id)));
    },
  },
  {
    id: 'mirrorpool', name: '念視の泉', types: ['action', 'attack'], cost: 2, potion: 1, main: '+1 アクション', desc: '全員の山札の一番上を見て、捨てるか戻すかをあなたが決める。そのあとアクション以外が出るまで山札をめくり、めくった札をすべて手札に入れる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const look = function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        if (yield* askYesNo(g, pi, `${t.name}の山札の上は${nm(id)}。捨てさせますか？`, '捨てる', '戻す', [id])) yield* discardCards(g, t, [id], true);
        else putOnDeck(t, id);
      };
      yield* look(pi);
      yield* attackOthers(g, look);
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        p.hand.push(id);
        if (!is(id, 'action')) break;
      }
    },
  },
  {
    id: 'academy', name: '大学', cost: 2, potion: 1, main: '+2 アクション', desc: 'コスト 5 以下のアクションカードを 1 枚獲得してよい',
    *play(g, p, pi) {
      g.turn.actions += 2;
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下のアクションを獲得してよい', 5, (id) => is(id, 'action'), true));
    },
  },
  {
    id: 'adept', name: '錬金術師', cost: 3, potion: 1, main: '+2 カード\n+1 アクション', desc: '片付けのとき、ポーションを場に出していれば、これを山札の上に置いてよい',
    *play(g, p) { drawCards(p, 2); g.turn.actions += 1; },
    *onCleanup(g, p, pi) {
      if (!g.playArea.includes('potion') || !g.playArea.includes('adept')) return;
      if (!(yield* askYesNo(g, pi, '「錬金術師」を山札の上に戻しますか？', '戻す', '戻さない', ['adept']))) return;
      putOnDeck(p, g.playArea.splice(g.playArea.indexOf('adept'), 1)[0]);
    },
  },
  {
    id: 'blackcat', name: '使い魔', types: ['action', 'attack'], cost: 3, potion: 1, main: '+1 カード\n+1 アクション', desc: '他の人は呪いを獲得する',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    },
  },
  {
    id: 'arcanestone', name: '賢者の石', types: ['treasure'], cost: 3, potion: 1, autoPlay: true, main: '山札と捨て札\n5 枚ごとに +1 金', desc: '山札と捨て札の合計 5 枚ごとに +1 金',
    *play(g, p) { g.turn.money += Math.floor((p.deck.length + p.discard.length) / 5); },
  },
  {
    id: 'clayman', name: 'ゴーレム', cost: 4, potion: 1, main: 'アクションを\n2 枚めくって使う', desc: 'ゴーレム以外のアクションが 2 枚出るまで山札をめくり、ほかは捨てる。その 2 枚を好きな順に使う',
    *play(g, p, pi) {
      const found = [];
      const other = [];
      while (found.length < 2) {
        const id = takeTop(p);
        if (id == null) break;
        (is(id, 'action') && id !== 'clayman' ? found : other).push(id);
      }
      yield* discardCards(g, p, other, true);
      if (found.length === 2 && found[0] !== found[1]) {
        const [first] = yield* askCards(g, pi, '先に使うアクションを選ぶ', found, 1, 1);
        if (first === 1) found.reverse();
      }
      for (const id of found) { g.playArea.push(id); log(g, `${p.name}が${nm(id)}を使用。`); yield* resolve(g, id); }
    },
  },
  {
    id: 'pupil', name: '弟子', cost: 5, main: '+1 アクション', desc: '手札を 1 枚廃棄し、そのコスト 1 につき +1 カード。コストにポーションがあれば、さらに +2 カード',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      drawCards(p, costOf(g, id) + (CARDS[id].potion ? 2 : 0));
    },
  },
  {
    id: 'takeover', name: '支配', cost: 6, potion: 1, main: '左の人の手番を\n操作する', desc: 'この手番のあと、左の人が追加の手番を行う。その手番はあなたが操作し、その人が獲得する札はあなたが獲得し、廃棄する札は脇に置いて手番の終わりにその人の捨て札に戻す',
    *play(g) { g.turn.possess = true; },
  },
];

defineCards({ id: 'alchemy', name: '錬金術' }, [...basics, ...kingdom], [
  { id: 'forbiddenarts', name: '禁じられた術（基本と混ぜる）', cards: ['druggist', 'warehouse', 'command', 'mirrorpool', 'transform', 'academy', 'meadow', 'alembic', 'pawnbroker', 'workshop'] },
  { id: 'potionmixers', name: '薬の調合（基本と混ぜる）', cards: ['adept', 'druggist', 'clayman', 'herbpicker', 'transform', 'warehouse', 'abbey', 'crier', 'command', 'sorcerer'] },
  { id: 'chemistlesson', name: '化学の授業（基本と混ぜる）', cards: ['adept', 'blackcat', 'clayman', 'arcanestone', 'academy', 'vinerack', 'moat', 'market', 'command', 'village'] },
  { id: 'servants', name: '召使い（陰謀と混ぜる）', cards: ['clayman', 'takeover', 'mirrorpool', 'transform', 'vinerack', 'plotter', 'marquis', 'minetown', 'errand', 'jailer'] },
]);
