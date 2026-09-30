'use strict';
// 単品で出たカード（プロモ）13 種。名前は本家と別の言い回し。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  treasureEffect, later, currentPlayer, receive, kingdomPool, shuffle, pileOf,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;

function* playFromHand(g, pi, pred, purpose) {
  const p = g.players[pi];
  const [i] = yield* askHand(g, pi, purpose, 0, 1, pred);
  if (i == null) return;
  const [id] = takeFromHand(p, [i]);
  g.playArea.push(id);
  log(g, `${p.name}が${nm(id)}を使用。`);
  yield* resolve(g, id);
}
// サプライのアクションをその場で使う（札はサプライに残る）
function* playFromSupply(g, pi, max) {
  const id = yield* askSupply(g, pi, `使うアクション（コスト ${max} 以下・持続と命令以外）`, max, (x) => is(x, 'action') && !is(x, 'duration') && !is(x, 'command'), true);
  if (!id) return;
  const real = g.stacks[id] ? g.stacks[id].at(-1) : id;
  log(g, `${nm(real)}として使う。`);
  yield* resolve(g, real);
}

const kingdom = [
  {
    id: 'chapel2', name: '礼拝所', types: ['action', 'duration'], cost: 3, main: '+1 アクション', desc: '手札を 3 枚まで脇に置く。次の手番の始めにそれを手札に戻し、そのあと手札を 1 枚廃棄してよい',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const ids = takeFromHand(p, yield* askHand(g, pi, '脇に置く札（3 枚まで）', 0, 3));
      (p.mats.chapel2 = p.mats.chapel2 || []).push(...ids);
      later(g, 'chapel2', function* () {
        for (const id of ids) { const k = p.mats.chapel2.indexOf(id); if (k >= 0) p.hand.push(...p.mats.chapel2.splice(k, 1)); }
        const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1);
        if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
      });
    },
  },
  {
    id: 'darkmarket', name: '闇の市', cost: 3, main: '+2 金', desc: '闇の市の山の上 3 枚をめくり、1 枚をすぐ買ってよい（お金を払う）。残りは山の下へ。闇の市の山は、サプライにない王国カード 1 枚ずつで作る',
    *play(g, p, pi) {
      g.turn.money += 2;
      const bm = g.blackMarket || [];
      const shown = bm.splice(-3);
      if (!shown.length) return;
      const ok = shown.filter((id) => costOf(g, id) <= g.turn.money && !CARDS[id].potion && !CARDS[id].debt);
      const [i] = yield* askCards(g, pi, '買う札（なしでもよい）', ok, 0, 1);
      if (i != null) {
        const id = ok[i];
        shown.splice(shown.indexOf(id), 1);
        g.turn.money -= costOf(g, id);
        log(g, `${p.name}が闇の市で${nm(id)}を買った。`);
        yield* receive(g, pi, id);
      }
      bm.unshift(...shown);
    },
  },
  {
    id: 'dismantle', name: '解体', cost: 4, main: '廃棄して\n安い札と金', desc: '手札を 1 枚廃棄する。コストが 1 以上なら、それより安い札 1 枚と金 1 枚を獲得する',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id);
      if (c < 1) return;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下を獲得`, c - 1));
      yield* gain(g, pi, 'gold');
    },
  },
  {
    id: 'legate', name: '密使', cost: 4, main: '5 枚めくって\n4 枚手札に', desc: '山札の上 5 枚をめくる。左の人が 1 枚選んで捨て、残りを手札に入れる',
    *play(g, p, pi) {
      const shown = reveal(p, 5);
      if (!shown.length) return;
      const li = (pi + 1) % g.players.length;
      const [i] = yield* askCards(g, li, `${p.name}のめくった札から捨てさせる 1 枚`, shown, 1, 1);
      yield* discardCards(g, p, shown.splice(i ?? 0, 1));
      p.hand.push(...shown);
    },
  },
  {
    id: 'fencedvillage', name: '囲いの村', cost: 4, main: '+1 カード\n+2 アクション', desc: '片付けの始めに、場のアクションがこれを含めて 2 枚以下なら、これを山札の上に置いてよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onCleanup(g, p, pi) {
      if (g.playArea.filter((id) => is(id, 'action')).length > 2 || !g.playArea.includes('fencedvillage')) return;
      if (yield* askYesNo(g, pi, '「囲いの村」を山札の上に戻しますか？', '戻す', 'しない', ['fencedvillage'])) putOnDeck(p, g.playArea.splice(g.playArea.indexOf('fencedvillage'), 1)[0]);
    },
  },
  {
    id: 'bugyo', name: '奉行', cost: 5, main: '+1 アクション\nみんなに配る', desc: '1 つ選ぶ（かっこ内はあなた）: 全員 +1（+3）カード / 全員が銀（金）を獲得 / 全員が手札を 1 枚廃棄してよく、そうしたらちょうどコスト +1（+2）を獲得',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'c', label: '全員 +1 カード（自分 +3）' }, { value: 's', label: '全員 銀（自分 金）' }, { value: 't', label: '全員 格上げ（自分 +2）' }]);
      const n = g.players.length;
      for (let k = 0; k < n; k++) {
        const ti = (pi + k) % n;
        const t = g.players[ti];
        const me = k === 0;
        if (v === 'c') drawCards(t, me ? 3 : 1);
        else if (v === 's') yield* gain(g, ti, me ? 'gold' : 'silver');
        else {
          const [i] = yield* askHand(g, ti, '奉行: 廃棄して格上げする札（しなくてもよい）', 0, 1);
          if (i == null) continue;
          const [id] = takeFromHand(t, [i]);
          yield* trashCards(g, t, [id]);
          const c = costOf(g, id) + (me ? 2 : 1);
          yield* gain(g, ti, yield* askSupply(g, ti, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c));
        }
      }
    },
  },
  {
    id: 'borderland', name: '境の地', types: ['victory'], cost: 5, main: '勝利点 3 枚ごとに\n1 点', desc: '持っている勝利点カード 3 枚ごとに 1 点。獲得したとき +1 購入し、好きな枚数捨てて 1 枚につき +1 金',
    pointsFn: (all) => Math.floor(all.filter((id) => is(id, 'victory')).length / 3),
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      g.turn.buys += 1;
      const p = g.players[got.pi];
      const idx = yield* askHand(g, got.pi, '捨てる札（1 枚につき +1 金）', 0, p.hand.length);
      yield* discardCards(g, p, takeFromHand(p, idx));
      g.turn.money += idx.length;
    },
  },
  { id: 'nestegg', name: '隠し財布', types: ['treasure'], cost: 5, value: 2, main: '+2 金', desc: '山札を混ぜたとき、好きな位置に入れてよい（一番上に置く）' },
  {
    id: 'skipper', name: '船頭', types: ['action', 'duration', 'command'], cost: 6, main: 'サプライの札を使う\n（次の手番も）', desc: '今と次の手番の始めに: サプライの、コスト 4 以下の持続・命令でないアクションを 1 つ使う（札はサプライに残る）',
    *play(g, p, pi) {
      yield* playFromSupply(g, pi, 4);
      later(g, 'skipper', function* () { yield* playFromSupply(g, pi, 4); });
    },
  },
  {
    id: 'youngload', name: '若殿', types: ['action', 'duration', 'command'], cost: 8, main: '毎手番\nアクションを使う', desc: 'これと、手札のコスト 4 以下のアクションを 1 枚脇に置いてよい。以後、毎手番の始めにそのアクションを使い、捨てるときにまた脇に置く',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '脇に置くコスト 4 以下のアクション（なしでもよい）', 0, 1, (id) => is(id, 'action') && costOf(g, id) <= 4);
      if (i == null) return;
      const at = g.playArea.lastIndexOf('youngload');
      if (at >= 0) (p.mats.youngload = p.mats.youngload || []).push(...g.playArea.splice(at, 1));
      const [id] = takeFromHand(p, [i]);
      (p.mats.princed = p.mats.princed || []).push(id);
      const job = function* () {
        const k = p.mats.princed.indexOf(id);
        if (k < 0) return;
        p.mats.princed.splice(k, 1);
        g.playArea.push(id);
        log(g, `若殿が${nm(id)}を使う。`);
        yield* resolve(g, id);
        (g.turn.princeBack = g.turn.princeBack || []).push({ id, job });
      };
      p.nextTurn.push(job);
    },
  },
];

// サウナ／氷の湯（上下 2 種の山）
const saunaPile = { id: 'p_sauna', name: '蒸し風呂／氷の湯', cost: 4, main: '上下 2 種の山', desc: '上に蒸し風呂 5 枚、下に氷の湯 5 枚。一番上の札だけ買える' };
const saunaCards = [
  {
    id: 'steambath', pile: 'p_sauna', notSupply: true, name: '蒸し風呂', cost: 4, main: '+1 カード\n+1 アクション', desc: '手札の氷の湯を使ってよい。場にあるあいだ、銀を出すたびに手札を 1 枚廃棄してよい',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 1; yield* playFromHand(g, pi, (id) => id === 'icebath', '使う氷の湯（なしでもよい）'); },
  },
  {
    id: 'icebath', pile: 'p_sauna', notSupply: true, name: '氷の湯', cost: 5, main: '+3 カード', desc: '手札の蒸し風呂を使ってよい',
    *play(g, p, pi) { drawCards(p, 3); yield* playFromHand(g, pi, (id) => id === 'steambath', '使う蒸し風呂（なしでもよい）'); },
  },
];

const events = [
  {
    id: 'e_summon', name: '呼び寄せ', types: ['event'], cost: 5, main: 'アクションを\n次の手番に使う', desc: 'コスト 4 以下のアクションを獲得して脇に置く。次の手番の始めにそれを使う',
    *buy(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下のアクションを獲得', 4, (x) => is(x, 'action'));
      if (!(yield* gain(g, pi, id))) return;
      const real = p.discard.at(-1);
      if (real == null || pileOf(real) !== pileOf(id)) return;
      p.discard.pop();
      (p.mats.summon = p.mats.summon || []).push(real);
      p.nextTurn.push(function* (gg, pp, ppi) {
        const k = pp.mats.summon.indexOf(real);
        if (k < 0) return;
        pp.mats.summon.splice(k, 1);
        gg.playArea.push(real);
        yield* resolve(gg, real, ppi);
      });
    },
  },
];

// ---- 決まり ----
HOOKS.setup.push((g) => {
  if (g.kingdom.includes('p_sauna')) { g.stacks.p_sauna = [...Array(5).fill('icebath'), ...Array(5).fill('steambath')]; g.supply.p_sauna = 10; }
  if (g.kingdom.includes('darkmarket')) g.blackMarket = shuffle(kingdomPool().filter((id) => !(id in g.supply) && !['knights', 'castles'].includes(id) && !id.startsWith('p_') && CARDS[id].cost <= 8)).slice(0, 15);
});
// 蒸し風呂: 場にあるあいだ、銀を出すたびに手札を 1 枚廃棄してよい
HOOKS.treasure.push(function* (g, id) {
  if (id !== 'silver') return;
  const p = currentPlayer(g);
  for (let k = g.playArea.filter((x) => x === 'steambath').length; k > 0 && p.hand.length; k--) {
    const [i] = yield* askHand(g, g.current, '蒸し風呂: 廃棄する 1 枚（しなくてもよい）', 0, 1);
    if (i == null) break;
    yield* trashCards(g, p, takeFromHand(p, [i]));
  }
});
// 若殿: 使った札を捨てるとき、また脇に置く
HOOKS.endTurn.push(function* (g) {
  const p = currentPlayer(g);
  for (const { id, job } of g.turn.princeBack || []) {
    const at = g.playArea.indexOf(id);
    if (at < 0 || g.turn.stay.includes(id)) continue;
    p.mats.princed.push(...g.playArea.splice(at, 1));
    p.nextTurn.push(job);
  }
});

defineCards({ id: 'promo', name: 'プロモ' }, [...kingdom, saunaPile, ...saunaCards, ...events], [
  { id: 'promomix', name: 'プロモ詰め合わせ（基本と混ぜる）', cards: ['chapel2', 'darkmarket', 'dismantle', 'legate', 'fencedvillage', 'bugyo', 'borderland', 'nestegg', 'p_sauna', 'village'], landscapes: ['e_summon'] },
]);
