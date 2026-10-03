'use strict';
// 拡張「暗黒時代」のカード（35 種＋騎士 10 種、廃墟 5 種、避難所 3 種、サプライ外 3 種）。名前は公式日本語カード名（一部未確認）。
// 廃墟（ruins）と騎士（knights）は、ちがう札が重なった山（game.stacks）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, treasureEffect, allCards, shuffle, supplyOptions, receive,
  returnToPile, currentPlayer,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const A = ['action'];
const AA = ['action', 'attack'];
const LOOT = ['action', 'attack', 'looter'];

function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
function* fromTrash(g, pi, purpose, pred, to = 'discard') {
  const opts = [...new Set(g.trash.filter(pred))];
  if (!opts.length) return null;
  const [i] = yield* askCards(g, pi, purpose, opts, 1, 1);
  const id = opts[i ?? 0];
  g.trash.splice(g.trash.lastIndexOf(id), 1);
  log(g, `${g.players[pi].name}が廃棄置き場から${nm(id)}を獲得。`);
  yield* receive(g, pi, id, to);
  return id;
}
function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
// 山札の上 2 枚をめくり、コスト 3〜6 の 1 枚をその人が選んで廃棄、残りを捨てる。廃棄した札を返す
function* trashThreeToSix(g, ti) {
  const t = g.players[ti];
  const shown = reveal(t, 2);
  if (!shown.length) return null;
  log(g, `${t.name}がめくった: ${shown.map(nm).join('')}`);
  const idx = shown.map((id, i) => (costOf(g, id) >= 3 && costOf(g, id) <= 6 ? i : -1)).filter((i) => i >= 0);
  let hit = null;
  if (idx.length) {
    const pick = idx.length === 1 || shown[idx[0]] === shown[idx[1]] ? idx[0]
      : idx[(yield* askCards(g, ti, '廃棄する 1 枚を選ぶ（コスト 3〜6）', idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
    [hit] = shown.splice(pick, 1);
    yield* trashCards(g, t, [hit]);
  }
  yield* discardCards(g, t, shown, true);
  return hit;
}

// ---- 基本（廃墟・避難所）とサプライ外 ----
const extras = [
  { id: 'ruins', name: '廃墟', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '廃墟の山', desc: '5 種類の廃墟を混ぜた山。一番上の札が獲得される' },
  { id: 'ruin_mine', pile: 'ruins', name: '廃坑', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '+1 金', desc: '', *play(g) { g.turn.money += 1; } },
  { id: 'ruin_library', pile: 'ruins', name: '図書館跡地', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '+1 カード', desc: '', *play(g, p) { drawCards(p, 1); } },
  { id: 'ruin_market', pile: 'ruins', name: '市場跡地', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '+1 購入', desc: '', *play(g) { g.turn.buys += 1; } },
  { id: 'ruin_village', pile: 'ruins', name: '廃村', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '+1 アクション', desc: '', *play(g) { g.turn.actions += 1; } },
  {
    id: 'ruin_survivors', pile: 'ruins', name: '生存者', types: ['action', 'ruins'], cost: 0, notSupply: true, main: '上 2 枚を見る', desc: '山札の上 2 枚を見て、捨てるか好きな順に戻す',
    *play(g, p, pi) {
      const seen = reveal(p, 2);
      if (!seen.length) return;
      if (yield* askYesNo(g, pi, '見た札を捨てますか？', '捨てる', '戻す', seen)) yield* discardCards(g, p, seen); else yield* putBackInOrder(g, pi, seen);
    },
  },
  {
    id: 'shack', name: '納屋', types: ['reaction', 'shelter'], cost: 1, notSupply: true, main: '避難所', desc: '勝利点カードを買ったとき、手札から廃棄してよい',
    *reactBuy(g, id, pi) {
      if (!is(id, 'victory')) return;
      const p = g.players[pi];
      if (yield* askYesNo(g, pi, '「納屋」を廃棄しますか？', '廃棄する', 'しない', ['shack'])) yield* trashCards(g, p, takeFromHand(p, [p.hand.indexOf('shack')]));
    },
  },
  { id: 'tombs', name: '共同墓地', types: ['action', 'shelter'], cost: 1, notSupply: true, main: '+2 アクション', desc: '避難所', *play(g) { g.turn.actions += 2; } },
  {
    id: 'wildestate', name: '草茂る屋敷', types: ['victory', 'shelter'], cost: 1, notSupply: true, points: 0, main: '0 点', desc: '避難所。廃棄したとき +1 カード',
    *onTrash(g, p) { drawCards(p, 1); },
  },
  {
    id: 'booty', name: '略奪品', types: ['treasure'], cost: 0, notSupply: true, value: 3, autoPlay: true, main: '+3 金', desc: '使ったら、山に戻す',
    *play(g) { returnToPile(g, 'booty'); },
  },
  {
    id: 'lunatic', name: '狂人', types: A, cost: 0, notSupply: true, main: '+2 アクション', desc: 'これを山に戻す。戻したら、手札 1 枚につき +1 カード',
    *play(g, p) { g.turn.actions += 2; if (returnToPile(g, 'lunatic')) drawCards(p, p.hand.length); },
  },
  {
    id: 'sellsword', name: '傭兵', types: AA, cost: 0, notSupply: true, main: '2 枚廃棄して\n+2 カード +2 金', desc: '手札を 2 枚廃棄してよい。そうしたら +2 カード +2 金、他の人は手札が 3 枚になるまで捨てる',
    *play(g, p, pi) {
      const ok = p.hand.length >= 2 && (yield* askYesNo(g, pi, '手札を 2 枚廃棄しますか？', '廃棄する', 'しない'));
      if (ok) {
        yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 2 枚を選ぶ', 2, 2)));
        drawCards(p, 2); g.turn.money += 2;
      }
      yield* attackOthers(g, function* (ti) { if (ok) yield* discardDownTo(g, ti, 3); });
    },
  },
];

// ---- 騎士（10 種を混ぜた 1 つの山） ----
function knight(id, name, cost, main, extra, more = {}) {
  return {
    id, name, pile: 'knights', types: ['action', 'attack', 'knight', ...(more.victory ? ['victory'] : [])], cost, notSupply: true, main,
    desc: `${main.replace(/\n/g, ' ')}。他の人は山札の上 2 枚をめくり、コスト 3〜6 の 1 枚を廃棄し、残りを捨てる。騎士が廃棄されたら、この札も廃棄する`,
    ...more,
    *play(g, p, pi) {
      if (extra) yield* extra(g, p, pi);
      let knightHit = false;
      yield* attackOthers(g, function* (ti) { const hit = yield* trashThreeToSix(g, ti); if (hit && is(hit, 'knight')) knightHit = true; });
      if (knightHit) yield* trashSelf(g, p, id);
    },
  };
}
const knights = [
  knight('k_ade', 'デイム・アンナ', 5, '2 枚まで廃棄', function* (g, p, pi) { yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄するカード（2 枚まで）', 0, 2))); }),
  knight('k_gisele', 'デイム・ジョセフィーヌ', 5, '2 点', null, { victory: true, points: 2 }),
  knight('k_mira', 'デイム・モリー', 5, '+2 アクション', function* (g) { g.turn.actions += 2; }),
  knight('k_noel', 'デイム・ナタリー', 5, 'コスト 3 以下を獲得', function* (g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 3 以下を獲得してよい', 3, null, true)); }),
  knight('k_serena', 'デイム・シルビア', 5, '+2 金', function* (g) { g.turn.money += 2; }),
  knight('k_bart', 'サー・ベイリー', 5, '+1 カード\n+1 アクション', function* (g, p) { drawCards(p, 1); g.turn.actions += 1; }),
  knight('k_derek', 'サー・デストリー', 5, '+2 カード', function* (g, p) { drawCards(p, 2); }),
  knight('k_marco', 'サー・マーチン', 4, '+2 購入', function* (g) { g.turn.buys += 2; }),
  knight('k_mika', 'サー・マイケル', 5, '手札を 3 枚に', function* (g) { yield* attackOthers(g, (ti) => discardDownTo(g, ti, 3)); }),
  knight('k_will', 'サー・ヴァンデル', 5, '廃棄されたら金貨', null, { *onTrash(g, p, pi) { yield* gain(g, pi, 'gold'); } }),
];

const kingdom = [
  { id: 'knights', name: '騎士団', types: ['action', 'attack', 'knight'], cost: 5, main: '騎士の山', desc: '10 人のちがう騎士を混ぜた山。一番上の騎士が買える' },
  // ---- コスト 1〜2 ----
  {
    id: 'poorhouse', name: '救貧院', cost: 1, main: '+4 金 - 財宝', desc: '+4 金。手札を見せ、財宝 1 枚につき -1 金（0 より下にはならない）',
    *play(g, p) { g.turn.money += Math.max(0, 4 - p.hand.filter((id) => is(id, 'treasure')).length); },
  },
  {
    id: 'pauper', name: '物乞い', types: ['action', 'reaction'], cost: 2, main: '銅貨 3 枚を手札に', desc: '銅貨を 3 枚手札に獲得する。他の人がアタックを使ったとき、これを捨てて、銀貨を 2 枚（1 枚は山札の上に）獲得してよい',
    *play(g, p, pi) { for (let k = 0; k < 3; k++) yield* gain(g, pi, 'copper', 'hand'); },
    *onAttack(g, t, ti) {
      yield* discardCards(g, t, takeFromHand(t, [t.hand.indexOf('pauper')]));
      yield* gain(g, ti, 'silver', 'deck');
      yield* gain(g, ti, 'silver');
    },
  },
  {
    id: 'footman', name: '従者', cost: 2, main: '+1 金', desc: '+2 アクション / +2 購入 / 銀貨を獲得 から 1 つ。廃棄したとき、アタックカードを 1 枚獲得する',
    *play(g, p, pi) {
      g.turn.money += 1;
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'a', label: '+2 アクション' }, { value: 'b', label: '+2 購入' }, { value: 's', label: '銀貨を獲得' }]);
      if (v === 'a') g.turn.actions += 2; else if (v === 'b') g.turn.buys += 2; else yield* gain(g, pi, 'silver');
    },
    *onTrash(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'アタックカードを 1 枚獲得', 99, (id) => is(id, 'attack'))); },
  },
  {
    id: 'rover', name: '浮浪者', cost: 2, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくり、呪い・廃墟・避難所・勝利点なら手札に入れる',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (['curse', 'ruins', 'shelter', 'victory'].some((t) => is(id, t))) p.hand.push(id); else putOnDeck(p, id);
    },
  },
  // ---- コスト 3 ----
  {
    id: 'gleaner', name: '採集者', cost: 3, main: '+1 アクション\n+1 購入', desc: '手札を 1 枚廃棄する。廃棄置き場のちがう名前の財宝 1 種につき +1 金',
    *play(g, p, pi) {
      g.turn.actions += 1; g.turn.buys += 1;
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1)));
      g.turn.money += new Set(g.trash.filter((id) => is(id, 'treasure'))).size;
    },
  },
  {
    id: 'recluse', name: '隠遁者', cost: 3, main: '廃棄して獲得', desc: '捨て札か手札の財宝以外を 1 枚廃棄してよい。コスト 3 以下を獲得する。何も買わなかった手番の片付けで、これを廃棄して狂人を獲得する',
    *play(g, p, pi) {
      const pool = [...p.discard.map((id, i) => ({ id, where: 'discard', i })), ...p.hand.map((id, i) => ({ id, where: 'hand', i }))].filter((x) => !is(x.id, 'treasure'));
      const [k] = yield* askCards(g, pi, '廃棄する札（捨て札・手札から。しなくてもよい）', pool.map((x) => x.id), 0, 1);
      if (k != null) {
        const x = pool[k];
        const [id] = (x.where === 'hand' ? p.hand : p.discard).splice(x.i, 1);
        yield* trashCards(g, p, [id]);
      }
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 3 以下を獲得', 3));
    },
    *onCleanup(g, p, pi) {
      if (g.turn.bought.length) return;
      if (yield* trashSelf(g, p, 'recluse')) yield* gain(g, pi, 'lunatic');
    },
  },
  {
    id: 'marketsquare', name: '青空市場', types: ['action', 'reaction'], cost: 3, main: '+1 カード　+1 アクション\n+1 購入', desc: '自分の札を廃棄したとき、手札からこれを捨てて金貨を獲得してよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; },
  },
  {
    id: 'scholar', name: '賢者', cost: 3, main: '+1 アクション', desc: 'コスト 3 以上が出るまで山札をめくり、それを手札に入れる。ほかは捨てる',
    *play(g, p) {
      g.turn.actions += 1;
      const other = [];
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        if (costOf(g, id) >= 3) { p.hand.push(id); break; }
        other.push(id);
      }
      yield* discardCards(g, p, other, true);
    },
  },
  {
    id: 'lumberroom', name: '物置', cost: 3, main: '+1 購入', desc: '好きな枚数捨てて同じ数引く。そのあと好きな枚数捨てて、1 枚につき +1 金',
    *play(g, p, pi) {
      g.turn.buys += 1;
      const a = takeFromHand(p, yield* askHand(g, pi, '捨てて引き直す札（好きな枚数）', 0, p.hand.length));
      yield* discardCards(g, p, a);
      drawCards(p, a.length);
      const b = takeFromHand(p, yield* askHand(g, pi, '捨てて +1 金にする札（好きな枚数）', 0, p.hand.length));
      yield* discardCards(g, p, b);
      g.turn.money += b.length;
    },
  },
  {
    id: 'waif', name: '浮浪児', types: AA, cost: 3, main: '+1 カード\n+1 アクション', desc: '他の人は手札が 4 枚になるまで捨てる。これが場にあるとき、別のアタックを使ったら、これを廃棄して傭兵を獲得してよい',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      yield* attackOthers(g, (ti) => discardDownTo(g, ti, 4));
    },
  },
  // ---- コスト 4 ----
  {
    id: 'arsenal', name: '武器庫', cost: 4, main: '山札の上に獲得', desc: 'コスト 4 以下を 1 枚、山札の上に獲得する',
    *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を山札の上に獲得', 4), 'deck'); },
  },
  {
    id: 'corpsecart', name: '死の荷車', types: ['action', 'looter'], cost: 4, main: '+5 金', desc: '手札のアクションを 1 枚廃棄してよい。しなければこれを廃棄する。これを獲得したとき、廃墟を 2 枚獲得する',
    *play(g, p, pi) {
      g.turn.money += 5;
      const [i] = yield* askHand(g, pi, '廃棄するアクション（しなければ死の荷車を廃棄）', 0, 1, (id) => is(id, 'action'));
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); else yield* trashSelf(g, p, 'corpsecart');
    },
    *onGain(g, got) { yield* gain(g, got.pi, 'ruins'); yield* gain(g, got.pi, 'ruins'); },
  },
  {
    id: 'fief', name: '封土', types: ['victory'], cost: 4, main: '銀貨 3 枚ごとに 1 点', desc: '持っている銀貨 3 枚ごとに 1 点。廃棄したとき、銀貨を 3 枚獲得する',
    pointsFn: (all) => Math.floor(all.filter((id) => id === 'silver').length / 3),
    *onTrash(g, p, pi) { for (let k = 0; k < 3; k++) yield* gain(g, pi, 'silver'); },
  },
  {
    id: 'stronghold', name: '城塞', cost: 4, main: '+1 カード\n+2 アクション', desc: '廃棄したとき、手札に戻す',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onTrash(g, p) { const i = g.trash.lastIndexOf('stronghold'); if (i >= 0) { g.trash.splice(i, 1); p.hand.push('stronghold'); log(g, `${p.name}の城塞が手札に戻った。`); } },
  },
  {
    id: 'hardware', name: '金物商', cost: 4, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくり、捨ててよい。アクションなら +1 アクション、財宝なら +1 金、勝利点なら +1 カード',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (yield* askYesNo(g, pi, `山札の一番上は${nm(id)}。捨てますか？`, '捨てる', '戻す', [id])) yield* discardCards(g, p, [id]); else putOnDeck(p, id);
      if (is(id, 'action')) g.turn.actions += 1;
      if (is(id, 'treasure')) g.turn.money += 1;
      if (is(id, 'victory')) drawCards(p, 1);
    },
  },
  {
    id: 'ravager', name: '襲撃者', types: LOOT, cost: 4, main: '略奪品を獲得', desc: '略奪品を 1 枚獲得する。他の人は廃墟を 1 枚獲得する',
    *play(g, p, pi) {
      yield* gain(g, pi, 'booty');
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'ruins'); });
    },
  },
  {
    id: 'parade', name: '行進', cost: 4, main: '2 回使って\n格上げ', desc: '手札のアクションを 1 枚 2 回使ってよい。そのあとそれを廃棄し、ちょうどコスト +1 のアクションを獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '2 回使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      yield* resolve(g, id);
      yield* resolve(g, id);
      yield* trashSelf(g, p, id);
      const c = costOf(g, id) + 1;
      yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} のアクションを獲得`, c, (x) => is(x, 'action') && costOf(g, x) === c));
    },
  },
  {
    id: 'rats', name: 'ネズミ', cost: 4, main: '+1 カード\n+1 アクション', desc: 'ネズミを 1 枚獲得する。手札のネズミ以外を 1 枚廃棄する。廃棄したとき +1 カード',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      yield* gain(g, pi, 'rats');
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚（ネズミ以外）', 1, 1, (id) => id !== 'rats')));
    },
    *onTrash(g, p) { drawCards(p, 1); },
  },
  {
    id: 'scrounger', name: 'ゴミあさり', cost: 4, main: '+2 金', desc: '山札をまとめて捨て札にしてよい。捨て札を見て 1 枚を山札の上に置く',
    *play(g, p, pi) {
      g.turn.money += 2;
      if (p.deck.length && (yield* askYesNo(g, pi, '山札をまとめて捨て札にしますか？', 'する', 'しない'))) p.discard.push(...p.deck.splice(0));
      const [i] = yield* askCards(g, pi, '捨て札から山札の上に置く 1 枚', [...p.discard], 1, 1);
      if (i != null) putOnDeck(p, p.discard.splice(i, 1)[0]);
    },
  },
  {
    id: 'troubadour', name: '吟遊詩人', cost: 4, main: '+1 カード\n+2 アクション', desc: '山札の上 3 枚をめくり、アクションを好きな順に戻し、残りを捨てる',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 2;
      const shown = reveal(p, 3);
      yield* discardCards(g, p, shown.filter((id) => !is(id, 'action')), true);
      yield* putBackInOrder(g, pi, shown.filter((id) => is(id, 'action')));
    },
  },
  // ---- コスト 5 ----
  {
    id: 'impostor', name: 'はみだし者', types: ['action', 'command'], cost: 5, main: '安いアクション\nとして使う', desc: 'サプライの、これより安いアクションカードを 1 つ選び、それとして使う',
    *play(g, p, pi) {
      const c = costOf(g, 'impostor');
      const id = yield* askSupply(g, pi, `コスト ${c - 1} 以下のアクションを選ぶ（それとして使う）`, c - 1, (x) => is(x, 'action') && !is(x, 'command'));
      if (!id) return;
      log(g, `はみだし者が${nm(id)}として使われた。`);
      yield* resolve(g, id);
    },
  },
  {
    id: 'hideout', name: '山賊の宿営地', cost: 5, main: '+1 カード\n+2 アクション', desc: '略奪品を 1 枚獲得する',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 2; yield* gain(g, pi, 'booty'); },
  },
  {
    id: 'ossuary', name: '地下墓所', cost: 5, main: '上 3 枚を見る', desc: '山札の上 3 枚を見て、手札に入れるか、捨てて +3 カードかを選ぶ。廃棄したとき、これより安いカードを獲得する',
    *play(g, p, pi) {
      const seen = reveal(p, 3);
      if (yield* askYesNo(g, pi, 'この 3 枚をどうしますか？', '手札に入れる', '捨てて 3 枚引く', seen)) p.hand.push(...seen);
      else { yield* discardCards(g, p, seen); drawCards(p, 3); }
    },
    *onTrash(g, p, pi) { const c = costOf(g, 'ossuary'); yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下を獲得`, c - 1)); },
  },
  {
    id: 'viscount', name: '伯爵', cost: 5, main: '2 回選ぶ', desc: '「2 枚捨てる / 1 枚を山札の上に / 銅貨を獲得」から 1 つ、「+3 金 / 手札をすべて廃棄 / 公領を獲得」から 1 つ',
    *play(g, p, pi) {
      const a = yield* askChoose(g, pi, '1 つめ', [{ value: 'd', label: '2 枚捨てる' }, { value: 't', label: '1 枚を山札の上に' }, { value: 'c', label: '銅貨を獲得' }]);
      if (a === 'd') yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚', 2, 2)));
      else if (a === 't') { const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚', 1, 1); if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]); }
      else yield* gain(g, pi, 'copper');
      const b = yield* askChoose(g, pi, '2 つめ', [{ value: 'm', label: '+3 金' }, { value: 'x', label: '手札をすべて廃棄' }, { value: 'u', label: '公領を獲得' }]);
      if (b === 'm') g.turn.money += 3;
      else if (b === 'x') yield* trashCards(g, p, p.hand.splice(0));
      else yield* gain(g, pi, 'duchy');
    },
  },
  {
    id: 'forgery', name: '偽造通貨', types: ['treasure'], cost: 5, value: 1, main: '+1 金　+1 購入', desc: '手札の財宝を 1 枚 2 回使ってよい。そうしたら、それを廃棄する',
    *play(g, p, pi) {
      g.turn.buys += 1;
      const [i] = yield* askHand(g, pi, '2 回使う財宝（なしでもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      yield* treasureEffect(g, id);
      yield* treasureEffect(g, id);
      yield* trashSelf(g, p, id);
    },
  },
  {
    id: 'zealot', name: '狂信者', types: LOOT, cost: 5, main: '+2 カード', desc: '他の人は廃墟を獲得する。手札の狂信者を使ってよい。廃棄したとき +3 カード',
    *play(g, p, pi) {
      drawCards(p, 2);
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'ruins'); });
      if (p.hand.includes('zealot') && (yield* askYesNo(g, pi, '手札の狂信者も使いますか？', '使う', '使わない', ['zealot']))) {
        p.hand.splice(p.hand.indexOf('zealot'), 1);
        g.playArea.push('zealot');
        log(g, `${p.name}が「狂信者」を使用。`);
        yield* resolve(g, 'zealot');
      }
    },
    *onTrash(g, p) { drawCards(p, 3); },
  },
  {
    id: 'gravedigger', name: '墓暴き', cost: 5, main: '廃棄置き場から\nか 格上げ', desc: '廃棄置き場のコスト 3〜6 を山札の上に獲得するか、手札のアクションを廃棄してコスト +3 以下を獲得するかを選ぶ',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'trash', label: '廃棄置き場から獲得' }, { value: 'up', label: 'アクションを格上げ' }]);
      if (v === 'trash') { yield* fromTrash(g, pi, '獲得する札（コスト 3〜6）', (id) => costOf(g, id) >= 3 && costOf(g, id) <= 6, 'deck'); return; }
      const [i] = yield* askHand(g, pi, '廃棄するアクション', 1, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 3;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得`, max));
    },
  },
  {
    id: 'junkman', name: '屑屋', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: '手札を 1 枚廃棄する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1;
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1)));
    },
  },
  {
    id: 'psychic', name: '秘術師', cost: 5, main: '+1 アクション\n+2 金', desc: '名前を 1 つ言い、山札の一番上をめくる。当たれば手札に入れる',
    *play(g, p, pi) {
      g.turn.actions += 1; g.turn.money += 2;
      const mine = [...new Set(allCards(p))];
      const [k] = yield* askCards(g, pi, '山札の一番上を当てる', mine, 1, 1);
      const [top] = reveal(p, 1);
      if (top == null) return;
      if (top === mine[k ?? 0]) { p.hand.push(top); log(g, `${p.name}が${nm(top)}を当てた！`); } else putOnDeck(p, top);
    },
  },
  {
    id: 'ransack', name: '略奪', types: AA, cost: 5, main: '略奪品 2 枚', desc: 'これを廃棄する。手札が 5 枚以上の他の人は手札を見せ、あなたが選んだ 1 枚を捨てる。略奪品を 2 枚獲得する',
    *play(g, p, pi) {
      yield* trashSelf(g, p, 'ransack');
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 5) return;
        const [i] = yield* askCards(g, pi, `${t.name}の手札から捨てさせる 1 枚`, [...t.hand], 1, 1);
        yield* discardCards(g, t, takeFromHand(t, [i ?? 0]));
      });
      yield* gain(g, pi, 'booty');
      yield* gain(g, pi, 'booty');
    },
  },
  {
    id: 'rework', name: '建て直し', cost: 5, main: '+1 アクション', desc: '名前を 1 つ言い、それ以外の勝利点が出るまで山札をめくる。それを廃棄し、コスト +3 以下の勝利点を獲得する。ほかは捨てる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const vs = Object.keys(g.supply).filter((id) => is(id, 'victory'));
      const [k] = yield* askCards(g, pi, '見逃す勝利点の名前を選ぶ', vs, 1, 1);
      const named = vs[k ?? 0];
      const other = [];
      let hit = null;
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        if (is(id, 'victory') && id !== named) { hit = id; break; }
        other.push(id);
      }
      yield* discardCards(g, p, other, true);
      if (!hit) return;
      yield* trashCards(g, p, [hit]);
      const max = costOf(g, hit) + 3;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下の勝利点を獲得`, max, (x) => is(x, 'victory')));
    },
  },
  {
    id: 'villain', name: '盗賊', types: AA, cost: 5, main: '+2 金', desc: '廃棄置き場にコスト 3〜6 があれば 1 枚獲得する。なければ、他の人は山札の上 2 枚からコスト 3〜6 を 1 枚廃棄し、残りを捨てる',
    *play(g, p, pi) {
      g.turn.money += 2;
      const got = yield* fromTrash(g, pi, '廃棄置き場から獲得する札（コスト 3〜6）', (id) => costOf(g, id) >= 3 && costOf(g, id) <= 6);
      yield* attackOthers(g, function* (ti) { if (!got) yield* trashThreeToSix(g, ti); });
    },
  },
  // ---- コスト 6 ----
  {
    id: 'offering', name: '祭壇', cost: 6, main: '廃棄して獲得', desc: '手札を 1 枚廃棄する。コスト 5 以下を 1 枚獲得する',
    *play(g, p, pi) {
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1)));
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を獲得', 5));
    },
  },
  {
    id: 'huntland', name: '狩場', cost: 6, main: '+4 カード', desc: '廃棄したとき、公領 1 枚か屋敷 3 枚を獲得する',
    *play(g, p) { drawCards(p, 4); },
    *onTrash(g, p, pi) {
      if (yield* askYesNo(g, pi, '狩場: どちらを獲得しますか？', '公領 1 枚', '屋敷 3 枚')) yield* gain(g, pi, 'duchy');
      else for (let k = 0; k < 3; k++) yield* gain(g, pi, 'estate');
    },
  },
];

// ---- どのカードにも関わる決まり ----
// 青空市場: 自分の札を廃棄したとき、手札の青空市場を捨てて金貨を獲得してよい
HOOKS.trash.push(function* (g, p, pi) {
  while (p.hand.includes('marketsquare') && (yield* askYesNo(g, pi, '札を廃棄した。「青空市場」を捨てて金貨を獲得しますか？', '捨てる', 'しない', ['marketsquare']))) {
    yield* discardCards(g, p, takeFromHand(p, [p.hand.indexOf('marketsquare')]), true);
    yield* gain(g, pi, 'gold');
  }
});
// 浮浪児: 場にあるとき別のアタックを使ったら、廃棄して傭兵を獲得してよい
HOOKS.play.push(function* (g, id) {
  if (!is(id, 'attack') || !g.playArea.includes('waif')) return;
  const p = currentPlayer(g);
  const others = g.playArea.filter((x) => x === 'waif').length - (id === 'waif' ? 1 : 0);
  for (let k = 0; k < others; k++) {
    if (!(yield* askYesNo(g, g.current, '「浮浪児」を廃棄して傭兵を獲得しますか？', '廃棄する', 'しない', ['waif']))) break;
    const at = g.playArea.indexOf('waif');
    yield* trashCards(g, p, g.playArea.splice(at, 1));
    yield* gain(g, g.current, 'sellsword');
  }
});
HOOKS.setup.push((g) => {
  const k = g.kingdom;
  const n = g.players.length;
  if (k.includes('knights')) { g.stacks.knights = shuffle(knights.map((c) => c.id)); g.supply.knights = 10; }
  if (k.some((id) => is(id, 'looter'))) {
    const all = shuffle(['ruin_mine', 'ruin_library', 'ruin_market', 'ruin_village', 'ruin_survivors'].flatMap((id) => Array(10).fill(id)));
    g.stacks.ruins = all.slice(0, 10 * (n - 1));
    g.supply.ruins = g.stacks.ruins.length;
  }
  if (k.some((id) => ['ravager', 'hideout', 'ransack'].includes(id))) g.nonSupply.booty = 15;
  if (k.includes('recluse')) g.nonSupply.lunatic = 10;
  if (k.includes('waif')) g.nonSupply.sellsword = 10;
});

defineCards({ id: 'darkages', name: '暗黒時代' }, [...extras, ...knights, ...kingdom], [
  { id: 'grimparade', name: '陰気な行列', cards: ['viscount', 'fief', 'knights', 'recluse', 'parade', 'rats', 'scholar', 'gleaner', 'waif', 'rework'] },
  { id: 'highandlow', name: '上と下', cards: ['recluse', 'huntland', 'psychic', 'poorhouse', 'pauper', 'offering', 'arsenal', 'impostor', 'zealot', 'gravedigger'] },
  { id: 'chivalryandrevelry', name: '騎士道と宴', cards: ['footman', 'rover', 'marketsquare', 'lumberroom', 'stronghold', 'hardware', 'troubadour', 'ossuary', 'junkman', 'knights'] },
  { id: 'deconstruction', name: '取り壊し（基本と混ぜる）', cards: ['offering', 'forgery', 'rover', 'gravedigger', 'hideout', 'remodel', 'mine', 'sorcerer', 'workshop', 'fair'] },
]);
