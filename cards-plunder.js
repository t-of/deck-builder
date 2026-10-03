'use strict';
// 拡張「略奪」のカード（王国 40 種）、戦利品 15 種、イベント 15 種、特性 15 種。名前は本家と別の言い回し。
// 戦利品: サプライ外の重なった山（game.nonSupply.loot / game.stacks.loot）。
// 「次に〜したとき」の持続: hold() で場に残し、player.watch の条件で効果を出して entry.done にする。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, treasureEffect, later, laterFor, hold, returnCard, returnToPile, currentPlayer,
  receive, shuffle, emptyPiles, pileOf, allCards, supplyOptions, takeFromSupply,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const T = ['treasure'];
const TD = ['treasure', 'duration'];
const AD = ['action', 'duration'];
const watchOf = (p) => (p.watch = p.watch || []);
// 次に when が起きたとき fn を行う（1 回きり）。entry があれば、効果のあと場から捨てられる
function watch(g, pi, when, fn, entry) { watchOf(g.players[pi]).push({ when, fn, entry }); }
function* fire(g, pi, when, ctx) {
  const p = g.players[pi];
  const ws = watchOf(p).filter((w) => w.when === when);
  for (const w of ws) {
    if (w.test && !w.test(ctx)) continue;
    p.watch.splice(p.watch.indexOf(w), 1);
    if (w.entry) w.entry.done = true;
    yield* w.fn(ctx);
  }
}
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
function* playNow(g, pi, id) {
  g.playArea.push(id);
  log(g, `${g.players[pi].name}が${nm(id)}を使用。`);
  if (is(id, 'action') && (!is(id, 'treasure') || g.turn.phase === 'action')) yield* resolve(g, id); else yield* treasureEffect(g, id);
}
const loot = (g, pi, to) => gain(g, pi, 'loot', to);
// 手番の終わりに手札に戻す札（檻・パズル箱・ペテン師など）
const toHandLater = (p, ids) => (p.mats.laterhand = p.mats.laterhand || []).push(...ids);

// ---- 戦利品（各 2 枚、混ぜた山） ----
const LT = ['treasure', 'loot'];
const lootCards = [
  { id: 'l_amphora', name: 'アンフォラ', types: [...LT, 'duration'], cost: 7, main: '今か次の手番に\n+1 購入 +3 金', desc: '',
    *play(g, p, pi) { const fx = function* () { g.turn.buys += 1; g.turn.money += 3; }; if (yield* askYesNo(g, pi, 'いつ受けますか？', '今', '次の手番の始め')) yield* fx(); else later(g, 'l_amphora', fx); } },
  { id: 'l_doubloons', name: 'ダブロン金貨', types: LT, cost: 7, value: 3, autoPlay: true, main: '+3 金', desc: '獲得したとき、金貨を獲得する', *onGain(g, got) { yield* gain(g, got.pi, 'gold'); } },
  { id: 'l_chalice', name: '尽きぬ杯', types: [...LT, 'duration'], cost: 7, value: 1, autoPlay: true, main: '+1 金　+1 購入\nずっと毎手番', desc: '今と、このあとの毎手番の始めに +1 金 +1 購入（場に残り続ける）',
    *play(g) { g.turn.buys += 1; const job = function* () { g.turn.money += 1; g.turn.buys += 1; later(g, 'l_chalice', job); }; later(g, 'l_chalice', job); } },
  { id: 'l_figurehead', name: '船首像', types: [...LT, 'duration'], cost: 7, value: 3, autoPlay: true, main: '+3 金\n次の手番 +2 カード', desc: '', *play(g, p) { later(g, 'l_figurehead', function* () { drawCards(p, 2); }); } },
  { id: 'l_hammer', name: 'ハンマー', types: LT, cost: 7, value: 3, main: '+3 金\nコスト 4 以下を獲得', desc: '', *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4)); } },
  { id: 'l_insignia', name: '勲章', types: LT, cost: 7, value: 3, autoPlay: true, main: '+3 金', desc: 'この手番、獲得した札を山札の上に置いてよい', *play(g) { g.turn.topdeckGains = true; } },
  { id: 'l_jewels', name: '宝石', types: [...LT, 'duration'], cost: 7, value: 3, autoPlay: true, main: '+3 金　+1 購入', desc: '次の手番の始めに、これを山札の一番下に置く',
    *play(g, p) { g.turn.buys += 1; later(g, 'l_jewels', function* () { const at = g.playArea.indexOf('l_jewels'); if (at >= 0) p.deck.unshift(...g.playArea.splice(at, 1)); }); } },
  { id: 'l_orb', name: '宝珠', types: LT, cost: 7, main: '捨て札を使うか\n+1 購入 +3 金', desc: '捨て札を見て、アクションか財宝を 1 枚使うか、+1 購入 +3 金',
    *play(g, p, pi) {
      const opts = p.discard.filter((id) => is(id, 'action') || is(id, 'treasure'));
      const [i] = yield* askCards(g, pi, '使う札（なければ +1 購入 +3 金）', opts, 0, 1);
      if (i == null) { g.turn.buys += 1; g.turn.money += 3; return; }
      p.discard.splice(p.discard.lastIndexOf(opts[i]), 1);
      yield* playNow(g, pi, opts[i]);
    } },
  { id: 'l_goat', name: '賞品のヤギ', types: LT, cost: 7, value: 3, main: '+3 金　+1 購入', desc: '手札を 1 枚廃棄してよい',
    *play(g, p, pi) { g.turn.buys += 1; const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); } },
  { id: 'l_puzzlebox', name: 'パズルボックス', types: LT, cost: 7, value: 3, main: '+3 金　+1 購入', desc: '手札を 1 枚脇に置き、手番の終わりに手札に戻してよい',
    *play(g, p, pi) { g.turn.buys += 1; const [i] = yield* askHand(g, pi, '取っておく 1 枚（しなくてもよい）', 0, 1); if (i != null) toHandLater(p, takeFromHand(p, [i])); } },
  { id: 'l_sextant', name: '六分儀', types: LT, cost: 7, value: 3, main: '+3 金　+1 購入', desc: '山札の上 5 枚を見て、好きな枚数捨て、残りを好きな順に戻す',
    *play(g, p, pi) {
      g.turn.buys += 1;
      const seen = reveal(p, 5);
      const idx = yield* askCards(g, pi, '捨てる札（好きな枚数）', seen, 0, seen.length);
      yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)), true);
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    } },
  { id: 'l_shield', name: '盾', types: [...LT, 'reaction'], cost: 7, value: 3, autoPlay: true, blocksAttack: true, main: '+3 金　+1 購入', desc: '他の人がアタックを使ったとき、手札から見せて、その効果を受けない', *play(g) { g.turn.buys += 1; } },
  { id: 'l_scroll', name: '呪符の巻物', types: ['action', 'treasure', 'loot'], cost: 7, main: '廃棄して\n安い札を獲得', desc: 'これを廃棄し、これより安い札を獲得する。それがアクションか財宝なら使ってよい',
    *play(g, p, pi) {
      yield* trashSelf(g, p, 'l_scroll');
      const id = yield* askSupply(g, pi, 'コスト 6 以下を獲得', 6);
      const real = id && (g.stacks[id] ? g.stacks[id].at(-1) : id);
      if (!(yield* gain(g, pi, id))) return;
      const k = real ? p.discard.lastIndexOf(real) : -1; // 獲得した札（ほかの効果で動いていなければ捨て札にある）
      if (k >= 0 && (is(real, 'action') || is(real, 'treasure')) && (yield* askYesNo(g, pi, `${nm(real)}を使いますか？`, '使う', 'しない', [real]))) { p.discard.splice(k, 1); yield* playNow(g, pi, real); }
    } },
  { id: 'l_staff', name: '杖', types: LT, cost: 7, value: 3, main: '+3 金　+1 購入', desc: '手札のアクションを 1 枚使ってよい',
    *play(g, p, pi) { g.turn.buys += 1; const [i] = yield* askHand(g, pi, '使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action')); if (i != null) yield* playNow(g, pi, takeFromHand(p, [i])[0]); } },
  { id: 'l_sword', name: '剣', types: ['treasure', 'attack', 'loot'], cost: 7, value: 3, autoPlay: true, main: '+3 金　+1 購入', desc: '他の人は手札が 4 枚になるまで捨てる',
    *play(g) { g.turn.buys += 1; yield* attackOthers(g, (ti) => discardDownTo(g, ti, 4)); } },
].map((c) => ({ ...c, pile: 'loot', notSupply: true }));
const lootPile = { id: 'loot', name: '戦利品の山', types: ['treasure', 'loot'], cost: 7, notSupply: true, main: '戦利品', desc: '15 種の戦利品を 2 枚ずつ混ぜた山' };

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'birdcage', name: '檻', types: TD, cost: 2, main: '手札をしまう', desc: '手札を 4 枚まで脇に置く。次に勝利点カードを獲得したら、これを廃棄し、手番の終わりに脇の札を手札に入れる',
    *play(g, p, pi) {
      const ids = takeFromHand(p, yield* askHand(g, pi, '脇に置く札（4 枚まで）', 0, 4));
      (p.mats.birdcage = p.mats.birdcage || []).push(...ids);
      const e = hold(g, pi, 'birdcage');
      watch(g, pi, 'gainVictory', function* () {
        const at = g.playArea.lastIndexOf('birdcage');
        const k = p.inPlay.lastIndexOf('birdcage');
        if (at >= 0) yield* trashCards(g, p, g.playArea.splice(at, 1)); else if (k >= 0) yield* trashCards(g, p, p.inPlay.splice(k, 1));
        for (const id of ids) { const j = p.mats.birdcage.indexOf(id); if (j >= 0) toHandLater(p, p.mats.birdcage.splice(j, 1)); }
      }, e);
    },
  },
  {
    id: 'grotto', name: '岩屋', types: AD, cost: 2, main: '+1 アクション', desc: '手札を 4 枚まで脇に置く。次の手番の始めに、それを捨てて同じ枚数引く',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const ids = takeFromHand(p, yield* askHand(g, pi, '脇に置く札（4 枚まで）', 0, 4));
      (p.mats.grotto = p.mats.grotto || []).push(...ids);
      later(g, 'grotto', function* () {
        for (const id of ids) { const j = p.mats.grotto.indexOf(id); if (j >= 0) p.discard.push(...p.mats.grotto.splice(j, 1)); }
        drawCards(p, ids.length);
      });
    },
  },
  { id: 'jewelegg', name: '宝飾卵', types: T, cost: 2, value: 1, autoPlay: true, main: '+1 金　+1 購入', desc: '廃棄したとき、戦利品を獲得する', *play(g) { g.turn.buys += 1; }, *onTrash(g, p, pi) { yield* loot(g, pi); } },
  {
    id: 'search', name: '調査', types: AD, cost: 2, main: '+2 金', desc: '次にサプライの山が空になったとき、これを廃棄して戦利品を獲得する',
    *play(g, p, pi) {
      g.turn.money += 2;
      const e = hold(g, pi, 'search');
      watch(g, pi, 'pileEmpty', function* () {
        const at = g.playArea.lastIndexOf('search');
        const k = p.inPlay.lastIndexOf('search');
        if (at >= 0) yield* trashCards(g, p, g.playArea.splice(at, 1)); else if (k >= 0) yield* trashCards(g, p, p.inPlay.splice(k, 1));
        yield* loot(g, pi);
      }, e);
    },
  },
  {
    id: 'shaman', name: 'シャーマン', cost: 2, main: '+1 アクション\n+1 金', desc: '手札を 1 枚廃棄してよい。この札を使う対局では、手番の始めに廃棄置き場のコスト 6 以下を 1 枚獲得する',
    *play(g, p, pi) { g.turn.actions += 1; g.turn.money += 1; const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); },
  },
  // ---- コスト 3 ----
  {
    id: 'hiddenshrine', name: '秘境の社', types: AD, cost: 3, main: '+1 金', desc: '次に財宝を獲得したとき、手札を 2 枚まで廃棄する',
    *play(g, p, pi) {
      g.turn.money += 1;
      watch(g, pi, 'gainTreasure', function* () { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '隠れた神社: 廃棄する札（2 枚まで）', 0, 2))); }, hold(g, pi, 'hiddenshrine'));
    },
  },
  {
    id: 'lorelei', name: 'セイレーン', types: ['action', 'duration', 'attack'], cost: 3, main: '次の手番に\n8 枚まで引く', desc: '他の人は呪いを獲得する。獲得したとき、手札のアクションを廃棄しなければ、これを廃棄する',
    *play(g, p) {
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
      later(g, 'lorelei', function* () { drawCards(p, Math.max(0, 8 - p.hand.length)); });
    },
    *onGain(g, got) {
      const p = g.players[got.pi];
      const [i] = yield* askHand(g, got.pi, '廃棄するアクション（しなければセイレーンを廃棄）', 0, 1, (id) => is(id, 'action'));
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); else yield* relocate(g, got, 'trash');
    },
  },
  { id: 'stowaway', name: '密航者', types: ['action', 'duration', 'reaction'], cost: 3, main: '次の手番に\n+2 カード', desc: '誰かが持続カードを獲得したとき、手札から使ってよい',
    *play(g, p, pi) { laterFor(g, pi, 'stowaway', function* () { drawCards(p, 2); }); } },
  {
    id: 'taskmaster', name: '現場監督', types: AD, cost: 3, main: '+1 アクション\n+1 金', desc: 'この手番にちょうどコスト 5 の札を獲得したら、次の手番の始めにこの効果をくり返す',
    *play(g, p, pi) {
      const run = function* () {
        g.turn.actions += 1; g.turn.money += 1;
        g.turn.taskmasters = (g.turn.taskmasters || []);
        g.turn.taskmasters.push(run);
      };
      yield* run();
    },
  },
  // ---- コスト 4 ----
  { id: 'plenty', name: '豊穣', types: TD, cost: 4, main: '次にアクションを獲得したら\n+1 購入 +3 金', desc: '',
    *play(g, p, pi) { watch(g, pi, 'gainAction', function* () { if (g.current === pi) { g.turn.buys += 1; g.turn.money += 3; } }, hold(g, pi, 'plenty')); } },
  {
    id: 'cabinboy', name: 'キャビンボーイ', types: AD, cost: 4, main: '+1 カード\n+1 アクション', desc: '次の手番の始めに、+2 金か、これを廃棄して持続カードを獲得するかを選ぶ',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      later(g, 'cabinboy', function* () {
        if (yield* askYesNo(g, pi, 'キャビンボーイ: どちらにしますか？', '+2 金', '廃棄して持続を獲得')) { g.turn.money += 2; return; }
        if (yield* trashSelf(g, p, 'cabinboy')) yield* gain(g, pi, yield* askSupply(g, pi, '持続カードを獲得', 99, (id) => is(id, 'duration')));
      });
    },
  },
  { id: 'meltpot', name: '坩堝', types: T, cost: 4, main: '廃棄して\nコストだけ +金', desc: '手札を 1 枚廃棄し、そのコスト 1 につき +1 金',
    *play(g, p, pi) { const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)); if (id) { yield* trashCards(g, p, [id]); g.turn.money += costOf(g, id); } } },
  { id: 'flagship', name: '旗艦', types: ['action', 'duration', 'command'], cost: 4, main: '+2 金', desc: '次に命令でないアクションを使うとき、もう一度使う',
    *play(g, p, pi) { g.turn.money += 2; watch(g, pi, 'playAction', function* (id) { log(g, `旗艦で${nm(id)}をもう一度使う。`); yield* resolve(g, id); }, hold(g, pi, 'flagship')); } },
  { id: 'fortunehunter', name: '幸運の狩人', cost: 4, main: '+2 金', desc: '山札の上 3 枚を見て、財宝を 1 枚使ってよい。残りを好きな順に戻す',
    *play(g, p, pi) {
      g.turn.money += 2;
      const seen = reveal(p, 3);
      const tr = seen.filter((id) => is(id, 'treasure'));
      const [i] = yield* askCards(g, pi, '使う財宝（なしでもよい）', tr, 0, 1);
      if (i != null) { seen.splice(seen.indexOf(tr[i]), 1); yield* playNow(g, pi, tr[i]); }
      yield* putBackInOrder(g, pi, seen);
    } },
  { id: 'gondola', name: 'ゴンドラ', types: TD, cost: 4, main: '今か次の手番に\n+2 金', desc: '獲得したとき、手札のアクションを 1 枚使ってよい',
    *play(g, p, pi) { if (yield* askYesNo(g, pi, 'いつ受けますか？', '今', '次の手番の始め')) g.turn.money += 2; else later(g, 'gondola', function* () { g.turn.money += 2; }); },
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      const p = g.players[got.pi];
      const [i] = yield* askHand(g, got.pi, '使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i != null) yield* playNow(g, got.pi, takeFromHand(p, [i])[0]);
    } },
  { id: 'harborvillage', name: '港村', cost: 4, main: '+1 カード\n+2 アクション', desc: 'この手番、次に使ったアクションで +金 を得たら、さらに +1 金',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; g.turn.harborv = (g.turn.harborv || 0) + 1; } },
  { id: 'landingparty', name: '上陸部隊', types: AD, cost: 4, main: '+2 カード\n+2 アクション', desc: '次に手番の最初に使った札が財宝なら、そのあとこれを山札の上に置く',
    *play(g, p, pi) { drawCards(p, 2); g.turn.actions += 2; watch(g, pi, 'firstTreasure', function* () { const at = g.playArea.lastIndexOf('landingparty'); if (at >= 0) putOnDeck(p, g.playArea.splice(at, 1)[0]); }, hold(g, pi, 'landingparty')); } },
  { id: 'chartmaker', name: '地図作り', types: ['action', 'reaction'], cost: 4, main: '4 枚見て 2 枚手札に', desc: '山札の上 4 枚を見て、2 枚を手札に、残りを捨てる。誰かが勝利点を獲得したとき、手札から使ってよい',
    *play(g, p, pi) {
      const seen = reveal(p, 4);
      const idx = yield* askCards(g, pi, '手札に入れる 2 枚', seen, 2, 2);
      p.hand.push(...seen.filter((_, i) => idx.includes(i)));
      yield* discardCards(g, p, seen.filter((_, i) => !idx.includes(i)), true);
    } },
  { id: 'maroon', name: '置き去り', cost: 4, main: '廃棄して\n種類 1 つにつき +2', desc: '手札を 1 枚廃棄し、その種類 1 つにつき +2 カード',
    *play(g, p, pi) { const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)); if (id) { yield* trashCards(g, p, [id]); drawCards(p, 2 * CARDS[id].types.length); } } },
  { id: 'rope', name: 'ロープ', types: TD, cost: 4, value: 1, main: '+1 金　+1 購入', desc: '次の手番の始めに +1 カードし、手札を 1 枚廃棄してよい',
    *play(g, p, pi) { g.turn.buys += 1; later(g, 'rope', function* () { drawCards(p, 1); const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); }); } },
  { id: 'swampshacks', name: '沼地の小屋', cost: 4, main: '+2 アクション', desc: '場の札 3 枚ごとに +1 カード', *play(g, p) { g.turn.actions += 2; drawCards(p, Math.floor(g.playArea.length / 3)); } },
  { id: 'toolbox', name: '工具', types: T, cost: 4, main: '場の札を写す', desc: '誰かの場にある札と同じ札を 1 枚獲得する',
    *play(g, p, pi) {
      const names = [...new Set([...g.playArea, ...g.players.flatMap((q) => q.inPlay)])].filter((id) => g.supply[id] > 0 || g.supply[pileOf(id)] > 0);
      const [i] = yield* askCards(g, pi, '獲得する札', names, 1, 1);
      if (i != null) yield* gain(g, pi, g.supply[names[i]] > 0 ? names[i] : pileOf(names[i]));
    } },
  // ---- コスト 5 ----
  { id: 'buriedgold', name: '埋められた財宝', types: TD, cost: 5, main: '次の手番に\n+1 購入 +3 金', desc: '獲得したとき、それを使う',
    *play(g) { later(g, 'buriedgold', function* () { g.turn.buys += 1; g.turn.money += 3; }); },
    *onGain(g, got) { if (got.pi === g.current && (yield* relocate(g, got, 'gone'))) yield* playNow(g, got.pi, 'buriedgold'); } },
  { id: 'crew', name: '乗組員', types: AD, cost: 5, main: '+3 カード', desc: '次の手番の始めに、これを山札の上に置く',
    *play(g, p) { drawCards(p, 3); later(g, 'crew', function* () { const at = g.playArea.indexOf('crew'); if (at >= 0) putOnDeck(p, g.playArea.splice(at, 1)[0]); }); } },
  { id: 'slasher', name: '切り裂き魔', types: ['action', 'duration', 'attack'], cost: 5, main: '手札を 3 枚に', desc: '他の人は手札が 3 枚になるまで捨てる。次に誰かがコスト 5 以上の財宝を獲得したとき、戦利品を獲得する',
    *play(g, p, pi) {
      yield* attackOthers(g, (ti) => discardDownTo(g, ti, 3));
      const e = hold(g, pi, 'slasher');
      (g.slashers = g.slashers || []).push({ pi, e });
    } },
  { id: 'enlarge', name: '拡大', types: AD, cost: 5, main: '格上げ\n（次の手番も）', desc: '今と次の手番の始めに: 手札を 1 枚廃棄し、そのコスト +2 以下を獲得する',
    *play(g, p, pi) {
      const once = function* () { const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)); if (!id) return; yield* trashCards(g, p, [id]); const max = costOf(g, id) + 2; yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得`, max)); };
      yield* once();
      later(g, 'enlarge', once);
    } },
  { id: 'statuette', name: '小像', types: T, cost: 5, main: '+2 カード', desc: 'アクションを 1 枚捨ててよい。そうしたら +1 購入 +1 金',
    *play(g, p, pi) { drawCards(p, 2); const [i] = yield* askHand(g, pi, '捨てるアクション（しなくてもよい）', 0, 1, (id) => is(id, 'action')); if (i != null) { yield* discardCards(g, p, takeFromHand(p, [i])); g.turn.buys += 1; g.turn.money += 1; } } },
  { id: 'firstmate', name: '一等航海士', cost: 5, main: '同じ名前のアクションを\n好きなだけ使う', desc: 'そのあと、手札が 6 枚になるまで引く',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '使うアクション（同じ名前を続けて使う・なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i != null) {
        const id = p.hand[i];
        while (p.hand.includes(id) && (yield* askYesNo(g, pi, `${nm(id)}を使いますか？`, '使う', 'やめる', [id]))) yield* playNow(g, pi, takeFromHand(p, [p.hand.indexOf(id)])[0]);
      }
      drawCards(p, Math.max(0, 6 - p.hand.length));
    } },
  { id: 'frigate', name: 'フリゲート艦', types: ['action', 'duration', 'attack'], cost: 5, main: '+3 金', desc: '次の手番の始めまで、他の人はアクションを使うたびに、手札が 4 枚になるまで捨てる',
    *play(g) {
      g.turn.money += 3;
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.frigate = (g.players[ti].tokens.frigate || 0) + 1; });
      later(g, 'frigate', function* () { for (const ti of hit) g.players[ti].tokens.frigate -= 1; });
    } },
  { id: 'miningroad', name: '採掘路', cost: 5, main: '+1 アクション　+1 購入\n+2 金', desc: 'この手番に 1 度、財宝を獲得したとき、それを使ってよい', *play(g) { g.turn.actions += 1; g.turn.buys += 1; g.turn.money += 2; g.turn.miningroad = (g.turn.miningroad || 0) + 1; } },
  { id: 'pendant', name: 'ペンダント', types: T, cost: 5, autoPlay: true, main: '場の財宝の種類\nだけ +金', desc: '場のちがう名前の財宝 1 種につき +1 金', *play(g) { g.turn.money += new Set(g.playArea.filter((id) => is(id, 'treasure'))).size; } },
  { id: 'pickaxe', name: 'つるはし', types: T, cost: 5, value: 1, main: '+1 金', desc: '手札を 1 枚廃棄する。コスト 3 以上なら戦利品を手札に獲得する',
    *play(g, p, pi) { const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)); if (!id) return; yield* trashCards(g, p, [id]); if (costOf(g, id) >= 3) yield* loot(g, pi, 'hand'); } },
  { id: 'pilgrim', name: '巡礼者', cost: 5, main: '+4 カード', desc: '手札を 1 枚山札の上に置く', *play(g, p, pi) { drawCards(p, 4); const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚', 1, 1); if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]); } },
  { id: 'purser', name: '操舵手', types: AD, cost: 5, main: 'ずっと毎手番\n獲得か手札へ', desc: 'このあとの毎手番の始めに、コスト 4 以下を獲得してこの上に置くか、この上の札を 1 枚手札に入れるか（場に残り続ける）',
    *play(g, p, pi) {
      const mine = (p.mats.purser = p.mats.purser || []);
      const job = function* () {
        const take = mine.length && (yield* askYesNo(g, pi, '需品係: どちらにしますか？', '上の札を手札へ', 'コスト 4 以下を獲得して置く'));
        if (take) { const [i] = yield* askCards(g, pi, '手札に入れる札', mine, 1, 1); p.hand.push(...mine.splice(i ?? 0, 1)); }
        else { const id = yield* askSupply(g, pi, 'コスト 4 以下を獲得（需品係の上へ）', 4); const c = id && takeFromSupply(g, id); if (c) { g.turn.gained.push(c); mine.push(c); } }
        later(g, 'purser', job);
      };
      later(g, 'purser', job);
    } },
  { id: 'silvermine', name: '銀貨鉱山', types: T, cost: 5, main: '安い財宝を手札に', desc: 'これより安い財宝を手札に獲得する',
    *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下の財宝を手札に獲得', costOf(g, 'silvermine') - 1, (id) => is(id, 'treasure')), 'hand'); } },
  { id: 'longship', name: 'ロングシップ', types: AD, cost: 5, main: '+2 アクション\n次の手番 +2 カード', desc: '', *play(g, p) { g.turn.actions += 2; later(g, 'longship', function* () { drawCards(p, 2); }); } },
  { id: 'trickster', name: 'ペテン師', types: ['action', 'attack'], cost: 5, main: '呪いを配る', desc: '他の人は呪いを獲得する。この手番に 1 度、場から財宝を捨てるとき、それを脇に置いて手番の終わりに手札に入れてよい',
    *play(g) { yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); }); g.turn.trickster = (g.turn.trickster || 0) + 1; } },
  { id: 'wealthyvillage', name: '裕福な村', cost: 5, main: '+1 カード\n+2 アクション', desc: '獲得したとき、場に 3 種類以上の財宝があれば戦利品を獲得する',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onGain(g, got) { if (got.pi === g.current && new Set(g.playArea.filter((id) => is(id, 'treasure'))).size >= 3) yield* loot(g, got.pi); } },
  // ---- コスト 6〜7 ----
  { id: 'lootsack', name: '戦利品の袋', types: T, cost: 6, value: 1, main: '+1 金　+1 購入\n戦利品を獲得', desc: '', *play(g, p, pi) { g.turn.buys += 1; yield* loot(g, pi); } },
  { id: 'kingscache', name: '王の蓄え', types: T, cost: 7, main: '財宝を 3 回', desc: '手札の財宝を 1 枚、3 回使ってよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '3 回使う財宝（なしでもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      for (let k = 0; k < 3; k++) yield* treasureEffect(g, id);
    } },
];

// ---- イベント ----
const E = ['event'];
const events = [
  { id: 'pe_bury', name: '埋葬', types: E, cost: 1, main: '+1 購入', desc: '捨て札の札を 1 枚、山札の一番下に置く',
    *buy(g, p, pi) { g.turn.buys += 1; const [i] = yield* askCards(g, pi, '山札の下に置く 1 枚', [...p.discard], 1, 1); if (i != null) p.deck.unshift(p.discard.splice(i, 1)[0]); } },
  { id: 'pe_avoid', name: '回避', types: E, cost: 2, main: '+1 購入', desc: 'この手番、次に山札を混ぜるとき、3 枚までを捨て札に残す（要らない札を自動で選ぶ）', *buy(g, p) { g.turn.buys += 1; p.tokens.avoid = (p.tokens.avoid || 0) + 3; } },
  { id: 'pe_deliver', name: '配達', types: E, cost: 2, main: '+1 購入', desc: 'この手番、獲得した札を脇に置き、手番の終わりに手札に入れる', *buy(g) { g.turn.buys += 1; g.turn.deliver = true; } },
  { id: 'pe_peril', name: '危難', types: E, cost: 2, main: 'アクションを\n戦利品に', desc: '手札のアクションを 1 枚廃棄してよい。そうしたら戦利品を獲得する',
    *buy(g, p, pi) { const [i] = yield* askHand(g, pi, '廃棄するアクション（しなくてもよい）', 0, 1, (id) => is(id, 'action')); if (i != null) { yield* trashCards(g, p, takeFromHand(p, [i])); yield* loot(g, pi); } } },
  { id: 'pe_rush', name: '突貫', types: E, cost: 2, main: '+1 購入', desc: 'この手番、次にアクションを獲得したとき、それを使う', *buy(g) { g.turn.buys += 1; g.turn.rush = (g.turn.rush || 0) + 1; } },
  { id: 'pe_foray', name: '襲撃', types: E, cost: 3, main: '3 枚捨てて戦利品', desc: '手札を 3 枚見せて捨てる。3 枚ともちがう名前なら戦利品を獲得する',
    *buy(g, p, pi) { const ids = takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚', 3, 3)); yield* discardCards(g, p, ids); if (ids.length === 3 && new Set(ids).size === 3) yield* loot(g, pi); } },
  { id: 'pe_launch', name: '発進', types: E, cost: 3, once: true, main: 'アクションフェイズに戻る', desc: '1 手番に 1 度: アクションフェイズに戻り、+1 カード +1 アクション +1 購入',
    *buy(g, p) { g.turn.phase = 'action'; drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; } },
  { id: 'pe_mirror', name: '鏡映', types: E, cost: 3, main: '+1 購入', desc: 'この手番、次にアクションを獲得したとき、同じ札をもう 1 枚獲得する', *buy(g) { g.turn.buys += 1; g.turn.mirror = (g.turn.mirror || 0) + 1; } },
  { id: 'pe_prepare', name: '準備', types: E, cost: 3, main: '手札を次の手番に', desc: '手札を脇に置く。次の手番の始めに、その中のアクションと財宝を使い、残りを捨てる',
    *buy(g, p, pi) {
      const ids = p.hand.splice(0);
      (p.mats.prepare = p.mats.prepare || []).push(...ids);
      p.nextTurn.push(function* (gg, pp, ppi) {
        for (const id of ids) {
          const k = pp.mats.prepare.indexOf(id);
          if (k < 0) continue;
          pp.mats.prepare.splice(k, 1);
          if (is(id, 'action') || is(id, 'treasure')) yield* playNow(gg, ppi, id); else pp.discard.push(id);
        }
      });
    } },
  { id: 'pe_scrounge', name: '物色', types: E, cost: 3, main: '廃棄か拾う', desc: '手札を 1 枚廃棄するか、廃棄置き場の屋敷を獲得して、そうしたらコスト 5 以下を獲得する',
    *buy(g, p, pi) {
      if (!g.trash.includes('estate') || (yield* askYesNo(g, pi, 'どちらにしますか？', '手札を 1 枚廃棄', '廃棄置き場の屋敷を拾う'))) { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1))); return; }
      g.trash.splice(g.trash.indexOf('estate'), 1);
      yield* receive(g, pi, 'estate');
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を獲得', 5));
    } },
  { id: 'pe_journey', name: '旅行', types: E, cost: 4, once: true, main: '場を残して\n追加の手番', desc: '1 手番に 1 度: 前の手番が自分でなければ、この手番の片付けで場の札を捨てずに、追加の手番を行う',
    *buy(g) { if (!g.extraTurn) { g.turn.seize = true; g.turn.keepPlay = true; } } },
  { id: 'pe_maelstrom', name: '大渦巻', types: E, cost: 4, main: '3 枚廃棄', desc: '手札を 3 枚廃棄する。手札が 5 枚以上の他の人は 1 枚廃棄する',
    *buy(g, p, pi) {
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 3 枚', 3, 3)));
      yield* eachOther(g, function* (ti) { const t = g.players[ti]; if (t.hand.length >= 5) yield* trashCards(g, t, takeFromHand(t, yield* askHand(g, ti, '廃棄する 1 枚', 1, 1))); });
    } },
  { id: 'pe_looting', name: '略奪行為', types: E, cost: 6, main: '戦利品を獲得', desc: '', *buy(g, p, pi) { yield* loot(g, pi); } },
  { id: 'pe_invasion', name: '侵略', types: E, cost: 10, main: 'アタック・公領\nアクション・戦利品', desc: '手札のアタックを使ってよい。公領を獲得、アクションを山札の上に獲得、戦利品を獲得して使う',
    *buy(g, p, pi) {
      const [i] = yield* askHand(g, pi, '使うアタック（なしでもよい）', 0, 1, (id) => is(id, 'attack'));
      if (i != null) yield* playNow(g, pi, takeFromHand(p, [i])[0]);
      yield* gain(g, pi, 'duchy');
      yield* gain(g, pi, yield* askSupply(g, pi, 'アクションを山札の上に獲得', 99, (id) => is(id, 'action')), 'deck');
      const top = g.stacks.loot && g.stacks.loot.at(-1);
      if ((yield* loot(g, pi)) && top) { const k = p.discard.lastIndexOf(top); if (k >= 0) { p.discard.splice(k, 1); yield* playNow(g, pi, top); } }
    } },
  { id: 'pe_prosper', name: '繁栄', types: E, cost: 10, main: '戦利品と\n財宝を種類ごとに', desc: '戦利品を獲得し、ちがう名前の財宝を好きなだけ 1 枚ずつ獲得する',
    *buy(g, p, pi) {
      yield* loot(g, pi);
      const opts = Object.keys(g.supply).filter((id) => is(id, 'treasure') && g.supply[id] > 0);
      const idx = yield* askCards(g, pi, '獲得する財宝（好きなだけ・1 種 1 枚）', opts, 0, opts.length);
      for (const i of idx) yield* gain(g, pi, opts[i]);
    } },
];

// ---- 特性（対局の始めに、アクションか財宝の山 1 つにつく） ----
const TR = ['trait'];
const trait = (id, name, main, desc) => ({ id, name, types: TR, cost: 0, main, desc });
const traits = [
  trait('t_cheap', '安価な', 'コスト -1', 'この山の札はコストが 1 下がる'),
  trait('t_cursed', '呪われた', '戦利品と呪い', 'この山の札を獲得したとき、戦利品と呪いを獲得する'),
  trait('t_fawning', 'へつらう', '属州で獲得', '属州を獲得したとき、この山の札を獲得する'),
  trait('t_fated', '運命の', '混ぜると一番上', '山札を混ぜたとき、この山の札を山札の一番上に置く（ponytail: 一番上か一番下かを選べず、上に置く）'),
  trait('t_friendly', '友好的な', '捨てて獲得', '片付けの始めに、この山の札を 1 枚捨てて、同じ札を獲得してよい'),
  trait('t_hasty', 'せっかちな', '次の手番に使う', 'この山の札を獲得したとき、脇に置き、次の手番の始めに使う'),
  trait('t_inherited', '受け継がれた', '初めのデッキに', '対局の始めに、初めのデッキの屋敷 1 枚がこの山の札に替わる'),
  trait('t_inspiring', '鼓舞する', '使ったら\nもう 1 枚', '自分の手番にこの山の札を使ったあと、場にない手札のアクションを 1 枚使ってよい'),
  trait('t_nearby', '近隣の', '獲得で +1 購入', 'この山の札を獲得したとき +1 購入'),
  trait('t_patient', '忍耐強い', '次の手番に使う', '片付けの始めに、手札のこの山の札を脇に置き、次の手番の始めに使ってよい'),
  trait('t_pious', '敬虔な', '獲得で廃棄', 'この山の札を獲得したとき、手札を 1 枚廃棄してよい'),
  trait('t_reckless', '無謀な', '効果を 2 回', 'この山の札は効果を 2 回使う。場から捨てるとき、山に戻す'),
  trait('t_rich', '豊かな', '獲得で銀貨', 'この山の札を獲得したとき、銀貨を獲得する'),
  trait('t_shy', '内気な', '捨てて +2 カード', '手番の始めに、この山の札を 1 枚捨てて +2 カードにしてよい'),
  trait('t_tireless', '疲れ知らずの', '山札の上に戻る', '場から捨てるとき、脇に置き、手番の終わりに山札の上に置く'),
];
const hasTrait = (g, t, id) => g.traits[t] && pileOf(id) === g.traits[t];

// ---- 決まり ----
HOOKS.setup.push((g) => {
  const needsLoot = [...g.kingdom, ...g.landscapes].some((id) => ['jewelegg', 'search', 'slasher', 'pickaxe', 'lootsack', 'wealthyvillage', 'pe_peril', 'pe_foray', 'pe_looting', 'pe_invasion', 'pe_prosper', 't_cursed'].includes(id));
  if (needsLoot) { g.stacks.loot = shuffle(lootCards.flatMap((c) => [c.id, c.id])); g.nonSupply.loot = 30; }
  for (const t of g.landscapes.filter((id) => is(id, 'trait'))) {
    const piles = g.kingdom.filter((id) => (is(id, 'action') || is(id, 'treasure')) && !Object.values(g.traits).includes(id));
    if (piles.length) g.traits[t] = shuffle([...piles])[0];
  }
  if (g.traits.t_inherited) {
    for (const p of g.players) {
      const c = takeFromSupply(g, g.traits.t_inherited);
      if (!c) break;
      // 屋敷（なければ避難所、それもなければ銅貨）1 枚と入れ替える
      const pickOld = (arr) => ['estate', 'wildestate', 'shack', 'tombs', 'copper'].map((x) => arr.indexOf(x)).find((k) => k >= 0);
      const i = pickOld(p.deck);
      const j = pickOld(p.hand);
      const swap = (arr, k) => { const old = arr[k]; arr[k] = c; if (!returnCard(g, old)) g.trash.push(old); };
      if (i != null) swap(p.deck, i); else if (j != null) swap(p.hand, j); else if (!returnCard(g, c)) g.trash.push(c);
    }
  }
});
HOOKS.cost.push((g, id) => (g.traits && hasTrait(g, 't_cheap', id) ? 1 : 0));
// 山札を混ぜたとき: 運命の札は一番上へ。回避は要らない札（呪い・勝利点）を 3 枚まで捨て札に残す
HOOKS.shuffle.push((p, g) => {
  if (g && g.traits.t_fated) {
    const fated = p.deck.filter((id) => pileOf(id) === g.traits.t_fated);
    if (fated.length) p.deck = [...p.deck.filter((id) => pileOf(id) !== g.traits.t_fated), ...fated];
  }
  if (p.tokens.avoid > 0) {
    const junk = p.deck.map((id, i) => ({ id, i })).filter((x) => x.id === 'curse' || (is(x.id, 'victory') && !is(x.id, 'action') && !is(x.id, 'treasure'))).slice(0, p.tokens.avoid);
    for (const x of [...junk].reverse()) p.discard.push(...p.deck.splice(x.i, 1));
    p.tokens.avoid = 0;
  }
});
HOOKS.gain.push(function* (g, got) {
  const pi = got.pi;
  const p = g.players[pi];
  const mine = pi === g.current;
  if (is(got.id, 'action')) {
    yield* fire(g, pi, 'gainAction', got);
    if (mine && g.turn.mirror > 0) { g.turn.mirror -= 1; yield* gain(g, pi, got.id in g.supply ? got.id : pileOf(got.id)); }
    if (mine && g.turn.rush > 0 && got.to !== 'gone') { g.turn.rush -= 1; if (yield* relocate(g, got, 'gone')) yield* playNow(g, pi, got.id); }
  }
  if (is(got.id, 'treasure')) {
    yield* fire(g, pi, 'gainTreasure', got);
    if (mine && g.turn.miningroad > 0 && got.to !== 'gone' && (yield* askYesNo(g, pi, `採掘路: 獲得した${nm(got.id)}を使いますか？`, '使う', 'しない', [got.id]))) {
      g.turn.miningroad -= 1;
      if (yield* relocate(g, got, 'gone')) yield* playNow(g, pi, got.id);
    }
    if (costOf(g, got.id) >= 5 && g.slashers && g.slashers.length) {
      const s = g.slashers.shift();
      s.e.done = true;
      yield* loot(g, s.pi);
    }
  }
  if (is(got.id, 'victory')) {
    yield* fire(g, pi, 'gainVictory', got);
    for (let k = 0; k < g.players.length; k++) {
      const oi = (pi + k) % g.players.length;
      const o = g.players[oi];
      if (o.hand.includes('chartmaker') && (yield* askYesNo(g, oi, `勝利点が獲得された。「地図作り」を使いますか？`, '使う', '使わない', ['chartmaker']))) {
        o.hand.splice(o.hand.indexOf('chartmaker'), 1);
        yield* playOutOfTurn(g, oi, 'chartmaker');
      }
    }
  }
  if (is(got.id, 'duration')) {
    for (let k = 0; k < g.players.length; k++) {
      const oi = (pi + k) % g.players.length;
      const o = g.players[oi];
      if (o.hand.includes('stowaway') && (yield* askYesNo(g, oi, `持続カードが獲得された。「密航者」を使いますか？`, '使う', '使わない', ['stowaway']))) {
        o.hand.splice(o.hand.indexOf('stowaway'), 1);
        yield* playOutOfTurn(g, oi, 'stowaway');
      }
    }
  }
  if (mine && g.turn.taskmasters && costOf(g, got.id) === 5) {
    for (const run of g.turn.taskmasters.splice(0)) later(g, 'taskmaster', run);
  }
  // 山が空になった
  const pile = pileOf(got.id) in g.supply ? pileOf(got.id) : got.id;
  if (g.supply[pile] === 0) for (let k = 0; k < g.players.length; k++) yield* fire(g, k, 'pileEmpty', pile);
  // 特性
  if (hasTrait(g, 't_cursed', got.id)) { yield* loot(g, pi); yield* gain(g, pi, 'curse'); }
  if (hasTrait(g, 't_nearby', got.id) && mine) g.turn.buys += 1;
  if (hasTrait(g, 't_rich', got.id)) yield* gain(g, pi, 'silver');
  if (hasTrait(g, 't_pious', got.id)) { const [i] = yield* askHand(g, pi, '信心深い: 廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); }
  if (got.id === 'province' && g.traits.t_fawning) yield* gain(g, pi, g.traits.t_fawning);
  if (hasTrait(g, 't_hasty', got.id) && got.to !== 'gone' && (yield* relocate(g, got, 'gone'))) {
    const id = got.id;
    (p.mats.hasty = p.mats.hasty || []).push(id);
    p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.hasty.indexOf(id); if (k >= 0) { pp.mats.hasty.splice(k, 1); yield* playNow(gg, ppi, id); } });
  }
  // 配達: この手番に獲得した札は、手番の終わりに手札へ
  if (mine && g.turn.deliver && got.to !== 'gone' && got.to !== 'trash' && (yield* relocate(g, got, 'gone'))) toHandLater(p, [got.id]);
});
HOOKS.play.push(function* (g, id) {
  const p = currentPlayer(g);
  g.turn.firstPlayed = true; // 最初に使った札がアクションなら、上陸部隊は戻らない
  if (p.tokens.frigate > 0) g.turn.frigateAfter = true;
  if (!is(id, 'command')) yield* fire(g, g.current, 'playAction', id);
  const before = g.turn.money;
  g.turn.harborWatch = g.turn.harborv > 0 ? before : null;
});
HOOKS.afterAction.push(function* (g, id) {
  const p = currentPlayer(g);
  if (g.turn.harborWatch != null) { if (g.turn.money > g.turn.harborWatch) g.turn.money += 1; g.turn.harborv -= 1; g.turn.harborWatch = null; }
  if (g.turn.frigateAfter) { g.turn.frigateAfter = false; yield* discardDownTo(g, g.current, 4); }
  if (hasTrait(g, 't_inspiring', id)) {
    const [i] = yield* askHand(g, g.current, '鼓舞する: 場にないアクションを使ってよい', 0, 1, (x) => is(x, 'action') && !g.playArea.includes(x));
    if (i != null) yield* playNow(g, g.current, takeFromHand(p, [i])[0]);
  }
});
HOOKS.treasure.push(function* (g) {
  if (!g.turn.firstPlayed) { g.turn.firstPlayed = true; yield* fire(g, g.current, 'firstTreasure'); }
});
HOOKS.turnStart.push(function* (g, p, pi) {
  // シャーマンの対局: 手番の始めに廃棄置き場のコスト 6 以下を獲得
  if (g.kingdom.includes('shaman')) {
    const opts = [...new Set(g.trash.filter((id) => costOf(g, id) <= 6))];
    if (opts.length) {
      const [i] = yield* askCards(g, pi, 'シャーマン: 廃棄置き場から獲得する札', opts, 1, 1);
      const id = opts[i ?? 0];
      g.trash.splice(g.trash.lastIndexOf(id), 1);
      yield* receive(g, pi, id);
    }
  }
  if (g.traits.t_shy) {
    const [i] = yield* askHand(g, pi, '内気な: 捨てて +2 カード（しなくてもよい）', 0, 1, (id) => hasTrait(g, 't_shy', id));
    if (i != null) { yield* discardCards(g, p, takeFromHand(p, [i])); drawCards(p, 2); }
  }
});
HOOKS.endTurn.push(function* (g) {
  const p = currentPlayer(g);
  const pi = g.current;
  if (g.traits.t_friendly) {
    const [i] = yield* askHand(g, pi, '友好的な: 捨てて同じ札を獲得（しなくてもよい）', 0, 1, (id) => hasTrait(g, 't_friendly', id));
    if (i != null) { const [id] = takeFromHand(p, [i]); yield* discardCards(g, p, [id]); yield* gain(g, pi, g.traits.t_friendly); }
  }
  if (g.traits.t_patient) {
    const idx = yield* askHand(g, pi, '忍耐強い: 次の手番に使う札（好きな枚数）', 0, 99, (id) => hasTrait(g, 't_patient', id));
    for (const id of takeFromHand(p, idx)) {
      (p.mats.patient = p.mats.patient || []).push(id);
      p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.patient.indexOf(id); if (k >= 0) { pp.mats.patient.splice(k, 1); yield* playNow(gg, ppi, id); } });
    }
  }
  // ペテン師: 場から捨てる財宝を 1 枚取っておく
  for (let k = g.turn.trickster || 0; k > 0; k--) {
    const tr = g.playArea.filter((id) => is(id, 'treasure'));
    const [i] = yield* askCards(g, pi, 'ペテン師: 手番の終わりに手札へ戻す財宝（なしでもよい）', tr, 0, 1);
    if (i == null) break;
    toHandLater(p, [g.playArea.splice(g.playArea.indexOf(tr[i]), 1)[0]]);
  }
  // 無謀な札は山に戻る。たゆまぬ札は山札の上へ（引いたあと）
  for (const id of [...g.playArea]) {
    if (hasTrait(g, 't_reckless', id) && !g.turn.stay.includes(id)) { const [c] = g.playArea.splice(g.playArea.indexOf(id), 1); if (!returnCard(g, c)) p.discard.push(c); }
    else if (hasTrait(g, 't_tireless', id) && !g.turn.stay.includes(id)) (p.mats.tireless = p.mats.tireless || []).push(...g.playArea.splice(g.playArea.indexOf(id), 1));
  }
  // 船旅: 場の札を捨てない（そのまま追加の手番へ）
  if (g.turn.keepPlay) g.turn.stay.push(...g.playArea);
});
HOOKS.afterCleanup.push(function* (g, p) {
  if (p.mats.laterhand && p.mats.laterhand.length) p.hand.push(...p.mats.laterhand.splice(0));
  if (p.mats.tireless && p.mats.tireless.length) for (const id of p.mats.tireless.splice(0)) putOnDeck(p, id);
});

defineCards({ id: 'plunder', name: '略奪' }, [lootPile, ...lootCards, ...kingdom, ...events, ...traits], [
  { id: 'firstplunder', name: 'はじめての略奪', cards: ['grotto', 'shaman', 'hiddenshrine', 'plenty', 'fortunehunter', 'harborvillage', 'swampshacks', 'crew', 'longship', 'lootsack'], landscapes: ['pe_looting', 't_rich'] },
  { id: 'highseasplunder', name: '荒海', cards: ['birdcage', 'search', 'lorelei', 'stowaway', 'taskmaster', 'flagship', 'gondola', 'slasher', 'frigate', 'purser'], landscapes: ['pe_launch', 't_cheap'] },
  { id: 'treasurecove', name: '宝の入り江', cards: ['jewelegg', 'meltpot', 'rope', 'toolbox', 'buriedgold', 'statuette', 'pendant', 'pickaxe', 'silvermine', 'kingscache'], landscapes: ['pe_prosper', 't_nearby'] },
]);
