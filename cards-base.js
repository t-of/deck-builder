'use strict';
// 基本セットのカード（第二版の 26 種＋基本カード）と、初版だけにある 6 種。
// 名前はホビージャパン版ドミニオンの公式日本語カード名。
// main: カードの真ん中に大きく出す文言、desc: 効果の全文。
import {
  CARDS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, emptyPiles, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal, receive,
} from './engine.js';

const names = (ids) => ids.map((id) => `「${CARDS[id].name}」`).join('');
const log = (g, text) => g.log.push(text);


const basics = [
  { id: 'copper',   name: '銅貨', types: ['treasure'], cost: 0, value: 1, main: '+1 金', desc: '使うと、お金が 1 増える' },
  { id: 'silver',   name: '銀貨', types: ['treasure'], cost: 3, value: 2, main: '+2 金', desc: '使うと、お金が 2 増える' },
  { id: 'gold',     name: '金貨', types: ['treasure'], cost: 6, value: 3, main: '+3 金', desc: '使うと、お金が 3 増える' },
  { id: 'estate',   name: '屋敷', types: ['victory'], cost: 2, points: 1, main: '1 点', desc: 'ゲームの終わりに数える' },
  { id: 'duchy',    name: '公領', types: ['victory'], cost: 5, points: 3, main: '3 点', desc: 'ゲームの終わりに数える' },
  { id: 'province', name: '属州', types: ['victory'], cost: 8, points: 6, main: '6 点', desc: 'ゲームの終わりに数える' },
  { id: 'curse',    name: '呪い', types: ['curse'],   cost: 0, points: -1, main: '-1 点', desc: 'ゲームの終わりに 1 点減る' },
];

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'warehouse', name: '地下貯蔵庫', cost: 2, main: '+1 アクション', desc: '手札を好きな枚数捨て、同じ枚数引く',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const idx = yield* askHand(g, pi, '捨てるカードを選ぶ（好きな枚数）', 0, p.hand.length);
      const cards = takeFromHand(p, idx);
      yield* discardCards(g, p, cards);
      drawCards(p, cards.length);
    },
  },
  {
    id: 'abbey', name: '礼拝堂', cost: 2, main: '廃棄', desc: '手札を 4 枚まで廃棄する',
    *play(g, p, pi) {
      const idx = yield* askHand(g, pi, '廃棄するカードを選ぶ（4 枚まで）', 0, 4);
      yield* trashCards(g, p, takeFromHand(p, idx));
    },
  },
  {
    id: 'moat', name: '堀', types: ['action', 'reaction'], cost: 2, blocksAttack: true, main: '+2 カード',
    desc: '他の人がアタックを使ったとき、手札にあれば見せて、その効果を受けない',
    *play(g, p) { drawCards(p, 2); },
  },
  // ---- コスト 3 ----
  {
    id: 'crier', name: '前駆者', cost: 3, main: '+1 カード\n+1 アクション', desc: '捨て札を見て、1 枚を山札の上に置いてよい',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const [i] = yield* askCards(g, pi, '山札の上に戻す 1 枚（なしでもよい）', [...p.discard], 0, 1);
      if (i != null) { const [id] = p.discard.splice(i, 1); putOnDeck(p, id); log(g, `${p.name}が捨て札から 1 枚を山札の上に置いた。`); }
    },
  },
  {
    id: 'moneylender', name: '商人', cost: 3, main: '+1 カード\n+1 アクション', desc: 'この手番で最初に銀貨を出すと +1 金',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.silverBonus += 1; },
  },
  {
    id: 'attendant', name: '家臣', cost: 3, main: '+2 金', desc: '山札の一番上を捨てる。それがアクションなら、使ってよい',
    *play(g, p, pi) {
      g.turn.money += 2;
      const [id] = reveal(p, 1);
      if (id == null) return;
      log(g, `${p.name}が山札の上の「${CARDS[id].name}」を捨てた。`);
      if (is(id, 'action') && (yield* askYesNo(g, pi, `「${CARDS[id].name}」を使いますか？`, '使う', '使わない', [id]))) {
        g.playArea.push(id);
        log(g, `${p.name}が「${CARDS[id].name}」を使用。`);
        yield* resolve(g, id);
      } else {
        p.discard.push(id);
      }
    },
  },
  {
    id: 'village', name: '村', cost: 3, main: '+1 カード\n+2 アクション', desc: '',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
  },
  {
    id: 'workshop', name: '工房', cost: 3, main: 'カードを獲得', desc: 'コスト 4 以下のカードを 1 枚獲得する',
    *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を 1 枚獲得', 4)); },
  },
  // ---- コスト 4 ----
  {
    id: 'official', name: '役人', types: ['action', 'attack'], cost: 4, main: '銀貨を獲得',
    desc: '銀貨を 1 枚、山札の上に獲得する。他の人は手札の勝利点カードを 1 枚、山札の上に置く（なければ手札を見せる）',
    *play(g, p, pi) {
      yield* gain(g, pi, 'silver', 'deck');
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [i] = yield* askHand(g, ti, '山札の上に置く勝利点カードを選ぶ', 1, 1, (id) => is(id, 'victory'));
        if (i == null) { log(g, `${t.name}の手札に勝利点カードはなかった。`); return; }
        const [id] = takeFromHand(t, [i]);
        putOnDeck(t, id);
        log(g, `${t.name}が「${CARDS[id].name}」を山札の上に置いた。`);
      });
    },
  },
  {
    id: 'meadow', name: '庭園', types: ['victory'], cost: 4, main: '10 枚ごとに 1 点',
    desc: '持っているカード 10 枚ごとに 1 点（端数は切り捨て）',
    pointsFn: (all) => Math.floor(all.length / 10),
  },
  {
    id: 'hunter', name: '密猟者', cost: 4, main: '+1 カード　+1 アクション\n+1 金', desc: '空になったサプライの山 1 つにつき、手札を 1 枚捨てる',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      g.turn.money += 1;
      const n = emptyPiles(g);
      if (!n) return;
      const idx = yield* askHand(g, pi, `捨てるカードを ${n} 枚選ぶ`, n, n);
      yield* discardCards(g, p, takeFromHand(p, idx));
    },
  },
  {
    id: 'mercenary', name: '民兵', types: ['action', 'attack'], cost: 4, main: '+2 金', desc: '他の全員は、手札が 3 枚になるまで捨てる',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const need = t.hand.length - 3;
        if (need <= 0) return;
        const idx = yield* askHand(g, ti, `手札が 3 枚になるまで捨てる（${need} 枚選ぶ）`, need, need);
        yield* discardCards(g, t, takeFromHand(t, idx));
      });
    },
  },
  {
    id: 'pawnbroker', name: '金貸し', cost: 4, main: '銅貨を廃棄して\n+3 金', desc: '手札の銅貨を 1 枚廃棄してよい。そうしたら +3 金',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する銅貨を選ぶ（しなくてもよい）', 0, 1, (id) => id === 'copper');
      if (i == null) return;
      yield* trashCards(g, p, takeFromHand(p, [i]));
      g.turn.money += 3;
    },
  },
  {
    id: 'remodel', name: '改築', cost: 4, main: '廃棄して獲得', desc: '手札を 1 枚廃棄し、そのコスト +2 以下のカードを 1 枚獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 2;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を 1 枚獲得`, max, null, false, CARDS[id].potion || 0));
    },
  },
  {
    id: 'smithy', name: '鍛冶屋', cost: 4, main: '+3 カード', desc: '山札から 3 枚引く',
    *play(g, p) { drawCards(p, 3); },
  },
  {
    id: 'command', name: '玉座の間', cost: 4, main: 'アクションを\n2 回使う', desc: '手札のアクションカードを 1 枚、2 回使ってよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '2 回使うアクションを選ぶ（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      log(g, `${p.name}が「${CARDS[id].name}」を 2 回使う。`);
      const before = p.nextTurn.length;
      yield* resolve(g, id);
      yield* resolve(g, id);
      if (p.nextTurn.length > before) g.turn.stay.push('command'); // 持続を 2 回使ったら、号令も一緒に場に残る
    },
  },
  // ---- コスト 5 ----
  {
    id: 'highwayman', name: '山賊', types: ['action', 'attack'], cost: 5, main: '金貨を獲得',
    desc: '金貨を 1 枚獲得する。他の人は山札の上 2 枚をめくり、銅貨以外の財宝を 1 枚廃棄し、残りを捨てる',
    *play(g, p, pi) {
      yield* gain(g, pi, 'gold');
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 2);
        if (!shown.length) return;
        log(g, `${t.name}がめくった: ${names(shown)}`);
        const idx = shown.map((id, i) => (is(id, 'treasure') && id !== 'copper' ? i : -1)).filter((i) => i >= 0);
        if (idx.length) {
          const pick = idx.length === 1 || shown[idx[0]] === shown[idx[1]]
            ? idx[0]
            : idx[(yield* askCards(g, ti, '廃棄する財宝を選ぶ', idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
          yield* trashCards(g, t, shown.splice(pick, 1));
        }
        yield* discardCards(g, t, shown, true);
      });
    },
  },
  {
    id: 'assembly', name: '議事堂', cost: 5, main: '+4 カード\n+1 購入', desc: '他の人は 1 枚引く',
    *play(g, p) {
      drawCards(p, 4);
      g.turn.buys += 1;
      yield* eachOther(g, function* (ti) { drawCards(g.players[ti], 1); });
    },
  },
  {
    id: 'fair', name: '祝祭', cost: 5, main: '+2 アクション\n+1 購入　+2 金', desc: '',
    *play(g) { g.turn.actions += 2; g.turn.buys += 1; g.turn.money += 2; },
  },
  {
    id: 'alembic', name: '研究所', cost: 5, main: '+2 カード\n+1 アクション', desc: '',
    *play(g, p) { drawCards(p, 2); g.turn.actions += 1; },
  },
  {
    id: 'archive', name: '書庫', cost: 5, main: '7 枚まで引く', desc: '手札が 7 枚になるまで引く。引いたアクションカードは脇に置いてよい（あとで捨てる）',
    *play(g, p, pi) {
      const aside = [];
      while (p.hand.length < 7) {
        const id = takeTop(p);
        if (id == null) break;
        if (is(id, 'action') && (yield* askYesNo(g, pi, `「${CARDS[id].name}」を引いた。脇に置きますか？`, '脇に置く', '手札に入れる', [id]))) aside.push(id);
        else p.hand.push(id);
      }
      yield* discardCards(g, p, aside, true);
    },
  },
  {
    id: 'market', name: '市場', cost: 5, main: '+1 カード　+1 アクション\n+1 購入　+1 金', desc: '',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; g.turn.money += 1; },
  },
  {
    id: 'mine', name: '鉱山', cost: 5, main: '財宝を格上げ', desc: '手札の財宝を 1 枚廃棄してよい。そのコスト +3 以下の財宝を 1 枚、手札に獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する財宝を選ぶ（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 3;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下の財宝を 1 枚、手札へ獲得`, max, (c) => is(c, 'treasure')), 'hand');
    },
  },
  {
    id: 'sentinel', name: '衛兵', cost: 5, main: '+1 カード\n+1 アクション', desc: '山札の上 2 枚を見て、それぞれ廃棄・捨てる・戻すを選ぶ。戻す札は好きな順に置く',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const seen = reveal(p, 2);
      const keep = [];
      for (const id of seen) {
        const act = yield* askChoose(g, pi, `「${CARDS[id].name}」をどうしますか？`, [
          { value: 'trash', label: '廃棄' }, { value: 'discard', label: '捨てる' }, { value: 'keep', label: '山札に戻す' },
        ], [id]);
        if (act === 'trash') yield* trashCards(g, p, [id]);
        else if (act === 'discard') yield* discardCards(g, p, [id]);
        else keep.push(id);
      }
      if (keep.length === 2 && keep[0] !== keep[1]) {
        const [top] = yield* askCards(g, pi, '一番上に置く札を選ぶ', keep, 1, 1);
        if (top === 0) keep.reverse();
      }
      for (const id of keep) putOnDeck(p, id); // 最後に置いた札が一番上
    },
  },
  {
    id: 'sorcerer', name: '魔女', types: ['action', 'attack'], cost: 5, main: '+2 カード', desc: '他の人は「呪い」を 1 枚獲得する',
    *play(g, p) {
      drawCards(p, 2);
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    },
  },
  // ---- コスト 6 ----
  {
    id: 'craftsman', name: '職人', cost: 6, main: '手札に獲得', desc: 'コスト 5 以下のカードを 1 枚、手札に獲得する。そのあと手札を 1 枚、山札の上に置く',
    *play(g, p, pi) {
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を 1 枚、手札へ獲得', 5), 'hand');
      const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚を選ぶ', 1, 1);
      if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]);
    },
  },
];

// 初版だけにあって、第二版で入れ替わった 6 種
const firstEdition = [
  {
    id: 'woodsman', name: '木こり', cost: 3, main: '+1 購入\n+2 金', desc: '',
    *play(g) { g.turn.buys += 1; g.turn.money += 2; },
  },
  {
    id: 'bursar', name: '宰相', cost: 3, main: '+2 金', desc: '山札をすべて、そのまま捨て札にしてよい',
    *play(g, p, pi) {
      g.turn.money += 2;
      if (p.deck.length && (yield* askYesNo(g, pi, `山札 ${p.deck.length} 枚を捨て札にしますか？`, '捨て札にする', 'しない'))) {
        p.discard.push(...p.deck);
        p.deck = [];
        log(g, `${p.name}が山札を捨て札にした。`);
      }
    },
  },
  {
    id: 'banquet', name: '祝宴', cost: 4, main: 'カードを獲得', desc: 'このカードを廃棄し、コスト 5 以下のカードを 1 枚獲得する',
    *play(g, p, pi) {
      const at = g.playArea.lastIndexOf('banquet');
      if (at >= 0) yield* trashCards(g, p, g.playArea.splice(at, 1));
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を 1 枚獲得', 5));
    },
  },
  {
    id: 'scout', name: '密偵', types: ['action', 'attack'], cost: 4, main: '+1 カード\n+1 アクション',
    desc: '全員（自分も）の山札の一番上をめくり、それぞれ捨てるか戻すかをあなたが決める',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const look = function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        const discard = yield* askYesNo(g, pi, `${t.name}の山札の上は「${CARDS[id].name}」。捨てさせますか？`, '捨てる', '戻す', [id]);
        if (discard) { t.discard.push(id); log(g, `${t.name}の「${CARDS[id].name}」を捨てた。`); } else putOnDeck(t, id);
      };
      yield* look(pi);
      yield* attackOthers(g, look);
    },
  },
  {
    id: 'pickpocket', name: '泥棒', types: ['action', 'attack'], cost: 4, main: '財宝を盗む',
    desc: '他の人は山札の上 2 枚をめくる。その中の財宝 1 枚をあなたが選んで廃棄し、廃棄した財宝を獲得してよい。残りは捨てる',
    *play(g, p, pi) {
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 2);
        if (!shown.length) return;
        log(g, `${t.name}がめくった: ${names(shown)}`);
        const idx = shown.map((id, i) => (is(id, 'treasure') ? i : -1)).filter((i) => i >= 0);
        if (idx.length) {
          const pick = idx.length === 1 || shown[idx[0]] === shown[idx[1]]
            ? idx[0]
            : idx[(yield* askCards(g, pi, `${t.name}の財宝から廃棄する 1 枚`, idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
          const [id] = shown.splice(pick, 1);
          yield* trashCards(g, t, [id]);
          if (yield* askYesNo(g, pi, `廃棄した「${CARDS[id].name}」を獲得しますか？`, '獲得する', 'しない', [id])) {
            g.trash.splice(g.trash.lastIndexOf(id), 1);
            log(g, `${p.name}が「${CARDS[id].name}」を獲得。`);
            yield* receive(g, pi, id);
          }
        }
        yield* discardCards(g, t, shown, true);
      });
    },
  },
  {
    id: 'explorer', name: '冒険者', cost: 6, main: '財宝を 2 枚\n手札に', desc: '財宝が 2 枚出るまで山札をめくり、その財宝を手札に入れる。ほかにめくった札は捨てる',
    *play(g, p) {
      const found = [];
      const other = [];
      while (found.length < 2) {
        const id = takeTop(p);
        if (id == null) break;
        (is(id, 'treasure') ? found : other).push(id);
      }
      p.hand.push(...found);
      yield* discardCards(g, p, other, true);
      if (found.length) log(g, `${p.name}が${names(found)}を手札に入れた。`);
    },
  },
].map((c) => ({ ...c, set: 'base1' }));

defineCards({ id: 'base', name: '基本' }, [...basics, ...kingdom], [
  { id: 'first', name: 'はじめてのゲーム', cards: ['warehouse', 'market', 'moneylender', 'mercenary', 'mine', 'moat', 'remodel', 'smithy', 'village', 'workshop'] },
  { id: 'size', name: '大きさのちがい', cards: ['craftsman', 'highwayman', 'official', 'abbey', 'fair', 'meadow', 'sentinel', 'command', 'sorcerer', 'workshop'] },
  { id: 'decktop', name: '山札の上', cards: ['craftsman', 'official', 'assembly', 'fair', 'crier', 'alembic', 'pawnbroker', 'sentinel', 'attendant', 'village'] },
  { id: 'sleight', name: '手さばき', cards: ['warehouse', 'assembly', 'fair', 'meadow', 'archive', 'crier', 'mercenary', 'hunter', 'smithy', 'command'] },
  { id: 'improve', name: '改良', cards: ['craftsman', 'warehouse', 'market', 'moneylender', 'mine', 'moat', 'pawnbroker', 'hunter', 'remodel', 'sorcerer'] },
  { id: 'silvergold', name: '銀貨と金貨', cards: ['highwayman', 'official', 'abbey', 'crier', 'alembic', 'moneylender', 'mine', 'pawnbroker', 'command', 'attendant'] },
]);
defineCards({ id: 'base1', name: '基本（初版）' }, firstEdition, [
  { id: 'firstclassic', name: '初版のはじめて', cards: ['warehouse', 'market', 'mercenary', 'mine', 'moat', 'remodel', 'smithy', 'village', 'woodsman', 'workshop'] },
  { id: 'bigmoney', name: '大金持ち', cards: ['explorer', 'bursar', 'banquet', 'alembic', 'market', 'mine', 'pawnbroker', 'command', 'woodsman', 'scout'] },
  { id: 'interaction', name: 'かけひき', cards: ['official', 'bursar', 'assembly', 'fair', 'archive', 'mercenary', 'moat', 'scout', 'pickpocket', 'village'] },
]);
