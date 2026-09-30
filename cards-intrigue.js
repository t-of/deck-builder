'use strict';
// 拡張「陰謀」のカード（第二版の 26 種と、初版だけにある 6 種）。名前は本家と別の言い回し。
import {
  CARDS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, resolve, reveal,
  putBackInOrder, supplyOptions, allCards, receive, takeFromSupply,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;

// 場（playArea）からこのカードを廃棄する。もう場にない（2 回目の効果など）なら false
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'backyard', name: '裏庭', cost: 2, main: '+3 カード', desc: '手札を 1 枚、山札の上に置く',
    *play(g, p, pi) {
      drawCards(p, 3);
      const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚を選ぶ', 1, 1);
      if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]);
    },
  },
  {
    id: 'prowler', name: '忍び', cost: 2, main: '+1 アクション', desc: 'サプライのアクションカードを 1 枚廃棄するか、廃棄置き場のアクションカードを 1 枚獲得する',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const inTrash = [...new Set(g.trash.filter((id) => is(id, 'action')))];
      const canTrash = supplyOptions(g, 99, (id) => is(id, 'action')).length > 0;
      const how = !inTrash.length ? 'trash' : !canTrash ? 'gain'
        : yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'trash', label: 'サプライから廃棄' }, { value: 'gain', label: '廃棄置き場から獲得' }]);
      if (how === 'trash') {
        const id = yield* askSupply(g, pi, 'サプライから廃棄するアクションを選ぶ', 99, (c) => is(c, 'action'));
        const c = id && takeFromSupply(g, id);
        if (c) yield* trashCards(g, p, [c]);
      } else if (inTrash.length) {
        const [i] = yield* askCards(g, pi, '廃棄置き場から獲得するアクションを選ぶ', inTrash, 1, 1);
        const id = inTrash[i ?? 0];
        g.trash.splice(g.trash.indexOf(id), 1);
        log(g, `${p.name}が廃棄置き場から${nm(id)}を獲得。`);
        yield* receive(g, pi, id);
      }
    },
  },
  {
    id: 'errand', name: '使い走り', cost: 2, main: '2 つ選ぶ', desc: '+1 カード / +1 アクション / +1 購入 / +1 金 から、ちがうものを 2 つ選ぶ',
    *play(g, p, pi) {
      const all = [{ value: 'card', label: '+1 カード' }, { value: 'action', label: '+1 アクション' }, { value: 'buy', label: '+1 購入' }, { value: 'coin', label: '+1 金' }];
      const a = yield* askChoose(g, pi, '1 つめを選ぶ', all);
      const b = yield* askChoose(g, pi, '2 つめを選ぶ', all.filter((c) => c.value !== a));
      for (const v of [a, b]) {
        if (v === 'card') drawCards(p, 1);
        else if (v === 'action') g.turn.actions += 1;
        else if (v === 'buy') g.turn.buys += 1;
        else g.turn.money += 1;
      }
    },
  },
  // ---- コスト 3 ----
  {
    id: 'carnival', name: '仮装行列', cost: 3, main: '+2 カード', desc: '手札のある全員が、手札を 1 枚ずつ左の人に同時に渡す。そのあと手札を 1 枚廃棄してよい',
    *play(g, p, pi) {
      drawCards(p, 2);
      const n = g.players.length;
      const order = Array.from({ length: n }, (_, k) => (pi + k) % n).filter((i) => g.players[i].hand.length);
      if (order.length > 1) {
        const passed = [];
        for (const i of order) {
          const [h] = yield* askHand(g, i, '左の人に渡す 1 枚を選ぶ', 1, 1);
          passed.push(takeFromHand(g.players[i], [h ?? 0])[0]);
        }
        order.forEach((i, k) => g.players[order[(k + 1) % order.length]].hand.push(passed[k]));
        log(g, '全員が 1 枚ずつ左に渡した。');
      }
      const [t] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ（しなくてもよい）', 0, 1);
      if (t != null) yield* trashCards(g, p, takeFromHand(p, [t]));
    },
  },
  {
    id: 'slum', name: '長屋', cost: 3, main: '+2 アクション', desc: '手札を見せる。アクションカードがなければ +2 カード',
    *play(g, p) {
      g.turn.actions += 2;
      if (!p.hand.some((id) => is(id, 'action'))) { drawCards(p, 2); log(g, `${p.name}の手札にアクションがなく、2 枚引いた。`); }
    },
  },
  {
    id: 'butler', name: '家令', cost: 3, main: '1 つ選ぶ', desc: '+2 カード / +2 金 / 手札を 2 枚廃棄 から 1 つ選ぶ',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'card', label: '+2 カード' }, { value: 'coin', label: '+2 金' }, { value: 'trash', label: '手札を 2 枚廃棄' }]);
      if (v === 'card') drawCards(p, 2);
      else if (v === 'coin') g.turn.money += 2;
      else yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 2 枚を選ぶ', 2, 2)));
    },
  },
  {
    id: 'conman', name: 'ぺてん師', types: ['action', 'attack'], cost: 3, main: '+2 金', desc: '他の人は山札の一番上を廃棄し、あなたが選んだ同じコストのカードを獲得する',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        yield* trashCards(g, t, [id]);
        const c = costOf(g, id);
        const pick = yield* askSupply(g, pi, `${t.name}に獲得させる、コスト ${c} のカード`, c, (x) => costOf(g, x) === c);
        yield* gain(g, ti, pick);
      });
    },
  },
  {
    id: 'fountain', name: '占いの泉', cost: 3, main: '+1 カード\n+1 アクション', desc: 'カードの名前を 1 つ言い、山札の一番上をめくる。当たればそれを手札に入れる',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const mine = [...new Set(allCards(p))];
      const guessIdx = yield* askCards(g, pi, '山札の一番上のカードを当てる', mine, 1, 1);
      const guess = mine[guessIdx[0] ?? 0];
      const [top] = reveal(p, 1);
      if (top == null) return;
      if (top === guess) { p.hand.push(top); log(g, `${p.name}が${nm(top)}を当てた！`); } else { putOnDeck(p, top); log(g, `${p.name}の予想ははずれ（${nm(top)}）。`); }
    },
  },
  // ---- コスト 4 ----
  {
    id: 'landlord', name: '地主', cost: 4, main: '+1 購入', desc: '小屋を 1 枚捨ててよい。捨てたら +4 金、捨てなければ小屋を 1 枚獲得する',
    *play(g, p, pi) {
      g.turn.buys += 1;
      if (p.hand.includes('estate') && (yield* askYesNo(g, pi, '小屋を捨てて +4 金にしますか？', '捨てる', '捨てない'))) {
        yield* discardCards(g, p, takeFromHand(p, [p.hand.indexOf('estate')]));
        g.turn.money += 4;
      } else yield* gain(g, pi, 'estate');
    },
  },
  {
    id: 'suspension', name: 'つり橋', cost: 4, main: '+1 購入\n+1 金', desc: 'この手番のあいだ、すべてのカードのコストが 1 下がる',
    *play(g) { g.turn.buys += 1; g.turn.money += 1; g.turn.costDown += 1; },
  },
  {
    id: 'plotter', name: '黒幕', cost: 4, main: '+2 金', desc: 'この手番にアクションを 3 回以上使っていたら（これも数える）+1 カード +1 アクション',
    *play(g, p) {
      g.turn.money += 2;
      if (g.turn.actionsPlayed >= 3) { drawCards(p, 1); g.turn.actions += 1; }
    },
  },
  {
    id: 'envoy', name: '使節', types: ['action', 'reaction'], cost: 4, main: '+2 カード', desc: '引いたあと手札が 5 枚以下なら +2 アクション。他の人のアタックのとき手札が 5 枚以上なら、見せて 2 枚引き、3 枚捨ててよい',
    *play(g, p) { drawCards(p, 2); if (p.hand.length <= 5) g.turn.actions += 2; },
    canReact: (g, t) => t.hand.length >= 5,
    *onAttack(g, t, ti) {
      drawCards(t, 2);
      yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, '捨てる 3 枚を選ぶ', 3, 3)));
    },
  },
  {
    id: 'foundry', name: '鋳造所', cost: 4, main: 'カードを獲得', desc: 'コスト 4 以下を 1 枚獲得する。それがアクションなら +1 アクション、財宝なら +1 金、勝利点なら +1 カード',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下を 1 枚獲得', 4);
      if (!(yield* gain(g, pi, id))) return;
      if (is(id, 'action')) g.turn.actions += 1;
      if (is(id, 'treasure')) g.turn.money += 1;
      if (is(id, 'victory')) drawCards(p, 1);
    },
  },
  {
    id: 'watermill', name: '水車小屋', types: ['action', 'victory'], cost: 4, points: 1, main: '+1 カード\n+1 アクション', desc: '手札を 2 枚捨ててよい。2 枚捨てたら +2 金。1 点',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      if (p.hand.length < 2 || !(yield* askYesNo(g, pi, '手札を 2 枚捨てて +2 金にしますか？', '捨てる', 'しない'))) return;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2)));
      g.turn.money += 2;
    },
  },
  {
    id: 'minetown', name: '鉱山町', cost: 4, main: '+1 カード\n+2 アクション', desc: 'このカードを廃棄してよい。そうしたら +2 金',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 2;
      if (g.playArea.includes('minetown') && (yield* askYesNo(g, pi, 'このカードを廃棄して +2 金にしますか？', '廃棄する', 'しない'))) {
        if (yield* trashSelf(g, p, 'minetown')) g.turn.money += 2;
      }
    },
  },
  {
    id: 'tunnel', name: '抜け道', cost: 4, main: '+2 カード\n+1 アクション', desc: '手札を 1 枚、山札の好きな位置に入れる',
    *play(g, p, pi) {
      drawCards(p, 2);
      g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '山札に入れる 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      const n = p.deck.length;
      const choices = [{ value: n, label: '一番上' }];
      for (let k = 1; k <= Math.min(4, n); k++) choices.push({ value: n - k, label: k === n ? '一番下' : `上から ${k + 1} 枚目` });
      const pos = choices.length === 1 ? n : yield* askChoose(g, pi, `${nm(id)}を入れる位置`, choices, [id]);
      p.deck.splice(pos, 0, id);
    },
  },
  // ---- コスト 5 ----
  {
    id: 'chamberlain', name: '侍従', cost: 5, main: '種類の数だけ選ぶ', desc: '手札を 1 枚見せる。その種類の数だけ、+1 アクション / +1 購入 / +3 金 / 金を獲得 からちがうものを選ぶ',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '見せる 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const id = p.hand[i];
      log(g, `${p.name}が${nm(id)}を見せた。`);
      let left = [{ value: 'action', label: '+1 アクション' }, { value: 'buy', label: '+1 購入' }, { value: 'coin', label: '+3 金' }, { value: 'gold', label: '金を獲得' }];
      for (let k = 0; k < Math.min(4, CARDS[id].types.length); k++) {
        const v = yield* askChoose(g, pi, `選ぶ（${k + 1}/${CARDS[id].types.length}）`, left);
        left = left.filter((c) => c.value !== v);
        if (v === 'action') g.turn.actions += 1;
        else if (v === 'buy') g.turn.buys += 1;
        else if (v === 'coin') g.turn.money += 3;
        else yield* gain(g, pi, 'gold');
      }
    },
  },
  {
    id: 'marquis', name: '荘園主', types: ['victory'], cost: 5, main: '荘園 1 枚ごとに 1 点', desc: '持っている荘園 1 枚につき 1 点',
    pointsFn: (all) => all.filter((id) => id === 'duchy').length,
  },
  {
    id: 'henchman', name: '子分', types: ['action', 'attack'], cost: 5, main: '+1 アクション', desc: '+2 金か、手札を捨てて 4 枚引くかを選ぶ。後者なら、手札が 5 枚以上の他の人も手札を捨てて 4 枚引く',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'coin', label: '+2 金' }, { value: 'redraw', label: '手札を捨てて 4 枚引く（他の人も）' }]);
      if (v === 'coin') g.turn.money += 2;
      const redraw = function* (t) { yield* discardCards(g, t, t.hand.splice(0), true); drawCards(t, 4); };
      if (v === 'redraw') yield* redraw(p);
      // アタックなので、+2 金を選んでも水濠などを見せる機会はある
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (v === 'redraw' && t.hand.length >= 5) { yield* redraw(t); log(g, `${t.name}が手札を捨てて 4 枚引いた。`); }
      });
    },
  },
  {
    id: 'nightwatch', name: '夜回り', cost: 5, main: '+3 カード', desc: '山札の上 4 枚をめくり、勝利点カードと災いを手札に入れる。残りは好きな順に戻す',
    *play(g, p, pi) {
      drawCards(p, 3);
      const shown = reveal(p, 4);
      const take = shown.filter((id) => is(id, 'victory') || is(id, 'curse'));
      p.hand.push(...take);
      if (take.length) log(g, `${p.name}が${take.map(nm).join('')}を手札に入れた。`);
      yield* putBackInOrder(g, pi, shown.filter((id) => !take.includes(id)));
    },
  },
  {
    id: 'swap', name: '取り替え', types: ['action', 'attack'], cost: 5, main: '廃棄して獲得', desc: '手札を 1 枚廃棄し、そのコスト +2 以下を獲得する。アクションか財宝なら山札の上へ。勝利点なら他の人は災いを獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      let got = null;
      if (i != null) {
        const [id] = takeFromHand(p, [i]);
        yield* trashCards(g, p, [id]);
        const max = costOf(g, id) + 2;
        got = yield* askSupply(g, pi, `コスト ${max} 以下を 1 枚獲得`, max, null, false, CARDS[id].potion || 0);
        const top = got && (is(got, 'action') || is(got, 'treasure'));
        if (!(yield* gain(g, pi, got, top ? 'deck' : 'discard'))) got = null;
      }
      yield* attackOthers(g, function* (ti) { if (got && is(got, 'victory')) yield* gain(g, ti, 'curse'); });
    },
  },
  {
    id: 'jailer', name: '牢番', types: ['action', 'attack'], cost: 5, main: '+3 カード', desc: '他の人は、手札を 2 枚捨てるか、災いを 1 枚手札に獲得するかを選ぶ',
    *play(g, p) {
      drawCards(p, 3);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const v = yield* askChoose(g, ti, '牢番のアタック。どちらにしますか？', [{ value: 'discard', label: '手札を 2 枚捨てる' }, { value: 'curse', label: '災いを手札に獲得' }]);
        if (v === 'discard') yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, '捨てる 2 枚を選ぶ', 2, 2)));
        else yield* gain(g, ti, 'curse', 'hand');
      });
    },
  },
  {
    id: 'tradepost', name: '取引所', cost: 5, main: '2 枚廃棄して\n銀を獲得', desc: '手札を 2 枚廃棄する。2 枚廃棄したら、銀を 1 枚手札に獲得する',
    *play(g, p, pi) {
      const idx = yield* askHand(g, pi, '廃棄する 2 枚を選ぶ', 2, 2);
      yield* trashCards(g, p, takeFromHand(p, idx));
      if (idx.length === 2) yield* gain(g, pi, 'silver', 'hand');
    },
  },
  {
    id: 'refine', name: '手直し', cost: 5, main: '+1 カード\n+1 アクション', desc: '手札を 1 枚廃棄し、ちょうどコスト +1 のカードを 1 枚獲得する',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id) + 1;
      yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} のカードを獲得`, c, (x) => costOf(g, x) === c));
    },
  },
  // ---- コスト 6 ----
  {
    id: 'mansion', name: '豪邸', types: ['treasure', 'victory'], cost: 6, value: 2, points: 2, main: '+2 金\n2 点', desc: '財宝としても勝利点としても使える',
  },
  {
    id: 'aristocrat', name: '貴人', types: ['action', 'victory'], cost: 6, points: 2, main: '+3 カード か\n+2 アクション', desc: '+3 カードか +2 アクションを選ぶ。2 点',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'card', label: '+3 カード' }, { value: 'action', label: '+2 アクション' }]);
      if (v === 'card') drawCards(p, 3); else g.turn.actions += 2;
    },
  },
];

const firstEdition = [
  {
    id: 'hideaway', name: '隠れ部屋', types: ['action', 'reaction'], cost: 2, main: '捨てた枚数\nだけ +金', desc: '手札を好きな枚数捨て、1 枚につき +1 金。他の人のアタックのとき見せて、2 枚引いてから手札を 2 枚山札の上に置いてよい',
    *play(g, p, pi) {
      const idx = yield* askHand(g, pi, '捨てるカードを選ぶ（1 枚につき +1 金）', 0, p.hand.length);
      yield* discardCards(g, p, takeFromHand(p, idx));
      g.turn.money += idx.length;
    },
    *onAttack(g, t, ti) {
      drawCards(t, 2);
      const idx = yield* askHand(g, ti, '山札の上に置く 2 枚を選ぶ', 2, 2);
      yield* putBackInOrder(g, ti, takeFromHand(t, idx));
    },
  },
  {
    id: 'hall', name: '広間', types: ['action', 'victory'], cost: 3, points: 1, main: '+1 カード\n+1 アクション', desc: '1 点',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; },
  },
  {
    id: 'tinker', name: '鋳物師', cost: 4, main: '銅 +1 金', desc: 'この手番のあいだ、銅を出すたびに +1 金',
    *play(g) { g.turn.copperBonus += 1; },
  },
  {
    id: 'surveyor', name: '測量士', cost: 4, main: '+1 アクション', desc: '山札の上 4 枚をめくり、勝利点カードを手札に入れる。残りは好きな順に戻す',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const shown = reveal(p, 4);
      const take = shown.filter((id) => is(id, 'victory'));
      p.hand.push(...take);
      yield* putBackInOrder(g, pi, shown.filter((id) => !is(id, 'victory')));
    },
  },
  {
    id: 'wrecker', name: '壊し屋', types: ['action', 'attack'], cost: 5, main: '壊す', desc: '他の人はコスト 3 以上が出るまで山札をめくり、それを廃棄する。そのコスト -2 以下を獲得してよい。ほかにめくった札は捨てる',
    *play(g) {
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const other = [];
        let hit = null;
        for (let id = takeTop(t); id != null; id = takeTop(t)) {
          if (costOf(g, id) >= 3) { hit = id; break; }
          other.push(id);
        }
        if (hit) {
          yield* trashCards(g, t, [hit]);
          const max = costOf(g, hit) - 2;
          yield* gain(g, ti, yield* askSupply(g, ti, `コスト ${max} 以下を獲得してよい`, max, null, true));
        }
        yield* discardCards(g, t, other, true);
      });
    },
  },
  {
    id: 'toll', name: '通行料', cost: 5, main: '左の人の札で\n得をする', desc: '左の人が山札の上 2 枚をめくって捨てる。ちがう名前 1 枚ごとに、アクションなら +2 アクション、財宝なら +2 金、勝利点なら +2 カード',
    *play(g, p) {
      const left = g.players[(g.current + 1) % g.players.length];
      const shown = reveal(left, 2);
      yield* discardCards(g, left, shown, true);
      if (shown.length) log(g, `${left.name}がめくった: ${shown.map(nm).join('')}`);
      for (const id of new Set(shown)) {
        if (is(id, 'action')) g.turn.actions += 2;
        if (is(id, 'treasure')) g.turn.money += 2;
        if (is(id, 'victory')) drawCards(p, 2);
      }
    },
  },
].map((c) => ({ ...c, set: 'intrigue1' }));

defineCards({ id: 'intrigue', name: '陰謀' }, kingdom, [
  { id: 'victorydance', name: '勝利の舞', cards: ['landlord', 'chamberlain', 'marquis', 'mansion', 'foundry', 'carnival', 'watermill', 'aristocrat', 'nightwatch', 'swap'] },
  { id: 'schemes', name: 'たくらみ', cards: ['backyard', 'prowler', 'errand', 'slum', 'butler', 'conman', 'suspension', 'plotter', 'tunnel', 'jailer'] },
  { id: 'wishes', name: '願かけ', cards: ['landlord', 'plotter', 'backyard', 'envoy', 'marquis', 'tunnel', 'slum', 'jailer', 'refine', 'fountain'] },
  { id: 'underlings', name: '手下たち（基本と混ぜる）', cards: ['warehouse', 'fair', 'archive', 'sentinel', 'attendant', 'chamberlain', 'envoy', 'henchman', 'aristocrat', 'errand'] },
  { id: 'grandscheme', name: '大仕掛け（基本と混ぜる）', cards: ['official', 'command', 'alembic', 'market', 'moat', 'carnival', 'suspension', 'foundry', 'tradepost', 'swap'] },
]);
defineCards({ id: 'intrigue1', name: '陰謀（初版）' }, firstEdition, [
  { id: 'intrigueclassic', name: '初版の陰謀', cards: ['hideaway', 'hall', 'tinker', 'surveyor', 'wrecker', 'toll', 'landlord', 'suspension', 'errand', 'slum'] },
]);
