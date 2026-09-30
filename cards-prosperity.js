'use strict';
// 拡張「繁栄」のカード（第二版の 25 種、初版だけにある 9 種、新天地・白金）。名前は本家と別の言い回し。
// 勝利点トークン: player.tokens.vp（点に足す）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, currentPlayer, treasureEffect, emptyPiles,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const vp = (g, p, n) => { if (!n) return; p.tokens.vp = (p.tokens.vp || 0) + n; log(g, `${p.name}が勝利点トークンを ${n} 得た。`); };
const T = ['treasure'];
const leftOf = (g, pi) => (pi + 1) % g.players.length;

// 手札以外から財宝を場に出して使う
function* playTreasureFrom(g, id) {
  g.playArea.push(id);
  log(g, `${currentPlayer(g).name}が${nm(id)}を出した。`);
  yield* treasureEffect(g, id);
}
// 財宝が出るまで山札をめくる。財宝（なければ null）と、ほかにめくった札
function revealUntilTreasure(p) {
  const other = [];
  for (let id = takeTop(p); id != null; id = takeTop(p)) {
    if (is(id, 'treasure')) return { hit: id, other };
    other.push(id);
  }
  return { hit: null, other };
}
// 左の人に、買えない（獲得できない）カードを 1 つ言わせる
function* nameCard(g, pi, purpose) {
  const li = leftOf(g, pi);
  const piles = Object.keys(g.supply).filter((id) => g.supply[id] > 0);
  const [i] = yield* askCards(g, li, purpose, piles, 1, 1);
  const id = piles[i ?? 0];
  log(g, `${g.players[li].name}が${nm(id)}を指定した。`);
  return id;
}

const basics = [
  { id: 'platinum', name: '白金', types: T, cost: 9, value: 5, notSupply: true, main: '+5 金', desc: '使うと、お金が 5 増える' },
  { id: 'colony', name: '新天地', types: ['victory'], cost: 11, points: 10, notSupply: true, main: '10 点', desc: 'ゲームの終わりに数える。この山が空になってもゲームが終わる' },
];

const kingdom = [
  // ---- コスト 3 ----
  {
    id: 'firetower', name: '火の見やぐら', types: ['action', 'reaction'], cost: 3, main: '6 枚まで引く', desc: '手札が 6 枚になるまで引く。カードを獲得したとき手札から見せて、それを廃棄するか山札の上に置いてよい',
    *play(g, p) { drawCards(p, Math.max(0, 6 - p.hand.length)); },
    *reactGain(g, got) {
      const v = yield* askChoose(g, got.pi, `${nm(got.id)}を獲得した。「火の見やぐら」を見せますか？`, [
        { value: 'no', label: '見せない' }, { value: 'trash', label: '見せて廃棄' }, { value: 'deck', label: '見せて山札の上へ' },
      ], [got.id]);
      if (v !== 'no') yield* relocate(g, got, v);
    },
  },
  {
    id: 'anvil', name: '打ち台', types: T, cost: 3, value: 1, main: '+1 金', desc: '手札の財宝を 1 枚捨ててよい。捨てたらコスト 4 以下を 1 枚獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '捨てる財宝を選ぶ（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      yield* discardCards(g, p, takeFromHand(p, [i]));
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を 1 枚獲得', 4));
    },
  },
  // ---- コスト 4 ----
  {
    id: 'prelate', name: '高僧', cost: 4, main: '+1 金\n+1 勝利点トークン', desc: '手札を 1 枚廃棄し、そのコスト 2 につき +1 勝利点トークン。他の人は手札を 1 枚廃棄してよい',
    *play(g, p, pi) {
      g.turn.money += 1;
      vp(g, p, 1);
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i != null) {
        const [id] = takeFromHand(p, [i]);
        yield* trashCards(g, p, [id]);
        vp(g, p, Math.floor(costOf(g, id) / 2));
      }
      yield* eachOther(g, function* (ti) {
        const t = g.players[ti];
        const [k] = yield* askHand(g, ti, '「高僧」: 手札を 1 枚廃棄してよい', 0, 1);
        if (k != null) yield* trashCards(g, t, takeFromHand(t, [k]));
      });
    },
  },
  {
    id: 'stele', name: '石碑', cost: 4, main: '+2 金\n+1 勝利点トークン', desc: '',
    *play(g, p) { g.turn.money += 2; vp(g, p, 1); },
  },
  {
    id: 'stoneyard', name: '石工場', types: T, cost: 4, value: 1, autoPlay: true, main: '+1 金', desc: 'この手番のあいだ、アクションカードのコストが 2 下がる',
    *play(g) { g.turn.actionCostDown += 2; },
  },
  {
    id: 'artisanrow', name: '職人町', cost: 4, main: '+1 カード　+2 アクション\n+1 購入', desc: '',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; g.turn.buys += 1; },
  },
  {
    id: 'scribe', name: '書役', types: ['action', 'reaction', 'attack'], cost: 4, main: '+2 金', desc: '手札が 5 枚以上の他の人は、1 枚を山札の上に置く。自分の手番の始めに、手札から使ってよい',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 5) return;
        const [i] = yield* askHand(g, ti, '山札の上に置く 1 枚を選ぶ', 1, 1);
        if (i != null) putOnDeck(t, takeFromHand(t, [i])[0]);
      });
    },
    *atTurnStart(g, p, pi) {
      while (p.hand.includes('scribe') && (yield* askYesNo(g, pi, '手番の始めに「書役」を使いますか？', '使う', '使わない', ['scribe']))) {
        p.hand.splice(p.hand.indexOf('scribe'), 1);
        g.playArea.push('scribe');
        log(g, `${p.name}が「書役」を使用。`);
        yield* resolve(g, 'scribe');
      }
    },
  },
  {
    id: 'stake', name: '種銭', types: T, cost: 4, main: '廃棄して\n+1 金 か 点', desc: '手札を 1 枚廃棄する。+1 金か、このカードを廃棄して手札を見せ、ちがう名前の財宝 1 種につき +1 勝利点トークン',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
      const kinds = new Set(p.hand.filter((id) => is(id, 'treasure'))).size;
      const v = yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'coin', label: '+1 金' }, { value: 'vp', label: `これを廃棄して +${kinds} 勝利点トークン` }]);
      if (v === 'coin') { g.turn.money += 1; return; }
      const at = g.playArea.lastIndexOf('stake');
      if (at >= 0) { yield* trashCards(g, p, g.playArea.splice(at, 1)); vp(g, p, kinds); }
    },
  },
  {
    id: 'diadem', name: '髪飾り', types: T, cost: 4, main: '+1 購入', desc: 'この手番、獲得したカードを山札の上に置いてよい。手札の財宝を 1 枚、2 回使ってよい',
    *play(g, p, pi) {
      g.turn.buys += 1;
      g.turn.topdeckGains = true;
      const [i] = yield* askHand(g, pi, '2 回使う財宝を選ぶ（なしでもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      yield* treasureEffect(g, id);
      yield* treasureEffect(g, id);
    },
  },
  // ---- コスト 5 ----
  {
    id: 'castletown', name: '城下町', cost: 5, main: '+1 カード\n+2 アクション', desc: '空の山が 1 つ以上あれば +1 カード。2 つ以上なら、さらに +1 購入 +1 金',
    *play(g, p) {
      drawCards(p, 1);
      g.turn.actions += 2;
      const e = emptyPiles(g);
      if (e >= 1) drawCards(p, 1);
      if (e >= 2) { g.turn.buys += 1; g.turn.money += 1; }
    },
  },
  {
    id: 'coinery', name: '鋳貨所', cost: 5, main: '財宝を複製', desc: '手札の財宝を 1 枚見せ、同じものを 1 枚獲得してよい。これを獲得したとき、場の（持続でない）財宝をすべて廃棄する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '見せる財宝を選ぶ（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i != null) yield* gain(g, pi, p.hand[i]);
    },
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      const tr = g.playArea.filter((id) => is(id, 'treasure') && !is(id, 'duration'));
      g.playArea = g.playArea.filter((id) => !(is(id, 'treasure') && !is(id, 'duration')));
      yield* trashCards(g, g.players[got.pi], tr);
    },
  },
  {
    id: 'mob', name: '群衆', types: ['action', 'attack'], cost: 5, main: '+3 カード', desc: '他の人は山札の上 3 枚をめくり、アクションと財宝を捨て、残りを好きな順に戻す',
    *play(g, p) {
      drawCards(p, 3);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 3);
        const out = shown.filter((id) => is(id, 'action') || is(id, 'treasure'));
        yield* discardCards(g, t, out);
        yield* putBackInOrder(g, ti, shown.filter((id) => !out.includes(id)));
      });
    },
  },
  {
    id: 'safebox', name: '貸し金庫', cost: 5, main: '+2 カード', desc: '手札を好きな枚数捨て、1 枚につき +1 金。他の人は 2 枚捨ててよい。そうしたら 1 枚引く',
    *play(g, p, pi) {
      drawCards(p, 2);
      const idx = yield* askHand(g, pi, '捨てるカードを選ぶ（1 枚につき +1 金）', 0, p.hand.length);
      yield* discardCards(g, p, takeFromHand(p, idx));
      g.turn.money += idx.length;
      yield* eachOther(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 2 || !(yield* askYesNo(g, ti, '「貸し金庫」: 2 枚捨てて 1 枚引きますか？', '捨てて引く', 'しない'))) return;
        yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, '捨てる 2 枚を選ぶ', 2, 2)));
        drawCards(t, 1);
      });
    },
  },
  {
    id: 'charlatan', name: 'まやかし師', types: ['action', 'attack'], cost: 5, main: '+3 金', desc: '他の人は災いを獲得する。このゲームでは、災いは 1 金の財宝でもある',
    *play(g) {
      g.turn.money += 3;
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    },
  },
  {
    id: 'curio', name: '蒐集箱', types: T, cost: 5, value: 2, autoPlay: true, main: '+2 金　+1 購入', desc: 'この手番、アクションカードを獲得するたびに +1 勝利点トークン',
    *play(g) { g.turn.buys += 1; g.turn.curio = (g.turn.curio || 0) + 1; },
  },
  {
    id: 'orb', name: '占い玉', types: T, cost: 5, value: 1, main: '+1 金', desc: '山札の一番上を見て、廃棄・捨てる・（アクションか財宝なら）使う、のどれかをしてよい',
    *play(g, p, pi) {
      const [id] = reveal(p, 1);
      if (id == null) return;
      const ch = [{ value: 'keep', label: '戻す' }, { value: 'trash', label: '廃棄' }, { value: 'discard', label: '捨てる' }];
      if (is(id, 'action') || is(id, 'treasure')) ch.push({ value: 'play', label: '使う' });
      const v = yield* askChoose(g, pi, `山札の一番上は${nm(id)}`, ch, [id]);
      if (v === 'keep') putOnDeck(p, id);
      else if (v === 'trash') yield* trashCards(g, p, [id]);
      else if (v === 'discard') yield* discardCards(g, p, [id]);
      else if (is(id, 'treasure') && !is(id, 'action')) yield* playTreasureFrom(g, id);
      else { g.playArea.push(id); log(g, `${p.name}が${nm(id)}を使用。`); yield* resolve(g, id); }
    },
  },
  {
    id: 'tycoon', name: '大旦那', cost: 5, main: '財宝の数だけ引く', desc: '手札を見せ、その中の財宝 1 枚につき +1 カード',
    *play(g, p) { drawCards(p, p.hand.filter((id) => is(id, 'treasure')).length); },
  },
  {
    id: 'warfund', name: '軍資金', types: T, cost: 5, main: 'カードを獲得', desc: '左の人がカードを 1 つ指定する。この手番に軍資金で指定されていない、コスト 5 以下を 1 枚獲得する',
    *play(g, p, pi) {
      const named = yield* nameCard(g, pi, '「軍資金」で獲得させないカードを指定する');
      (g.turn.warfund = g.turn.warfund || []).push(named);
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を 1 枚獲得', 5, (id) => !g.turn.warfund.includes(id)));
    },
  },
  // ---- コスト 6 ----
  {
    id: 'boulevard', name: '大通り', cost: 6, main: '+1 カード　+1 アクション\n+1 購入　+2 金', desc: '銅を場に出していると買えない',
    canBuy: (g) => !g.playArea.includes('copper'),
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; g.turn.money += 2; },
  },
  {
    id: 'stash', name: '隠し銭', types: T, cost: 6, value: 2, main: '+2 金', desc: 'この手番、勝利点カードを買うたびに金を 1 枚獲得する',
    *whenBuy(g, id, pi) { if (is(id, 'victory')) yield* gain(g, pi, 'gold'); },
  },
  // ---- コスト 7 以上 ----
  {
    id: 'banker', name: '金融屋', types: T, cost: 7, autoPlay: true, main: '場の財宝 1 枚\nにつき +1 金', desc: '場に出している財宝（これも含む）1 枚につき +1 金',
    *play(g) { g.turn.money += g.playArea.filter((id) => is(id, 'treasure')).length; },
  },
  {
    id: 'extension', name: '建て増し', cost: 7, main: '廃棄して獲得', desc: '手札を 1 枚廃棄し、そのコスト +3 以下を 1 枚獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 3;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を 1 枚獲得`, max, null, false, CARDS[id].potion || 0));
    },
  },
  {
    id: 'crucible', name: 'るつぼ', cost: 7, main: 'まとめて廃棄\nして獲得', desc: '手札を好きな枚数廃棄し、そのコストの合計とちょうど同じコストのカードを 1 枚獲得する',
    *play(g, p, pi) {
      const idx = yield* askHand(g, pi, '廃棄するカードを選ぶ（好きな枚数）', 0, p.hand.length);
      const ids = takeFromHand(p, idx);
      yield* trashCards(g, p, ids);
      const sum = ids.reduce((a, id) => a + costOf(g, id), 0);
      yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${sum} のカードを獲得`, sum, (id) => costOf(g, id) === sum));
    },
  },
  {
    id: 'council', name: '御前会議', cost: 7, main: 'アクションを\n3 回使う', desc: '手札のアクションカードを 1 枚、3 回使ってよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '3 回使うアクションを選ぶ（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      log(g, `${p.name}が${nm(id)}を 3 回使う。`);
      const before = p.nextTurn.length;
      for (let k = 0; k < 3; k++) yield* resolve(g, id);
      if (p.nextTurn.length > before) g.turn.stay.push('council');
    },
  },
  {
    id: 'hawker', name: '呼び売り', cost: 8, main: '+1 カード　+1 アクション\n+1 金', desc: '購入フェイズのあいだ、場のアクションカード 1 枚につき、コストが 2 下がる',
    costAdjust: (g) => (g.turn && g.turn.phase === 'buy' ? 2 * g.playArea.filter((id) => is(id, 'action')).length : 0),
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1; },
  },
];

const firstEdition = [
  {
    id: 'iou', name: '借用書', types: T, cost: 3, value: 1, main: '+1 金', desc: '財宝が出るまで山札をめくり、その財宝を捨てるか廃棄する。ほかにめくった札は捨てる',
    *play(g, p, pi) {
      const { hit, other } = revealUntilTreasure(p);
      yield* discardCards(g, p, other, true);
      if (!hit) return;
      if (yield* askYesNo(g, pi, `めくった財宝は${nm(hit)}。どうしますか？`, '廃棄', '捨てる', [hit])) yield* trashCards(g, p, [hit]);
      else yield* discardCards(g, p, [hit], true);
    },
  },
  {
    id: 'traderoute', name: '通商路', cost: 3, main: '+1 購入', desc: '勝利点の山から初めてカードが獲得されるたびに印が 1 つ増え、印 1 つにつき +1 金。手札を 1 枚廃棄する',
    *play(g, p, pi) {
      g.turn.buys += 1;
      g.turn.money += g.traderoute ? g.traderoute.mat : 0;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
    },
  },
  {
    id: 'charm', name: 'お守り', types: T, cost: 4, value: 1, main: '+1 金', desc: '場にあるあいだ、コスト 4 以下の勝利点以外のカードを買うたびに、同じものをもう 1 枚獲得する',
    *whenBuy(g, id, pi) { if (!is(id, 'victory') && costOf(g, id) <= 4) yield* gain(g, pi, id); },
  },
  {
    id: 'tally', name: '勘定場', cost: 5, main: '捨て札の銅を\n手札に', desc: '捨て札を見て、好きな枚数の銅を手札に入れる',
    *play(g, p, pi) {
      const n = p.discard.filter((id) => id === 'copper').length;
      if (!n) return;
      const k = yield* askChoose(g, pi, `捨て札の銅 ${n} 枚のうち、何枚手札に入れますか？`, Array.from({ length: n + 1 }, (_, j) => ({ value: n - j, label: `${n - j} 枚` })));
      for (let j = 0; j < k; j++) { p.discard.splice(p.discard.indexOf('copper'), 1); p.hand.push('copper'); }
    },
  },
  {
    id: 'forbidden', name: 'ご禁制', types: T, cost: 5, value: 3, main: '+3 金　+1 購入', desc: '左の人がカードを 1 つ指定する。この手番、それは買えない',
    *play(g, p, pi) {
      g.turn.buys += 1;
      g.turn.banned.push(yield* nameCard(g, pi, '「ご禁制」で買えなくするカードを指定する'));
    },
  },
  {
    id: 'quack', name: 'いかさま薬売り', types: ['action', 'attack'], cost: 5, main: '+2 金', desc: '他の人は手札の災いを 1 枚捨ててよい。捨てなければ、災いと銅を 1 枚ずつ獲得する',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.includes('curse') && (yield* askYesNo(g, ti, '手札の災いを捨てますか？（捨てなければ災いと銅を獲得）', '捨てる', '捨てない', ['curse']))) {
          yield* discardCards(g, t, takeFromHand(t, [t.hand.indexOf('curse')]));
          return;
        }
        yield* gain(g, ti, 'curse');
        yield* gain(g, ti, 'copper');
      });
    },
  },
  {
    id: 'seal', name: '御印', types: T, cost: 5, value: 2, main: '+2 金', desc: '場にあるあいだ、カードを獲得するたびに、それを山札の上に置いてよい',
    *whenGain(g, got) {
      if (got.to === 'deck' || got.to === 'trash') return;
      if (yield* askYesNo(g, got.pi, `獲得した${nm(got.id)}を山札の上に置きますか？`, '山札の上へ', 'そのまま', [got.id])) yield* relocate(g, got, 'deck');
    },
  },
  {
    id: 'gamble', name: '山っ気', types: T, cost: 5, value: 1, main: '+1 金', desc: '財宝が出るまで山札をめくり、その財宝を場に出して使う。ほかにめくった札は捨てる',
    *play(g, p) {
      const { hit, other } = revealUntilTreasure(p);
      yield* discardCards(g, p, other, true);
      if (hit) yield* playTreasureFrom(g, hit);
    },
  },
  {
    id: 'bouncer', name: '用心棒', types: ['action', 'attack'], cost: 6, main: '+1 購入\n+2 金', desc: '他の人は手札が 3 枚になるまで捨てる。場にあるあいだ、カードを買うたびに +1 勝利点トークン',
    *play(g) {
      g.turn.buys += 1;
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const need = t.hand.length - 3;
        if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が 3 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
      });
    },
    *whenBuy(g, id, pi) { vp(g, g.players[pi], 1); },
  },
].map((c) => ({ ...c, set: 'prosperity1' }));

// 髪飾り: この手番に獲得した札を山札の上に置いてよい（場の「髪飾り」の数に関係なく 1 回問う）
// 蒐集箱: この手番、アクションを獲得するたびに +1 勝利点トークン
// 通商路: 勝利点の山から初めて獲得されたら印を 1 つマットへ
HOOKS.gain.push(function* (g, got) {
  if (got.pi !== g.current) return;
  if (g.turn.curio && is(got.id, 'action')) vp(g, g.players[got.pi], g.turn.curio);

});
HOOKS.gain.push(function* (g, got) {
  const tr = g.traderoute;
  if (tr && tr.piles.includes(got.id)) { tr.piles.splice(tr.piles.indexOf(got.id), 1); tr.mat += 1; }
});
HOOKS.setup.push((g) => {
  g.traderoute = g.kingdom.includes('traderoute')
    ? { piles: Object.keys(g.supply).filter((id) => is(id, 'victory')), mat: 0 } : null;
});
// まやかし師: このゲームでは災いが 1 金の財宝にもなる
const curse = () => CARDS.curse;
HOOKS.setup.push((g) => {
  curse().types = g.kingdom.includes('charlatan') ? ['curse', 'treasure'] : ['curse'];
  curse().value = g.kingdom.includes('charlatan') ? 1 : undefined;
});

defineCards({ id: 'prosperity', name: '繁栄' }, [...basics, ...kingdom], [
  { id: 'beginners', name: 'はじめての繁栄', cards: ['banker', 'castletown', 'extension', 'boulevard', 'council', 'safebox', 'artisanrow', 'stele', 'crucible', 'firetower'] },
  { id: 'friendlyinteractive', name: 'なかよく競う', cards: ['prelate', 'castletown', 'scribe', 'curio', 'hawker', 'mob', 'stoneyard', 'diadem', 'warfund', 'artisanrow'] },
  { id: 'bigactions', name: '大きなアクション', cards: ['castletown', 'extension', 'crucible', 'boulevard', 'council', 'coinery', 'charlatan', 'tycoon', 'stake', 'orb'] },
  { id: 'biggestmoney', name: 'お金持ち（基本と混ぜる）', cards: ['banker', 'boulevard', 'mob', 'stash', 'hawker', 'alembic', 'market', 'mine', 'pawnbroker', 'craftsman'] },
]);
defineCards({ id: 'prosperity1', name: '繁栄（初版）' }, firstEdition, [
  { id: 'prosperityclassic', name: '初版の繁栄', cards: ['iou', 'traderoute', 'charm', 'tally', 'forbidden', 'quack', 'seal', 'gamble', 'bouncer', 'banker'] },
]);
