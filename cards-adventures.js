'use strict';
// 拡張「冒険」のカード（30 種＋トラベラーの先 8 種）とイベント 20 種。名前は本家と別の言い回し。
// リザーブ: 使うと酒場マット（p.mats.tavern）に置き、決まったときに呼び出す（call）。
// トラベラー: 場から捨てるとき、次の段の札と取り替えてよい（exchange）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, playOutOfTurn, treasureEffect, later, laterFor, flipJourney, toTavern, offerCalls,
  returnCard, supplyOptions, pileOf, currentPlayer, playTreasureGen, takeFromSupply,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const D = ['action', 'duration'];
const R = ['action', 'reserve'];
const TR = ['action', 'traveller'];
const tav = (p) => (p.mats.tavern = p.mats.tavern || []);

function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
// トラベラー: 片付けで場から捨てるとき、next と取り替えてよい
function traveller(next) {
  return function* onCleanup(g, p, pi) {
    const self = this && this.id;
    if (!(g.nonSupply[next] > 0)) return;
    if (!(yield* askYesNo(g, pi, `${nm(self)}を${nm(next)}と取り替えますか？`, '取り替える', 'しない', [self, next]))) return;
    const at = g.playArea.lastIndexOf(self);
    if (at < 0) return;
    if (!returnCard(g, self)) return; // 戻す山がなければ取り替えない
    g.playArea.splice(at, 1);
    g.nonSupply[next] -= 1;
    p.discard.push(next);
    log(g, `${p.name}が${nm(self)}を${nm(next)}と取り替えた。`);
  };
}
// アクションの山を 1 つ選ぶ（印を置く先）
function* askActionPile(g, pi, purpose, maxCost = 99) {
  const piles = supplyOptions(g, maxCost, (id) => is(id, 'action')).concat(Object.keys(g.supply).filter((id) => g.supply[id] <= 0 && is(id, 'action')));
  const uniq = [...new Set(piles)];
  if (!uniq.length) return null;
  const [i] = yield* askCards(g, pi, purpose, uniq, 1, 1);
  return uniq[i ?? 0];
}
const pileToken = (key, label) => function* (g, p, pi) {
  const pile = yield* askActionPile(g, pi, `${label}の印を置くアクションの山を選ぶ`);
  if (pile) { p.tokens.pile[key] = pile; log(g, `${p.name}が${nm(pile)}の山に${label}の印を置いた。`); }
};

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'realmcoin', name: '通用貨', types: ['treasure', 'reserve'], cost: 2, value: 1, autoPlay: true, main: '+1 金', desc: '使ったら酒場マットに置く。アクションを使い終えた直後に呼び出して +2 アクション',
    *play(g, p) { toTavern(g, p, 'realmcoin'); },
    call: { when: 'afterAction', *run(g) { g.turn.actions += 2; } },
  },
  {
    id: 'lad', name: '小僧', types: TR, cost: 2, main: '+1 カード\n+1 アクション', desc: '場から捨てるとき「探し屋」と取り替えてよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; },
  },
  {
    id: 'farmer', name: '百姓', types: TR, cost: 2, main: '+1 購入\n+1 金', desc: '場から捨てるとき「足軽」と取り替えてよい',
    *play(g) { g.turn.buys += 1; g.turn.money += 1; },
  },
  {
    id: 'catpaw', name: '猫の手', types: R, cost: 2, main: '+1 カード\n+1 アクション', desc: '酒場マットに置く。手番の始めに呼び出して、手札を 1 枚廃棄する',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; toTavern(g, p, 'catpaw'); },
    call: { when: 'start', *run(g, p, pi) { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1))); } },
  },
  {
    id: 'wreck', name: '打ち壊し', cost: 2, main: '+1 アクション', desc: 'これか手札 1 枚を廃棄する。そのコストの数だけ山札の上から見て、1 枚を手札に、残りを捨てる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const v = !p.hand.length ? 'self' : yield* askChoose(g, pi, 'どれを廃棄しますか？', [{ value: 'self', label: 'この打ち壊し' }, { value: 'hand', label: '手札から 1 枚' }]);
      let id = null;
      if (v === 'self') { const at = g.playArea.lastIndexOf('wreck'); if (at >= 0) { [id] = g.playArea.splice(at, 1); yield* trashCards(g, p, [id]); } }
      else { const [i] = yield* askHand(g, pi, '廃棄する 1 枚', 1, 1); if (i != null) { [id] = takeFromHand(p, [i]); yield* trashCards(g, p, [id]); } }
      if (!id) return;
      const seen = reveal(p, costOf(g, id));
      if (!seen.length) return;
      const [k] = yield* askCards(g, pi, '手札に入れる 1 枚', seen, 1, 1);
      p.hand.push(...seen.splice(k ?? 0, 1));
      yield* discardCards(g, p, seen, true);
    },
  },
  // ---- コスト 3 ----
  {
    id: 'wardstone', name: '護り石', types: D, cost: 3, main: '今と次の手番に\n1 つ選ぶ', desc: '今と次の手番の始めに: +1 金 / 手札を 1 枚廃棄 / 銀を獲得 から 1 つ',
    *play(g, p, pi) {
      const once = function* () {
        const v = yield* askChoose(g, pi, '護り石: 1 つ選ぶ', [{ value: 'c', label: '+1 金' }, { value: 't', label: '手札を 1 枚廃棄' }, { value: 's', label: '銀を獲得' }]);
        if (v === 'c') g.turn.money += 1;
        else if (v === 't') yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)));
        else yield* gain(g, pi, 'silver');
      };
      yield* once();
      later(g, 'wardstone', once);
    },
  },
  {
    id: 'escort', name: '護衛兵', types: ['action', 'duration', 'reaction'], cost: 3, main: '+1 カード\n+1 アクション', desc: '次の手番の始めに +1 金。他の人がアタックを使ったとき、手札から使ってよい',
    *play(g, p, pi) {
      drawCards(p, 1);
      if (pi === g.current) g.turn.actions += 1;
      laterFor(g, pi, 'escort', function* () { g.turn.money += 1; });
    },
    *onAttack(g, t, ti) { t.hand.splice(t.hand.indexOf('escort'), 1); yield* playOutOfTurn(g, ti, 'escort'); },
  },
  {
    id: 'stonecell', name: '石牢', types: D, cost: 3, main: '+1 アクション', desc: '今と次の手番の始めに: +2 カードしてから 2 枚捨てる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const once = function* () { drawCards(p, 2); yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2))); };
      yield* once();
      later(g, 'stonecell', once);
    },
  },
  {
    id: 'kit', name: '旅支度', types: D, cost: 3, main: '+2 カード', desc: '手札を 2 枚まで脇に置き、次の手番の始めに手札に戻す',
    *play(g, p, pi) {
      drawCards(p, 2);
      const ids = takeFromHand(p, yield* askHand(g, pi, '次の手番まで取っておく札（2 枚まで）', 0, 2));
      if (!ids.length) return;
      (p.mats.kit = p.mats.kit || []).push(...ids);
      later(g, 'kit', function* () { for (const id of ids) { const k = p.mats.kit.indexOf(id); if (k >= 0) p.hand.push(...p.mats.kit.splice(k, 1)); } });
    },
  },
  {
    id: 'pathguide', name: '道案内', types: R, cost: 3, main: '+1 カード\n+1 アクション', desc: '酒場マットに置く。手番の始めに呼び出して、手札をすべて捨て 5 枚引く',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; toTavern(g, p, 'pathguide'); },
    call: { when: 'start', *run(g, p) { yield* discardCards(g, p, p.hand.splice(0), true); drawCards(p, 5); } },
  },
  // ---- コスト 4 ----
  {
    id: 'copycat', name: '写し', types: R, cost: 4, main: '酒場マットへ', desc: '酒場マットに置く。コスト 6 以下を獲得したとき呼び出して、同じ札をもう 1 枚獲得する',
    *play(g, p) { toTavern(g, p, 'copycat'); },
    call: {
      when: 'gain',
      can: (g, p, got) => costOf(g, got.id) <= 6 && g.supply[pileOf(got.id)] > 0 && !CARDS[got.id].potion,
      *run(g, p, pi, got) { yield* gain(g, pi, g.supply[got.id] != null ? got.id : pileOf(got.id)); },
    },
  },
  {
    id: 'crow', name: 'カラス', cost: 4, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくる。財宝なら手札に。アクションか勝利点ならカラスを獲得する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (is(id, 'treasure')) { p.hand.push(id); return; }
      putOnDeck(p, id);
      if (is(id, 'action') || is(id, 'victory')) yield* gain(g, pi, 'crow');
    },
  },
  {
    id: 'courier', name: '早馬', cost: 4, main: '+1 購入\n+2 金', desc: '山札をまとめて捨て札にしてよい。この手番の最初の購入でこれを買ったら、コスト 4 以下を獲得し、他の人も同じ札を獲得する',
    *play(g, p, pi) {
      g.turn.buys += 1; g.turn.money += 2;
      if (p.deck.length && (yield* askYesNo(g, pi, '山札をまとめて捨て札にしますか？', 'する', 'しない'))) p.discard.push(...p.deck.splice(0));
    },
    *onBuy(g, pi) {
      if (g.turn.bought.length + g.turn.events.length !== 1) return;
      const id = yield* askSupply(g, pi, 'コスト 4 以下を獲得（他の人も同じ札を獲得）', 4);
      if (!(yield* gain(g, pi, id))) return;
      const n = g.players.length;
      for (let k = 1; k < n; k++) yield* gain(g, (pi + k) % n, id);
    },
  },
  {
    id: 'skinflint', name: 'けちん坊', cost: 4, main: '銅を貯める', desc: '手札の銅を酒場マットに置くか、マットの銅 1 枚につき +1 金を得るかを選ぶ',
    *play(g, p, pi) {
      const n = tav(p).filter((id) => id === 'copper').length;
      const v = !p.hand.includes('copper') ? 'coin' : yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'put', label: '銅を酒場マットへ' }, { value: 'coin', label: `+${n} 金` }]);
      if (v === 'coin') g.turn.money += n; else tav(p).push(...takeFromHand(p, [p.hand.indexOf('copper')]));
    },
  },
  {
    id: 'harbor', name: '港', cost: 4, main: '+1 カード\n+2 アクション', desc: 'これを買ったとき、もう 1 枚獲得する',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onBuy(g, pi) { yield* gain(g, pi, 'harbor'); },
  },
  {
    id: 'forester', name: '森番', cost: 4, main: '+1 購入', desc: '旅の印を裏返す。表になったら +5 カード',
    *play(g, p) { g.turn.buys += 1; if (flipJourney(p)) drawCards(p, 5); },
  },
  {
    id: 'shapeshift', name: '化け替え', types: R, cost: 4, main: '+1 アクション', desc: '酒場マットに置く。手番の始めに呼び出して、手札を 1 枚廃棄し、コスト +1 以下を手札に獲得する',
    *play(g, p) { g.turn.actions += 1; toTavern(g, p, 'shapeshift'); },
    call: {
      when: 'start',
      *run(g, p, pi) {
        const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
        if (i == null) return;
        const [id] = takeFromHand(p, [i]);
        yield* trashCards(g, p, [id]);
        const max = costOf(g, id) + 1;
        yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を手札に獲得`, max), 'hand');
      },
    },
  },
  // ---- コスト 5 ----
  {
    id: 'tinkerer', name: 'からくり師', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: '好きな枚数捨てる。捨てた枚数とちょうど同じコストのカードを 1 枚、山札の上に獲得してよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1;
      const idx = yield* askHand(g, pi, '捨てる札（好きな枚数）', 0, p.hand.length);
      yield* discardCards(g, p, takeFromHand(p, idx));
      const n = idx.length;
      yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${n} を山札の上に獲得してよい`, n, (id) => costOf(g, id) === n, true), 'deck');
    },
  },
  {
    id: 'bridgeogre', name: '橋守の鬼', types: ['action', 'attack', 'duration'], cost: 5, main: '+1 購入\n（次の手番も）', desc: '他の人は -1 金の印を受け取る。今と次の手番に +1 購入。場にあるあいだ、自分の手番はカードのコストが 1 下がる',
    *play(g) {
      yield* attackOthers(g, function* (ti) { g.players[ti].tokens.minusCoin = true; });
      g.turn.buys += 1;
      later(g, 'bridgeogre', function* () { g.turn.buys += 1; });
    },
  },
  {
    id: 'bigman', name: '大男', types: ['action', 'attack'], cost: 5, main: '+1 金 か +5 金', desc: '旅の印を裏返す。裏なら +1 金。表なら +5 金、他の人は山札の一番上をめくり、コスト 3〜6 なら廃棄、そうでなければ捨てて災いを獲得',
    *play(g, p) {
      if (!flipJourney(p)) { g.turn.money += 1; yield* attackOthers(g, function* () {}); return; }
      g.turn.money += 5;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        if (costOf(g, id) >= 3 && costOf(g, id) <= 6) yield* trashCards(g, t, [id]);
        else { yield* discardCards(g, t, [id], true); yield* gain(g, ti, 'curse'); }
      });
    },
  },
  {
    id: 'mazewood', name: '迷いの森', types: ['action', 'attack', 'duration'], cost: 5, main: '次の手番に\n+3 カード', desc: '次の手番の始めまで、他の人はカードを買うたびに手札を好きな順で山札の上に置く。次の手番の始めに +3 カード',
    *play(g, p) {
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.mazewood = (g.players[ti].tokens.mazewood || 0) + 1; });
      later(g, 'mazewood', function* () { for (const ti of hit) g.players[ti].tokens.mazewood -= 1; drawCards(p, 3); });
    },
  },
  {
    id: 'phantomcity', name: '幻の都', cost: 5, main: '+2 カード\n+2 アクション', desc: 'これを獲得したとき、他の人は 1 枚引く',
    *play(g, p) { drawCards(p, 2); g.turn.actions += 2; },
    *onGain(g, got) { const n = g.players.length; for (let k = 1; k < n; k++) drawCards(g.players[(got.pi + k) % n], 1); },
  },
  {
    id: 'oldrelic', name: '古の宝', types: ['treasure', 'attack'], cost: 5, value: 2, autoPlay: true, main: '+2 金', desc: '他の人は -1 カードの印を山札の上に置く（次に引くとき 1 枚少ない）',
    *play(g) { yield* attackOthers(g, function* (ti) { g.players[ti].tokens.minusCard = true; }); },
  },
  {
    id: 'carriage', name: 'お召し馬車', types: R, cost: 5, main: '+1 アクション', desc: '酒場マットに置く。アクションを使い終えた直後、それが場にあれば呼び出して、もう一度使う',
    *play(g, p) { g.turn.actions += 1; toTavern(g, p, 'carriage'); },
    call: {
      when: 'afterAction',
      can: (g, p, ctx) => g.playArea.includes(ctx.id),
      once: true,
      *run(g, p, pi, ctx) { log(g, `${nm(ctx.id)}をもう一度使う。`); yield* resolve(g, ctx.id); },
    },
  },
  {
    id: 'raconteur', name: '講釈師', cost: 5, main: '+1 アクション\n+1 金', desc: '手札の財宝を 3 枚まで使う。そのあとお金をすべて払い、1 金につき +1 カード',
    *play(g, p, pi) {
      g.turn.actions += 1; g.turn.money += 1;
      const idx = yield* askHand(g, pi, '使う財宝（3 枚まで）', 0, 3, (id) => is(id, 'treasure'));
      for (const id of idx.map((i) => p.hand[i])) yield* playTreasureGen(g, id);
      const n = Math.max(0, g.turn.money);
      g.turn.money -= n;
      drawCards(p, n);
    },
  },
  {
    id: 'bogfiend', name: '沼の魔物', types: ['action', 'attack', 'duration'], cost: 5, main: '次の手番に\n+3 金', desc: '次の手番の始めまで、他の人はカードを買うたびに災いを獲得する。次の手番の始めに +3 金',
    *play(g) {
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.bogfiend = (g.players[ti].tokens.bogfiend || 0) + 1; });
      later(g, 'bogfiend', function* () { for (const ti of hit) g.players[ti].tokens.bogfiend -= 1; g.turn.money += 3; });
    },
  },
  {
    id: 'windfall', name: '掘り当て', types: ['treasure'], cost: 5, value: 2, autoPlay: true, main: '+2 金', desc: '使うと、金と銅を 1 枚ずつ獲得する',
    *play(g, p, pi) { yield* gain(g, pi, 'gold'); yield* gain(g, pi, 'copper'); },
  },
  {
    id: 'vintner', name: '酒屋', types: R, cost: 5, main: '+1 購入\n+4 金', desc: '酒場マットに置く。購入フェイズの終わりに 2 金以上残っていれば、マットから捨て札にしてよい',
    *play(g, p) { g.turn.buys += 1; g.turn.money += 4; toTavern(g, p, 'vintner'); },
    call: { when: 'buyEnd', can: (g) => g.turn.money >= 2, *run() {} },
  },
  {
    id: 'farland', name: '果ての地', types: ['action', 'reserve', 'victory'], cost: 5, main: '酒場マットで 4 点', desc: '酒場マットに置く。ゲームの終わりに酒場マットにあれば 4 点（ほかの場所では 0 点）',
    *play(g, p) { toTavern(g, p, 'farland'); },
    scoreBonus: (p) => 4 * (p.mats.tavern || []).filter((id) => id === 'farland').length,
  },
  // ---- コスト 6 ----
  {
    id: 'servant', name: '奉公人', types: D, cost: 6, main: 'ずっと毎手番\n+1 カード', desc: 'ゲームの終わりまで、自分の手番の始めに +1 カード（場に残り続ける）',
    *play(g, p) {
      const job = function* () { drawCards(p, 1); later(g, 'servant', job); };
      later(g, 'servant', job);
    },
  },
];

// ---- トラベラーの先の段（サプライ外、各 5 枚） ----
const travellers = [
  {
    id: 'seeker', name: '探し屋', types: TR, cost: 3, notSupply: true, main: '+1 アクション\n+1 金', desc: '右の人が前の手番に獲得した札 1 枚につき銀を獲得する。「戦士」と取り替えてよい',
    *play(g, p, pi) {
      g.turn.actions += 1; g.turn.money += 1;
      const right = g.players[(pi - 1 + g.players.length) % g.players.length];
      for (let k = 0; k < right.lastGains.length; k++) yield* gain(g, pi, 'silver');
    },
  },
  {
    id: 'fighter', name: '戦士', types: ['action', 'attack', 'traveller'], cost: 4, notSupply: true, main: '+2 カード', desc: '場のトラベラー 1 枚につき、他の人は山札の一番上を捨て、コスト 3 か 4 なら廃棄する。「英傑」と取り替えてよい',
    *play(g, p) {
      drawCards(p, 2);
      const n = g.playArea.filter((id) => is(id, 'traveller')).length;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        for (let k = 0; k < n; k++) {
          const [id] = reveal(t, 1);
          if (id == null) break;
          if (costOf(g, id) === 3 || costOf(g, id) === 4) yield* trashCards(g, t, [id]); else yield* discardCards(g, t, [id], true);
        }
      });
    },
  },
  {
    id: 'paragon', name: '英傑', types: TR, cost: 5, notSupply: true, main: '+2 金\n財宝を獲得', desc: '財宝を 1 枚獲得する。「覇者」と取り替えてよい',
    *play(g, p, pi) { g.turn.money += 2; yield* gain(g, pi, yield* askSupply(g, pi, '財宝を 1 枚獲得', 99, (id) => is(id, 'treasure'))); },
  },
  {
    id: 'victor', name: '覇者', types: D, cost: 6, notSupply: true, protects: true, main: '+1 アクション', desc: 'ゲームの終わりまで、他の人のアタックを受けず、アクションを使うたびに +1 アクション（場に残り続ける）',
    *play(g, p) {
      g.turn.actions += 1;
      p.tokens.victor = (p.tokens.victor || 0) + 1;
      const job = function* () { later(g, 'victor', job); };
      later(g, 'victor', job);
    },
  },
  {
    id: 'ashigaru', name: '足軽', types: ['action', 'attack', 'traveller'], cost: 3, notSupply: true, main: '+2 金', desc: '場のほかのアタック 1 枚につき +1 金。手札が 4 枚以上の他の人は 1 枚捨てる。「落ち武者」と取り替えてよい',
    *play(g) {
      g.turn.money += 2 + g.playArea.filter((id) => is(id, 'attack')).length - 1;
      yield* attackOthers(g, function* (ti) { if (g.players[ti].hand.length >= 4) yield* discardDownTo(g, ti, g.players[ti].hand.length - 1); });
    },
  },
  {
    id: 'deserter', name: '落ち武者', types: TR, cost: 4, notSupply: true, main: '+2 カード\n+1 アクション', desc: '手札を 1 枚捨てる。「門人」と取り替えてよい',
    *play(g, p, pi) { drawCards(p, 2); g.turn.actions += 1; yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚', 1, 1))); },
  },
  {
    id: 'follower', name: '門人', types: TR, cost: 5, notSupply: true, main: 'アクションを\n2 回使う', desc: '手札のアクションを 1 枚 2 回使い、同じ札を獲得してよい。「師範」と取り替えてよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '2 回使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      const before = p.nextTurn.length;
      yield* resolve(g, id); yield* resolve(g, id);
      if (p.nextTurn.length > before) g.turn.stay.push('follower');
      yield* gain(g, pi, pileOf(id) in g.supply ? pileOf(id) : id);
    },
  },
  {
    id: 'master', name: '師範', types: R, cost: 6, notSupply: true, main: '酒場マットへ', desc: '酒場マットに置く。手番の始めに呼び出して、+1 カード / +1 アクション / +1 購入 / +1 金 の印を、自分の印のないアクションの山に置く',
    *play(g, p) { toTavern(g, p, 'master'); },
    call: {
      when: 'start',
      *run(g, p, pi) {
        const k = yield* askChoose(g, pi, 'どの印を置きますか？', [{ value: 'card', label: '+1 カード' }, { value: 'action', label: '+1 アクション' }, { value: 'buy', label: '+1 購入' }, { value: 'coin', label: '+1 金' }]);
        const used = Object.values(p.tokens.pile);
        const piles = [...new Set(Object.keys(g.supply).filter((id) => is(id, 'action') && !used.includes(id)))];
        if (!piles.length) return;
        const [i] = yield* askCards(g, pi, '印を置く山を選ぶ', piles, 1, 1);
        p.tokens.pile[k] = piles[i ?? 0];
      },
    },
  },
];
const chain = { lad: 'seeker', seeker: 'fighter', fighter: 'paragon', paragon: 'victor', farmer: 'ashigaru', ashigaru: 'deserter', deserter: 'follower', follower: 'master' };
for (const c of [...kingdom, ...travellers]) if (chain[c.id]) c.onCleanup = traveller(chain[c.id]).bind(c);

// ---- イベント ----
const E = ['event'];
const events = [
  {
    id: 'e_soup', name: '炊き出し', types: E, cost: 0, once: true, main: 'コスト 4 以下を獲得', desc: '1 手番に 1 度: 場に財宝がなければ、コスト 4 以下を 1 枚獲得する',
    *buy(g, p, pi) { if (!g.playArea.some((id) => is(id, 'treasure'))) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4)); },
  },
  {
    id: 'e_advance', name: '前借り', types: E, cost: 0, once: true, main: '+1 購入', desc: '1 手番に 1 度: -1 カードの印がなければ、それを受け取って +1 金',
    *buy(g, p) { g.turn.buys += 1; if (!p.tokens.minusCard) { p.tokens.minusCard = true; g.turn.money += 1; } },
  },
  {
    id: 'e_trial', name: '腕試し', types: E, cost: 0, main: '捨てて金', desc: 'アタック 1 枚か、災い 2 枚か、好きな札 6 枚を捨ててよい。そうしたら金を獲得する',
    *buy(g, p, pi) {
      const ch = [{ value: 'no', label: 'しない' }];
      if (p.hand.some((id) => is(id, 'attack'))) ch.push({ value: 'a', label: 'アタックを 1 枚捨てる' });
      if (p.hand.filter((id) => id === 'curse').length >= 2) ch.push({ value: 'c', label: '災いを 2 枚捨てる' });
      if (p.hand.length >= 6) ch.push({ value: 's', label: '6 枚捨てる' });
      const v = yield* askChoose(g, pi, '腕試し', ch);
      if (v === 'no') return;
      if (v === 'a') yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てるアタック', 1, 1, (id) => is(id, 'attack'))));
      else if (v === 'c') yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる災い', 2, 2, (id) => id === 'curse')));
      else yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 6 枚', 6, 6)));
      yield* gain(g, pi, 'gold');
    },
  },
  {
    id: 'e_keep', name: '取り置き', types: E, cost: 1, once: true, main: '+1 購入', desc: '1 手番に 1 度: 手札を 1 枚脇に置き、手番の終わり（引いたあと）に手札に戻す',
    *buy(g, p, pi) {
      g.turn.buys += 1;
      const [i] = yield* askHand(g, pi, '取り置く 1 枚', 1, 1);
      if (i != null) (p.mats.keep = p.mats.keep || []).push(...takeFromHand(p, [i]));
    },
  },
  {
    id: 'e_scouts', name: '物見の衆', types: E, cost: 2, main: '+1 購入', desc: '山札の上 5 枚を見て、3 枚を捨て、残りを好きな順に戻す',
    *buy(g, p, pi) {
      g.turn.buys += 1;
      const seen = reveal(p, 5);
      const idx = yield* askCards(g, pi, '捨てる 3 枚', seen, 3, 3);
      yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)), true);
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    },
  },
  {
    id: 'e_travelfair', name: '旅回りの市', types: E, cost: 2, main: '+2 購入', desc: 'この手番、獲得した札を山札の上に置いてよい',
    *buy(g) { g.turn.buys += 2; g.turn.topdeckGains = true; },
  },
  { id: 'e_bonfire', name: 'どんど焼き', types: E, cost: 3, main: '場の札を廃棄', desc: '場の札を 2 枚まで廃棄する',
    *buy(g, p, pi) {
      const idx = yield* askCards(g, pi, '廃棄する場の札（2 枚まで）', [...g.playArea], 0, 2);
      const ids = [...idx].sort((a, b) => b - a).map((i) => g.playArea.splice(i, 1)[0]);
      yield* trashCards(g, p, ids);
    },
  },
  { id: 'e_outing', name: '遠出', types: E, cost: 3, main: '次の手札 +2 枚', desc: 'この手番の終わりに、2 枚多く引く', *buy(g) { g.turn.extraDraw = (g.turn.extraDraw || 0) + 2; } },
  { id: 'e_ferry', name: '舟便', types: E, cost: 3, main: '山のコストを下げる', desc: '-2 コストの印をアクションの山に置く（自分の手番、その山の札のコストが 2 下がる）', buy: pileToken('cost', '-2 コスト') },
  { id: 'e_plan', name: '段取り', types: E, cost: 3, main: '廃棄の印', desc: '廃棄の印をアクションの山に置く（その山の札を買うとき、手札を 1 枚廃棄してよい）', buy: pileToken('trash', '廃棄') },
  {
    id: 'e_errand', name: '使いの旅', types: E, cost: 4, once: true, main: '追加の手番', desc: '1 手番に 1 度: 前の手番が自分でなければ、この手番のあとに追加の手番を行う（その手番は買えない）',
    *buy(g) { if (!g.extraTurn) g.turn.mission = true; },
  },
  {
    id: 'e_pilgrim', name: 'お参り', types: E, cost: 4, once: true, main: '場の札を複製', desc: '1 手番に 1 度: 旅の印を裏返す。表になったら、場のちがう名前の札を 3 枚まで選び、それぞれ 1 枚獲得する',
    *buy(g, p, pi) {
      if (!flipJourney(p)) return;
      const names = [...new Set(g.playArea)].filter((id) => g.supply[pileOf(id)] > 0 || g.supply[id] > 0);
      const idx = yield* askCards(g, pi, '獲得する札（3 枚まで）', names, 0, 3);
      for (const i of idx) yield* gain(g, pi, g.supply[names[i]] != null ? names[i] : pileOf(names[i]));
    },
  },
  {
    id: 'e_soiree', name: '夜会', types: E, cost: 5, main: 'コスト 4 以下を 2 枚', desc: '-1 金の印を受け取る。コスト 4 以下を 2 枚獲得する',
    *buy(g, p, pi) {
      p.tokens.minusCoin = true;
      for (let k = 0; k < 2; k++) yield* gain(g, pi, yield* askSupply(g, pi, `コスト 4 以下を獲得（${k + 1}/2）`, 4));
    },
  },
  {
    id: 'e_nightraid', name: '夜討ち', types: E, cost: 5, main: '場の銀の数だけ銀', desc: '場の銀 1 枚につき銀を獲得する。他の人は -1 カードの印を受け取る',
    *buy(g, p, pi) {
      for (let k = g.playArea.filter((id) => id === 'silver').length; k > 0; k--) yield* gain(g, pi, 'silver');
      for (let k = 1; k < g.players.length; k++) g.players[(pi + k) % g.players.length].tokens.minusCard = true;
    },
  },
  {
    id: 'e_searoute', name: '航路開き', types: E, cost: 5, main: 'アクションを獲得\n+1 購入の印', desc: 'コスト 4 以下のアクションを獲得し、その山に +1 購入の印を置く',
    *buy(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下のアクションを獲得', 4, (x) => is(x, 'action'));
      if (yield* gain(g, pi, id)) p.tokens.pile.buy = id;
    },
  },
  {
    id: 'e_barter', name: '物々交換', types: E, cost: 5, main: '廃棄して銀', desc: '手札を 2 枚まで廃棄し、1 枚につき銀を獲得する',
    *buy(g, p, pi) {
      const ids = takeFromHand(p, yield* askHand(g, pi, '廃棄する札（2 枚まで）', 0, 2));
      yield* trashCards(g, p, ids);
      for (let k = 0; k < ids.length; k++) yield* gain(g, pi, 'silver');
    },
  },
  { id: 'e_inherit', name: '家督', types: E, cost: 7, main: '小屋にアクションを\n継がせる', desc: '1 ゲームに 1 度: サプライのコスト 4 以下の勝利点でないアクションを 1 枚脇に置く。自分の小屋は、そのアクションとしても使える',
    canBuy: (g) => !g.players[g.current].tokens.inherit,
    *buy(g, p, pi) {
      const id = yield* askSupply(g, pi, '小屋に継がせるアクション（コスト 4 以下）', 4, (x) => is(x, 'action') && !is(x, 'victory') && !is(x, 'command'));
      const c = id && takeFromSupply(g, id);
      if (!c) return;
      (p.mats.inherit = p.mats.inherit || []).push(c);
      p.tokens.inherit = c;
      log(g, `${p.name}の小屋は、これから${CARDS[c].name}としても使える。`);
    } },
  { id: 'e_secretart', name: '秘伝', types: E, cost: 6, main: '+1 アクションの印', desc: '+1 アクションの印をアクションの山に置く', buy: pileToken('action', '+1 アクション') },
  { id: 'e_practice', name: '修練', types: E, cost: 6, main: '+1 金の印', desc: '+1 金の印をアクションの山に置く', buy: pileToken('coin', '+1 金') },
  { id: 'e_signpost', name: '道しるべ', types: E, cost: 8, main: '+1 カードの印', desc: '+1 カードの印をアクションの山に置く', buy: pileToken('card', '+1 カード') },
];

// ---- どのカードにも関わる決まり ----
// 写し: 獲得したとき、酒場マットから呼び出せる
HOOKS.gain.push(function* (g, got) { yield* offerCalls(g, got.pi, 'gain', got); });
// 迷いの森・沼の魔物: 印を受けた人がカードを買ったとき
HOOKS.buy.push(function* (g, id, pi) {
  const p = g.players[pi];
  for (let k = 0; k < (p.tokens.bogfiend || 0); k++) yield* gain(g, pi, 'curse');
  if (p.tokens.mazewood > 0 && p.hand.length) { log(g, `${p.name}は迷いの森で手札を山札の上に置く。`); yield* putBackInOrder(g, pi, p.hand.splice(0)); }
});
// 覇者: アクションを使うたびに +1 アクション
HOOKS.play.push(function* (g) { const p = currentPlayer(g); if (p.tokens.victor) g.turn.actions += p.tokens.victor; });
// 橋守の鬼: 自分の手番に場にあれば、コストが 1 下がる
HOOKS.cost.push((g) => (g.playArea ? g.playArea.filter((x) => x === 'bridgeogre').length : 0));
HOOKS.setup.push((g) => {
  if (g.kingdom.includes('lad')) for (const id of ['seeker', 'fighter', 'paragon', 'victor']) g.nonSupply[id] = 5;
  if (g.kingdom.includes('farmer')) for (const id of ['ashigaru', 'deserter', 'follower', 'master']) g.nonSupply[id] = 5;
});

defineCards({ id: 'adventures', name: '冒険' }, [...kingdom, ...travellers, ...events], [
  { id: 'gentleintro', name: 'やさしい冒険', cards: ['realmcoin', 'catpaw', 'lad', 'kit', 'pathguide', 'harbor', 'forester', 'phantomcity', 'windfall', 'servant'], landscapes: ['e_scouts', 'e_bonfire'] },
  { id: 'expertintro', name: '腕利きの冒険', cards: ['farmer', 'wardstone', 'escort', 'copycat', 'crow', 'courier', 'bigman', 'mazewood', 'carriage', 'vintner'], landscapes: ['e_ferry', 'e_errand'] },
  { id: 'levelup', name: '腕を上げる（基本と混ぜる）', cards: ['stonecell', 'bigman', 'carriage', 'realmcoin', 'farmer', 'market', 'mercenary', 'sentinel', 'moneylender', 'command'], landscapes: ['e_practice', 'e_travelfair'] },
]);
