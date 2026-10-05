'use strict';
// 拡張「夜想曲」のカード（王国 33 種）、家宝 7 種、精霊など 10 種、恵み 12・呪詛 12・状態 5。カード名は公式日本語版に合わせた。
// 夜行（night）: 購入のあとの夜のフェイズに使う。恵み・呪詛は山（game.boons / game.hexes）から 1 枚ずつめくって受ける。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, playOutOfTurn, treasureEffect, later, returnCard, returnToPile, currentPlayer,
  allCards, shuffle, receive, rng,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const N = ['night'];
const ND = ['night', 'duration'];
const FATE = ['action', 'fate'];
const DOOM = ['action', 'doom'];

function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
function* playFrom(g, pi, id) {
  g.playArea.push(id);
  log(g, `${g.players[pi].name}が${nm(id)}を使用。`);
  yield* resolve(g, id);
}
function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
// 恵み・呪詛の山からめくる（空なら捨てた分を混ぜ直す）
// 山がない対局（なりすまし・覇王などで別の札として使った）では、その場で作る
function pileFor(g, key) {
  if (!g[key]) g[key] = { deck: shuffle((key === 'boons' ? boons : hexes).map((c) => c.id), g), discard: [] };
  return g[key];
}
function drawFrom(g, pile) {
  if (!pile.deck.length) { pile.deck = shuffle(pile.discard, g); pile.discard = []; }
  return pile.deck.pop();
}
export function* receiveBoon(g, pi, id) {
  const b = id || drawFrom(g, pileFor(g, 'boons'));
  if (!b) return null;
  log(g, `${g.players[pi].name}が${nm(b)}を受けた。`);
  yield* CARDS[b].receive(g, g.players[pi], pi);
  if (!id) pileFor(g, 'boons').discard.push(b);
  return b;
}
function* receiveHex(g, pi, id) {
  const h = id || drawFrom(g, pileFor(g, 'hexes'));
  if (!h) return null;
  log(g, `${g.players[pi].name}が${nm(h)}を受けた。`);
  yield* CARDS[h].receive(g, g.players[pi], pi);
  if (!id) pileFor(g, 'hexes').discard.push(h);
  return h;
}
// 状態を得る。森の迷子は 1 人だけが持つ。錯乱・嫉妬は同時に 1 つだけ
function takeState(g, pi, id) {
  const p = g.players[pi];
  if (id === 's_lost') for (const q of g.players) q.states = q.states.filter((s) => s !== 's_lost');
  if (!p.states.includes(id)) p.states.push(id);
}

// ---- 恵み ----
const B = ['boon'];
const boons = [
  { id: 'b_earth', name: '大地の恵み', types: B, cost: 0, notSupply: true, main: '財宝を捨てて獲得', desc: '手札の財宝を 1 枚捨てて、コスト 4 以下を獲得してよい',
    *receive(g, p, pi) {
      const [i] = yield* askHand(g, pi, '捨てる財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure'));
      if (i == null) return;
      yield* discardCards(g, p, takeFromHand(p, [i]));
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4));
    } },
  { id: 'b_field', name: '田畑の恵み', types: B, cost: 0, notSupply: true, main: '+1 アクション\n+1 金', desc: '', *receive(g, p, pi) { if (pi === g.current) { g.turn.actions += 1; g.turn.money += 1; } } },
  { id: 'b_flame', name: '炎の恵み', types: B, cost: 0, notSupply: true, main: '廃棄', desc: '手札を 1 枚廃棄してよい',
    *receive(g, p, pi) { const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); } },
  { id: 'b_forest', name: '森の恵み', types: B, cost: 0, notSupply: true, main: '+1 購入\n+1 金', desc: '', *receive(g, p, pi) { if (pi === g.current) { g.turn.buys += 1; g.turn.money += 1; } } },
  { id: 'b_moon', name: '月の恵み', types: B, cost: 0, notSupply: true, main: '捨て札を山札に', desc: '捨て札を見て、1 枚を山札の上に置いてよい',
    *receive(g, p, pi) { const [i] = yield* askCards(g, pi, '山札の上に置く 1 枚（なしでもよい）', [...p.discard], 0, 1); if (i != null) putOnDeck(p, p.discard.splice(i, 1)[0]); } },
  { id: 'b_mountain', name: '山の恵み', types: B, cost: 0, notSupply: true, main: '銀貨を獲得', desc: '', *receive(g, p, pi) { yield* gain(g, pi, 'silver'); } },
  { id: 'b_river', name: '川の恵み', types: B, cost: 0, notSupply: true, main: '手番の終わりに\n+1 カード', desc: '', *receive(g, p, pi) { if (pi === g.current) g.turn.extraDraw = (g.turn.extraDraw || 0) + 1; } },
  { id: 'b_sea', name: '海の恵み', types: B, cost: 0, notSupply: true, main: '+1 カード', desc: '', *receive(g, p) { drawCards(p, 1); } },
  { id: 'b_sky', name: '太陽の恵み', types: B, cost: 0, notSupply: true, main: '3 枚捨てて金貨', desc: '手札を 3 枚捨てて、金貨を獲得してよい',
    *receive(g, p, pi) {
      if (p.hand.length < 3 || !(yield* askYesNo(g, pi, '手札を 3 枚捨てて金貨を獲得しますか？', 'する', 'しない'))) return;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚', 3, 3)));
      yield* gain(g, pi, 'gold');
    } },
  { id: 'b_sun', name: '空の恵み', types: B, cost: 0, notSupply: true, main: '上 4 枚を見る', desc: '山札の上 4 枚を見て、好きな枚数捨て、残りを好きな順に戻す',
    *receive(g, p, pi) {
      const seen = reveal(p, 4);
      const idx = yield* askCards(g, pi, '捨てる札（好きな枚数）', seen, 0, seen.length);
      yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)), true);
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    } },
  { id: 'b_swamp', name: '沼の恵み', types: B, cost: 0, notSupply: true, main: 'ウィル・オ・ウィスプを獲得', desc: '', *receive(g, p, pi) { yield* gain(g, pi, 'wisp'); } },
  { id: 'b_wind', name: '風の恵み', types: B, cost: 0, notSupply: true, main: '+2 カード\n2 枚捨てる', desc: '',
    *receive(g, p, pi) { drawCards(p, 2); yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚', 2, 2))); } },
];

// ---- 呪詛 ----
const H = ['hex'];
const hexes = [
  { id: 'h_omens', name: '凶兆', types: H, cost: 0, notSupply: true, main: '山札を捨て\n銅貨 2 枚を戻す', desc: '山札を捨て札にし、捨て札の銅貨を 2 枚山札の上に置く',
    *receive(g, p) {
      p.discard.push(...p.deck.splice(0));
      for (let k = 0; k < 2 && p.discard.includes('copper'); k++) putOnDeck(p, p.discard.splice(p.discard.indexOf('copper'), 1)[0]);
    } },
  { id: 'h_delusion', name: '幻惑', types: H, cost: 0, notSupply: true, main: '錯乱を受ける', desc: '錯乱・嫉妬のどちらも持っていなければ、錯乱を受ける',
    *receive(g, p, pi) { if (!p.states.includes('s_deluded') && !p.states.includes('s_envious')) takeState(g, pi, 's_deluded'); } },
  { id: 'h_envy', name: '羨望', types: H, cost: 0, notSupply: true, main: '嫉妬を受ける', desc: '錯乱・嫉妬のどちらも持っていなければ、嫉妬を受ける',
    *receive(g, p, pi) { if (!p.states.includes('s_deluded') && !p.states.includes('s_envious')) takeState(g, pi, 's_envious'); } },
  { id: 'h_famine', name: '飢饉', types: H, cost: 0, notSupply: true, main: 'アクションを捨てる', desc: '山札の上 3 枚をめくり、アクションを捨て、残りを山札に混ぜる',
    *receive(g, p) {
      const shown = reveal(p, 3);
      yield* discardCards(g, p, shown.filter((id) => is(id, 'action')), true);
      p.deck.push(...shown.filter((id) => !is(id, 'action')));
      shuffle(p.deck, g);
    } },
  { id: 'h_fear', name: '恐怖', types: H, cost: 0, notSupply: true, main: 'アクションか財宝を捨てる', desc: '手札が 5 枚以上なら、アクションか財宝を 1 枚捨てる',
    *receive(g, p, pi) { if (p.hand.length >= 5) yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てるアクションか財宝', 1, 1, (id) => is(id, 'action') || is(id, 'treasure')))); } },
  { id: 'h_greed', name: '貪欲', types: H, cost: 0, notSupply: true, main: '銅貨を山札の上に', desc: '', *receive(g, p, pi) { yield* gain(g, pi, 'copper', 'deck'); } },
  { id: 'h_haunting', name: '憑依', types: H, cost: 0, notSupply: true, main: '1 枚を山札の上に', desc: '手札が 4 枚以上なら、1 枚を山札の上に置く',
    *receive(g, p, pi) { if (p.hand.length >= 4) { const [i] = yield* askHand(g, pi, '山札の上に置く 1 枚', 1, 1); if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]); } } },
  { id: 'h_locusts', name: '蝗害', types: H, cost: 0, notSupply: true, main: '山札の上を廃棄', desc: '山札の一番上を廃棄する。銅貨か屋敷なら呪いを獲得。ほかは同じ種類でそれより安い札を獲得する',
    *receive(g, p, pi) {
      const [id] = reveal(p, 1);
      if (id == null) return;
      yield* trashCards(g, p, [id]);
      if (id === 'copper' || id === 'estate') { yield* gain(g, pi, 'curse'); return; }
      const c = costOf(g, id);
      if (c > 0) yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${c - 1} 以下で同じ種類の札を獲得`, c - 1, (x) => CARDS[x].types.some((t) => CARDS[id].types.includes(t))));
    } },
  { id: 'h_misery', name: 'みじめな生活', types: H, cost: 0, notSupply: true, main: '生活苦', desc: 'はじめてなら生活苦（-2 点）、2 回目からは二重苦（-4 点）',
    *receive(g, p, pi) {
      if (p.states.includes('s_twice')) return;
      if (p.states.includes('s_miserable')) { p.states = p.states.filter((s) => s !== 's_miserable'); takeState(g, pi, 's_twice'); } else takeState(g, pi, 's_miserable');
    } },
  { id: 'h_plague', name: '疫病', types: H, cost: 0, notSupply: true, main: '呪いを手札に', desc: '', *receive(g, p, pi) { yield* gain(g, pi, 'curse', 'hand'); } },
  { id: 'h_poverty', name: '貧困', types: H, cost: 0, notSupply: true, main: '手札を 3 枚に', desc: '', *receive(g, p, pi) { yield* discardDownTo(g, pi, 3); } },
  { id: 'h_war', name: '戦争', types: H, cost: 0, notSupply: true, main: 'コスト 3〜4 を廃棄', desc: 'コスト 3 か 4 が出るまで山札をめくり、それを廃棄する。ほかは捨てる',
    *receive(g, p) {
      const other = [];
      for (let id = takeTop(p); id != null; id = takeTop(p)) {
        if (costOf(g, id) === 3 || costOf(g, id) === 4) { yield* trashCards(g, p, [id]); break; }
        other.push(id);
      }
      yield* discardCards(g, p, other, true);
    } },
];

// ---- 状態 ----
const S = ['state'];
const states = [
  { id: 's_lost', name: '森の迷子', types: S, cost: 0, notSupply: true, main: '手番の始めに\n捨てて恵み', desc: '手番の始めに、手札を 1 枚捨てて恵みを受けてよい' },
  { id: 's_deluded', name: '錯乱', types: S, cost: 0, notSupply: true, main: 'アクションを\n買えない', desc: '購入フェイズの始めにこれを返し、その手番はアクションを買えない' },
  { id: 's_envious', name: '嫉妬', types: S, cost: 0, notSupply: true, main: '銀貨・金が 1 金', desc: '購入フェイズの始めにこれを返し、その手番は銀貨と金が 1 金しか出さない' },
  { id: 's_miserable', name: '生活苦', types: S, cost: 0, notSupply: true, points: -2, main: '-2 点', desc: '' },
  { id: 's_twice', name: '二重苦', types: S, cost: 0, notSupply: true, points: -4, main: '-4 点', desc: '' },
];

// ---- 家宝（初めのデッキの銅貨 1 枚と入れ替わる） ----
const HL = ['treasure', 'heirloom'];
const heirlooms = [
  { id: 'dimmirror', name: '呪いの鏡', types: HL, cost: 0, notSupply: true, value: 1, autoPlay: true, main: '+1 金', desc: '廃棄したとき、手札のアクションを 1 枚捨てて幽霊を獲得してよい',
    *onTrash(g, p, pi) {
      const [i] = yield* askHand(g, pi, '捨てるアクション（しなくてもよい・幽霊を獲得）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      yield* discardCards(g, p, takeFromHand(p, [i]));
      yield* gain(g, pi, 'phantom');
    } },
  { id: 'luckycoin', name: '幸運のコイン', types: HL, cost: 4, notSupply: true, value: 1, autoPlay: true, main: '+1 金\n銀貨を獲得', desc: '', *play(g, p, pi) { yield* gain(g, pi, 'silver'); } },
  { id: 'kid', name: 'ヤギ', types: HL, cost: 2, notSupply: true, value: 1, main: '+1 金', desc: '手札を 1 枚廃棄してよい',
    *play(g, p, pi) { const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1); if (i != null) yield* trashCards(g, p, takeFromHand(p, [i])); } },
  { id: 'cursedcoin', name: '呪われた金貨', types: HL, cost: 4, notSupply: true, value: 3, autoPlay: true, main: '+3 金', desc: '使うと呪いを獲得する', *play(g, p, pi) { yield* gain(g, pi, 'curse'); } },
  { id: 'wishlamp', name: '魔法のランプ', types: HL, cost: 0, notSupply: true, value: 1, autoPlay: true, main: '+1 金', desc: '場にちょうど 1 枚だけの札が 6 種以上あれば、これを廃棄して願いを 3 枚獲得する',
    *play(g, p, pi) {
      const once = [...new Set(g.playArea)].filter((id) => g.playArea.filter((x) => x === id).length === 1).length;
      if (once >= 6 && (yield* trashSelf(g, p, 'wishlamp'))) for (let k = 0; k < 3; k++) yield* gain(g, pi, 'wish2');
    } },
  { id: 'grazing', name: '牧草地', types: [...HL, 'victory'], cost: 2, notSupply: true, value: 1, main: '+1 金\n屋敷 1 枚につき 1 点', desc: '持っている屋敷 1 枚につき 1 点', pointsFn: (all) => all.filter((id) => id === 'estate').length },
  { id: 'purse', name: '革袋', types: HL, cost: 2, notSupply: true, value: 1, autoPlay: true, main: '+1 金　+1 購入', desc: '', *play(g) { g.turn.buys += 1; } },
];

// ---- 精霊など（サプライ外） ----
const others = [
  { id: 'wisp', name: 'ウィル・オ・ウィスプ', types: ['action', 'spirit'], cost: 0, notSupply: true, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくり、コスト 2 以上なら手札に入れる',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; const [id] = reveal(p, 1); if (id == null) return; if (costOf(g, id) >= 2) p.hand.push(id); else putOnDeck(p, id); } },
  { id: 'imp2', name: 'インプ', types: ['action', 'spirit'], cost: 2, notSupply: true, main: '+2 カード', desc: '場にないアクションを手札から 1 枚使ってよい',
    *play(g, p, pi) {
      drawCards(p, 2);
      const [i] = yield* askHand(g, pi, '使うアクション（場にないもの・なしでもよい）', 0, 1, (id) => is(id, 'action') && !g.playArea.includes(id));
      if (i != null) yield* playFrom(g, pi, takeFromHand(p, [i])[0]);
    } },
  { id: 'phantom', name: '幽霊', types: ['night', 'duration', 'spirit'], cost: 4, notSupply: true, main: 'アクションを\n次の手番に 2 回', desc: 'アクションが出るまで山札をめくり、それを脇に置く（ほかは捨てる）。次の手番の始めに、それを 2 回使う',
    *play(g, p, pi) {
      const other = [];
      let hit = null;
      for (let id = takeTop(p); id != null; id = takeTop(p)) { if (is(id, 'action')) { hit = id; break; } other.push(id); }
      yield* discardCards(g, p, other, true);
      if (!hit) return;
      (p.mats.phantom = p.mats.phantom || []).push(hit);
      later(g, 'phantom', function* () {
        const k = p.mats.phantom.indexOf(hit);
        if (k < 0) return;
        p.mats.phantom.splice(k, 1);
        g.playArea.push(hit);
        yield* resolve(g, hit);
        yield* resolve(g, hit);
      });
    } },
  { id: 'wish2', name: '願い', types: ['action'], cost: 0, notSupply: true, main: '+1 アクション', desc: 'これを山に戻す。戻したら、コスト 6 以下を手札に獲得する',
    *play(g, p, pi) { g.turn.actions += 1; if (returnToPile(g, 'wish2')) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 6 以下を手札に獲得', 6), 'hand'); } },
  { id: 'nightwing', name: 'コウモリ', types: N, cost: 2, notSupply: true, main: '2 枚まで廃棄', desc: '手札を 2 枚まで廃棄する。1 枚以上廃棄したら、これを吸血鬼と取り替える',
    *play(g, p, pi) {
      const ids = takeFromHand(p, yield* askHand(g, pi, '廃棄する札（2 枚まで）', 0, 2));
      yield* trashCards(g, p, ids);
      if (ids.length && g.supply.bloodsucker > 0 && returnToPile(g, 'nightwing')) { g.supply.bloodsucker -= 1; p.discard.push('bloodsucker'); log(g, `${p.name}がコウモリを吸血鬼と取り替えた。`); }
    } },
  { id: 'z_apprentice', name: 'ゾンビの弟子', types: ['action', 'zombie'], cost: 3, notSupply: true, main: 'アクションを廃棄\nして得をする', desc: '手札のアクションを 1 枚廃棄してよい。そうしたら +3 カード +1 アクション',
    *play(g, p, pi) { const [i] = yield* askHand(g, pi, '廃棄するアクション（しなくてもよい）', 0, 1, (id) => is(id, 'action')); if (i == null) return; yield* trashCards(g, p, takeFromHand(p, [i])); drawCards(p, 3); g.turn.actions += 1; } },
  { id: 'z_mason', name: 'ゾンビの石工', types: ['action', 'zombie'], cost: 3, notSupply: true, main: '山札の上を\n格上げ', desc: '山札の一番上を廃棄する。そのコスト +1 以下を獲得してよい',
    *play(g, p, pi) { const [id] = reveal(p, 1); if (id == null) return; yield* trashCards(g, p, [id]); const max = costOf(g, id) + 1; yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得してよい`, max, null, true)); } },
  { id: 'z_spy', name: 'ゾンビの密偵', types: ['action', 'zombie'], cost: 3, notSupply: true, main: '+1 カード\n+1 アクション', desc: '山札の一番上を見て、捨てるか戻す',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 1; const [id] = reveal(p, 1); if (id == null) return; if (yield* askYesNo(g, pi, `山札の一番上は${nm(id)}。捨てますか？`, '捨てる', '戻す', [id])) yield* discardCards(g, p, [id]); else putOnDeck(p, id); } },
];

const kingdom = [
  // ---- コスト 2 ----
  { id: 'druid', name: 'ドルイド', types: FATE, cost: 2, main: '+1 購入', desc: '対局の始めに脇に置いた 3 つの恵みのうち 1 つを受ける（恵みはそのまま残る）',
    *play(g, p, pi) {
      g.turn.buys += 1;
      const list = g.druidBoons || [];
      if (!list.length) return;
      const [i] = yield* askCards(g, pi, '受ける恵みを選ぶ', list, 1, 1);
      yield* receiveBoon(g, pi, list[i ?? 0]);
    } },
  { id: 'loyaldog', name: '忠犬', types: ['action', 'reaction'], cost: 2, main: '+2 カード', desc: '片付け以外で捨て札にしたとき、脇に置いて、手番の終わりに手札に戻してよい',
    *play(g, p) { drawCards(p, 2); },
    *onDiscard(g, p, pi) {
      if (!(yield* askYesNo(g, pi, '「番の犬」を脇に置いて、手番の終わりに手札に戻しますか？', '戻す', 'しない', ['loyaldog']))) return;
      const k = p.discard.lastIndexOf('loyaldog');
      if (k >= 0) (p.mats.loyaldog = p.mats.loyaldog || []).push(...p.discard.splice(k, 1));
    } },
  { id: 'protector', name: '守護者', types: ND, cost: 2, protects: true, main: '次の手番まで\nアタックを受けない', desc: '次の手番の始めに +1 金。それまで他の人のアタックを受けない。獲得したとき手札に入れる',
    *play(g) { later(g, 'protector', function* () { g.turn.money += 1; }); },
    *onGain(g, got) { yield* relocate(g, got, 'hand'); } },
  { id: 'priory', name: '修道院', types: N, cost: 2, main: '獲得した数だけ廃棄', desc: 'この手番に獲得した枚数まで、手札か場の銅貨を廃棄してよい',
    *play(g, p, pi) {
      for (let k = g.turn.gained.length; k > 0; k--) {
        const pool = [...p.hand.map((id, i) => ({ id, from: 'hand', i })), ...g.playArea.map((id, i) => ({ id, from: 'play', i })).filter((x) => x.id === 'copper')];
        const [j] = yield* askCards(g, pi, `廃棄する札（あと ${k} 枚まで・やめてもよい）`, pool.map((x) => x.id), 0, 1);
        if (j == null) break;
        const x = pool[j];
        const [id] = (x.from === 'hand' ? p.hand : g.playArea).splice(x.i, 1);
        yield* trashCards(g, p, [id]);
      }
    } },
  { id: 'sprite', name: 'ピクシー', types: FATE, cost: 2, main: '+1 カード\n+1 アクション', desc: '恵みの山の一番上を捨てる。これを廃棄して、その恵みを 2 回受けてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const b = drawFrom(g, pileFor(g, 'boons'));
      if (!b) return;
      pileFor(g, 'boons').discard.push(b);
      log(g, `恵みの山の一番上は${nm(b)}。`);
      if (g.playArea.includes('sprite') && (yield* askYesNo(g, pi, `妖精を廃棄して${nm(b)}を 2 回受けますか？`, '廃棄する', 'しない', [b]))) {
        if (yield* trashSelf(g, p, 'sprite')) { yield* receiveBoon(g, pi, b); yield* receiveBoon(g, pi, b); }
      }
    } },
  { id: 'trailer', name: '追跡者', types: FATE, cost: 2, main: '+1 金', desc: '恵みを受ける。場にあるあいだ、獲得した札を山札の上に置いてよい',
    *play(g, p, pi) { g.turn.money += 1; yield* receiveBoon(g, pi); },
    *whenGain(g, got) { if (got.to === 'discard' && (yield* askYesNo(g, got.pi, `獲得した${nm(got.id)}を山札の上に置きますか？`, '山札の上へ', 'そのまま', [got.id]))) yield* relocate(g, got, 'deck'); } },
  // ---- コスト 3 ----
  { id: 'fairychild', name: '取り替え子', types: N, cost: 3, main: '場の札を写す', desc: 'これを廃棄し、場にある札と同じ札を 1 枚獲得する。この対局では、コスト 3 以上を獲得するとき、代わりに化け子と取り替えてよい',
    *play(g, p, pi) {
      yield* trashSelf(g, p, 'fairychild');
      const names = [...new Set(g.playArea)].filter((id) => g.supply[id] > 0);
      if (!names.length) return;
      const [i] = yield* askCards(g, pi, '獲得する札（場にあるもの）', names, 1, 1);
      yield* gain(g, pi, names[i ?? 0]);
    } },
  { id: 'simpleton', name: '愚者', types: FATE, cost: 3, main: '恵みを 3 つ', desc: '森の迷子を持っていなければそれを受け、恵みを 3 つめくって好きな順に受ける',
    *play(g, p, pi) {
      if (p.states.includes('s_lost')) return;
      takeState(g, pi, 's_lost');
      const got = [drawFrom(g, pileFor(g, 'boons')), drawFrom(g, pileFor(g, 'boons')), drawFrom(g, pileFor(g, 'boons'))].filter(Boolean);
      while (got.length) {
        const [i] = yield* askCards(g, pi, '次に受ける恵み', got, 1, 1);
        const b = got.splice(i ?? 0, 1)[0];
        yield* receiveBoon(g, pi, b);
        pileFor(g, 'boons').discard.push(b);
      }
    } },
  { id: 'emptytown', name: 'ゴーストタウン', types: ND, cost: 3, main: '次の手番に\n+1 カード +1 アクション', desc: '獲得したとき手札に入れる',
    *play(g, p) { later(g, 'emptytown', function* () { drawCards(p, 1); g.turn.actions += 1; }); },
    *onGain(g, got) { yield* relocate(g, got, 'hand'); } },
  { id: 'goblin', name: 'レプラコーン', types: DOOM, cost: 3, main: '金貨を獲得', desc: '場の札がちょうど 7 枚なら願いを獲得。そうでなければ呪詛を受ける',
    *play(g, p, pi) { yield* gain(g, pi, 'gold'); if (g.playArea.length === 7) yield* gain(g, pi, 'wish2'); else yield* receiveHex(g, pi); } },
  { id: 'firewatch', name: '夜警', types: N, cost: 3, main: '上 5 枚を見る', desc: '山札の上 5 枚を見て、好きな枚数捨て、残りを好きな順に戻す。獲得したとき手札に入れる',
    *play(g, p, pi) {
      const seen = reveal(p, 5);
      const idx = yield* askCards(g, pi, '捨てる札（好きな枚数）', seen, 0, seen.length);
      yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)), true);
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    },
    *onGain(g, got) { yield* relocate(g, got, 'hand'); } },
  { id: 'hiddencave', name: '秘密の洞窟', types: ['action', 'duration'], cost: 3, main: '+1 カード\n+1 アクション', desc: '手札を 3 枚捨ててよい。そうしたら次の手番の始めに +3 金',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      if (p.hand.length < 3 || !(yield* askYesNo(g, pi, '手札を 3 枚捨てて、次の手番に +3 金にしますか？', 'する', 'しない'))) return;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚', 3, 3)));
      later(g, 'hiddencave', function* () { g.turn.money += 3; });
    } },
  // ---- コスト 4 ----
  { id: 'minstrel', name: '詩人', types: FATE, cost: 4, main: '+2 金\n恵みを受ける', desc: '', *play(g, p, pi) { g.turn.money += 2; yield* receiveBoon(g, pi); } },
  { id: 'luckyvillage', name: '恵みの村', types: FATE, cost: 4, main: '+1 カード\n+2 アクション', desc: '獲得したとき、恵みをめくり、今か次の手番の始めに受ける',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; },
    *onGain(g, got) {
      const b = drawFrom(g, pileFor(g, 'boons'));
      if (!b) return;
      pileFor(g, 'boons').discard.push(b);
      if (yield* askYesNo(g, got.pi, `${nm(b)}をいつ受けますか？`, '今', '次の手番の始め', [b])) yield* receiveBoon(g, got.pi, b);
      else g.players[got.pi].nextTurn.push(function* (gg, pp, ppi) { yield* receiveBoon(gg, ppi, b); });
    } },
  { id: 'graveyard', name: '墓地', types: ['victory'], cost: 4, points: 2, main: '2 点', desc: '獲得したとき、手札を 4 枚まで廃棄する',
    *onGain(g, got) { const p = g.players[got.pi]; yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, got.pi, '廃棄する札（4 枚まで）', 0, 4))); } },
  { id: 'secretcouncil', name: 'コンクラーベ', cost: 4, main: '+2 金', desc: '場にないアクションを手札から 1 枚使ってよい。そうしたら +1 アクション',
    *play(g, p, pi) {
      g.turn.money += 2;
      const [i] = yield* askHand(g, pi, '使うアクション（場にないもの・なしでもよい）', 0, 1, (id) => is(id, 'action') && !g.playArea.includes(id));
      if (i == null) return;
      yield* playFrom(g, pi, takeFromHand(p, [i])[0]);
      g.turn.actions += 1;
    } },
  { id: 'demonforge', name: '悪魔の工房', types: N, cost: 4, main: '獲得した数で決まる', desc: 'この手番に獲得した札が 2 枚以上ならインプ、1 枚ならコスト 4 以下、0 枚なら金貨を獲得する',
    *play(g, p, pi) {
      const n = g.turn.gained.length;
      if (n >= 2) yield* gain(g, pi, 'imp2');
      else if (n === 1) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4));
      else yield* gain(g, pi, 'gold');
    } },
  { id: 'purifier', name: '悪魔祓い', types: N, cost: 4, main: '廃棄して精霊', desc: '手札を 1 枚廃棄し、それより安い精霊（ウィル・オ・ウィスプ・インプ・幽霊）を獲得する',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id);
      const opts = ['wisp', 'imp2', 'phantom'].filter((s) => g.nonSupply[s] > 0 && CARDS[s].cost < c);
      if (!opts.length) return;
      const [k] = yield* askCards(g, pi, '獲得する精霊', opts, 1, 1);
      yield* gain(g, pi, opts[k ?? 0]);
    } },
  { id: 'deadcaller', name: 'ネクロマンサー', cost: 4, main: '廃棄置き場の\nアクションを使う', desc: '廃棄置き場の持続でないアクションを 1 つ使う（札は廃棄置き場に残り、この手番は裏向き）。はじめ廃棄置き場に屍 3 枚',
    *play(g, p, pi) {
      g.turn.usedDead = g.turn.usedDead || [];
      const opts = [...new Set(g.trash.filter((id) => is(id, 'action') && !is(id, 'duration')))].filter((id) => !g.turn.usedDead.includes(id));
      if (!opts.length) return;
      const [i] = yield* askCards(g, pi, '使う札（廃棄置き場から）', opts, 1, 1);
      const id = opts[i ?? 0];
      g.turn.usedDead.push(id);
      log(g, `${p.name}が廃棄置き場の${nm(id)}を使う。`);
      yield* resolve(g, id);
    } },
  { id: 'herdsman', name: '羊飼い', cost: 4, main: '+1 アクション', desc: '勝利点カードを好きな枚数見せて捨て、1 枚につき +2 カード',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const idx = yield* askHand(g, pi, '捨てる勝利点カード（好きな枚数）', 0, p.hand.length, (id) => is(id, 'victory'));
      yield* discardCards(g, p, takeFromHand(p, idx));
      drawCards(p, 2 * idx.length);
    } },
  { id: 'sneak', name: '暗躍者', types: ['action', 'attack', 'doom'], cost: 4, main: '+1 購入', desc: '他の人は次の呪詛を受ける。獲得したとき金貨を獲得する',
    *play(g) {
      g.turn.buys += 1;
      const h = drawFrom(g, pileFor(g, 'hexes'));
      if (!h) return;
      yield* attackOthers(g, function* (ti) { yield* receiveHex(g, ti, h); });
      pileFor(g, 'hexes').discard.push(h);
    },
    *onGain(g, got) { yield* gain(g, got.pi, 'gold'); } },
  // ---- コスト 5 ----
  { id: 'shoemender', name: 'カブラー', types: ND, cost: 5, main: '次の手番に\n手札へ獲得', desc: '次の手番の始めに、コスト 4 以下を手札に獲得する',
    *play(g, p, pi) { later(g, 'shoemender', function* () { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を手札に獲得', 4), 'hand'); }); } },
  { id: 'tombchamber', name: '納骨堂', types: ND, cost: 5, main: '財宝をしまって\n毎手番 1 枚', desc: '場の財宝を好きな枚数脇に置く。残っているあいだ、手番の始めにその 1 枚を手札に入れる',
    *play(g, p, pi) {
      const tr = g.playArea.filter((id) => is(id, 'treasure'));
      const idx = yield* askCards(g, pi, '脇に置く財宝（好きな枚数）', tr, 0, tr.length);
      if (!idx.length) return;
      const kept = idx.map((i) => tr[i]);
      for (const id of kept) g.playArea.splice(g.playArea.indexOf(id), 1);
      (p.mats.tombchamber = p.mats.tombchamber || []).push(...kept);
      const job = function* () {
        if (!kept.length) return;
        const [k] = yield* askCards(g, pi, '石室から手札に入れる 1 枚', kept, 1, 1);
        const id = kept.splice(k ?? 0, 1)[0];
        p.mats.tombchamber.splice(p.mats.tombchamber.indexOf(id), 1);
        p.hand.push(id);
        if (kept.length) later(g, 'tombchamber', job);
      };
      later(g, 'tombchamber', job);
    } },
  { id: 'hauntedvillage', name: '呪われた村', types: DOOM, cost: 5, main: '+2 アクション\n6 枚まで引く', desc: '手札が 6 枚になるまで引く。獲得したとき、呪詛を受ける',
    *play(g, p) { g.turn.actions += 2; drawCards(p, Math.max(0, 6 - p.hand.length)); },
    *onGain(g, got) { yield* receiveHex(g, got.pi); } },
  { id: 'rookery', name: '悪人のアジト', types: ND, cost: 5, main: '次の手番に\n+2 カード', desc: '獲得したとき手札に入れる',
    *play(g, p) { later(g, 'rookery', function* () { drawCards(p, 2); }); },
    *onGain(g, got) { yield* relocate(g, got, 'hand'); } },
  { id: 'figurine', name: '偶像', types: ['treasure', 'attack', 'fate'], cost: 5, value: 2, main: '+2 金', desc: '場の偶像が奇数枚なら恵みを受け、偶数枚なら他の人は呪いを獲得する',
    *play(g, p, pi) {
      if (g.playArea.filter((id) => id === 'figurine').length % 2) yield* receiveBoon(g, pi);
      else yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    } },
  { id: 'phantomhorse', name: 'プーカ', cost: 5, main: '財宝を廃棄して\n+4 カード', desc: '祟り金以外の財宝を手札から 1 枚廃棄してよい。そうしたら +4 カード',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄する財宝（しなくてもよい）', 0, 1, (id) => is(id, 'treasure') && id !== 'cursedcoin');
      if (i == null) return;
      yield* trashCards(g, p, takeFromHand(p, [i]));
      drawCards(p, 4);
    } },
  { id: 'holygrove', name: '聖なる木立ち', types: FATE, cost: 5, main: '+1 購入\n+3 金', desc: '恵みを受ける。それが +1 金の恵みでなければ、他の人もそれを受けてよい',
    *play(g, p, pi) {
      g.turn.buys += 1; g.turn.money += 3;
      const b = drawFrom(g, pileFor(g, 'boons'));
      if (!b) return;
      yield* receiveBoon(g, pi, b);
      if (b !== 'b_field' && b !== 'b_forest') {
        yield* eachOther(g, function* (ti) { if (yield* askYesNo(g, ti, `${nm(b)}を受けますか？`, '受ける', '受けない', [b])) yield* receiveBoon(g, ti, b); });
      }
      pileFor(g, 'boons').discard.push(b);
    } },
  { id: 'bully', name: '迫害者', types: ['action', 'attack', 'doom'], cost: 5, main: '+2 金', desc: '場にほかの札がなければインプを獲得する。あれば、他の人は次の呪詛を受ける',
    *play(g, p, pi) {
      g.turn.money += 2;
      if (g.playArea.length === 1) { yield* gain(g, pi, 'imp2'); yield* attackOthers(g, function* () {}); return; }
      const h = drawFrom(g, pileFor(g, 'hexes'));
      if (!h) return;
      yield* attackOthers(g, function* (ti) { yield* receiveHex(g, ti, h); });
      pileFor(g, 'hexes').discard.push(h);
    } },
  { id: 'doomedhero', name: '悲劇のヒーロー', cost: 5, main: '+3 カード\n+1 購入', desc: '引いたあと手札が 8 枚以上なら、これを廃棄して財宝を獲得する',
    *play(g, p, pi) {
      drawCards(p, 3); g.turn.buys += 1;
      if (p.hand.length >= 8 && (yield* trashSelf(g, p, 'doomedhero'))) yield* gain(g, pi, yield* askSupply(g, pi, '財宝を獲得', 99, (id) => is(id, 'treasure')));
    } },
  { id: 'bloodsucker', name: '吸血鬼', types: ['night', 'attack', 'doom'], cost: 5, main: '呪詛と獲得', desc: '他の人は次の呪詛を受ける。コスト 5 以下の（吸血鬼以外の）札を獲得し、これをコウモリと取り替える',
    *play(g, p, pi) {
      const h = drawFrom(g, pileFor(g, 'hexes'));
      if (h) { yield* attackOthers(g, function* (ti) { yield* receiveHex(g, ti, h); }); pileFor(g, 'hexes').discard.push(h); }
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を獲得', 5, (id) => id !== 'bloodsucker'));
      if (g.nonSupply.nightwing > 0 && returnToPile(g, 'bloodsucker')) { g.nonSupply.nightwing -= 1; p.discard.push('nightwing'); log(g, `${p.name}が吸血鬼をコウモリと取り替えた。`); }
    } },
  { id: 'wolfman', name: '人狼', types: ['action', 'night', 'attack', 'doom'], cost: 5, main: '昼 +3 カード\n夜 呪詛', desc: '夜のフェイズなら他の人は次の呪詛を受ける。そうでなければ +3 カード',
    *play(g, p) {
      if (g.turn.phase !== 'night') { drawCards(p, 3); return; }
      const h = drawFrom(g, pileFor(g, 'hexes'));
      if (!h) return;
      yield* attackOthers(g, function* (ti) { yield* receiveHex(g, ti, h); });
      pileFor(g, 'hexes').discard.push(h);
    } },
  // ---- コスト 6 ----
  { id: 'nightthief', name: '夜襲', types: ['night', 'duration', 'attack'], cost: 6, main: '次の手番に\n+3 金', desc: '手札が 5 枚以上の他の人は、あなたの場にある札と同じ札を 1 枚捨てる（なければ手札を見せる）',
    *play(g) {
      const inPlay = new Set(g.playArea);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 5) return;
        const [i] = yield* askHand(g, ti, '捨てる 1 枚（場にある札と同じもの）', 1, 1, (id) => inPlay.has(id));
        if (i != null) yield* discardCards(g, t, takeFromHand(t, [i])); else log(g, `${t.name}は手札を見せた。`);
      });
      later(g, 'nightthief', function* () { g.turn.money += 3; });
    } },
];

// ---- 決まり ----
const HEIRLOOM = { graveyard: 'dimmirror', simpleton: 'luckycoin', sprite: 'kid', phantomhorse: 'cursedcoin', hiddencave: 'wishlamp', herdsman: 'grazing', trailer: 'purse' };
HOOKS.setup.push((g) => {
  const k = g.kingdom;
  const uses = (t) => k.some((id) => is(id, t));
  if (uses('fate')) { g.boons = { deck: shuffle(boons.map((b) => b.id), g), discard: [] }; }
  if (uses('doom')) g.hexes = { deck: shuffle(hexes.map((h) => h.id), g), discard: [] };
  if (k.includes('druid') && g.boons) g.druidBoons = g.boons.deck.splice(-3);
  if (g.boons && boons.length) g.nonSupply.wisp = 12;
  if (k.includes('bully') || k.includes('demonforge')) g.nonSupply.imp2 = 13;
  if (k.includes('purifier')) { g.nonSupply.wisp = 12; g.nonSupply.imp2 = 13; g.nonSupply.phantom = 6; }
  if (k.includes('graveyard')) g.nonSupply.phantom = 6;
  if (k.includes('goblin') || k.includes('hiddencave')) g.nonSupply.wish2 = 12;
  if (k.includes('bloodsucker')) g.nonSupply.nightwing = 10;
  if (k.includes('deadcaller')) g.trash.push('z_apprentice', 'z_mason', 'z_spy');
  // 家宝: 初めのデッキの銅貨 1 枚と入れ替える
  for (const [card, h] of Object.entries(HEIRLOOM)) {
    if (!k.includes(card)) continue;
    for (const p of g.players) {
      const inHand = p.hand.indexOf('copper');
      if (inHand >= 0 && rng(g) < 0.5) p.hand[inHand] = h;
      else { const i = p.deck.indexOf('copper'); if (i >= 0) p.deck[i] = h; else if (inHand >= 0) p.hand[inHand] = h; }
    }
  }
});
// 化け子: この対局では、コスト 3 以上を獲得するとき、化け子と取り替えてよい
HOOKS.gain.push(function* (g, got) {
  if (!g.kingdom.includes('fairychild') || got.id === 'fairychild' || !(g.supply.fairychild > 0) || costOf(g, got.id) < 3) return;
  if (got.to === 'gone' || got.to === 'trash') return;
  if (!(yield* askYesNo(g, got.pi, `${nm(got.id)}を化け子と取り替えますか？`, '取り替える', 'しない', [got.id, 'fairychild']))) return;
  if (!(yield* relocate(g, got, 'gone'))) return;
  if (!returnCard(g, got.id)) { g.players[got.pi].discard.push(got.id); return; }
  g.supply.fairychild -= 1;
  g.players[got.pi].discard.push('fairychild');
  log(g, `${g.players[got.pi].name}が${nm(got.id)}を化け子と取り替えた。`);
});
// 森の迷子: 手番の始めに手札を捨てて恵み
HOOKS.turnStart.push(function* (g, p, pi) {
  if (!p.states.includes('s_lost') || !g.boons || !p.hand.length) return;
  const [i] = yield* askHand(g, pi, '森の迷子: 1 枚捨てて恵みを受けてよい', 0, 1);
  if (i == null) return;
  yield* discardCards(g, p, takeFromHand(p, [i]));
  yield* receiveBoon(g, pi);
});
// 錯乱・嫉妬: 購入フェイズの始めに返し、その手番だけ効く
HOOKS.buyPhase.push(function* (g) {
  const p = currentPlayer(g);
  if (p.states.includes('s_deluded')) { g.turn.noBuyActions = true; p.states = p.states.filter((s) => s !== 's_deluded'); log(g, `${p.name}は錯乱で、この手番アクションを買えない。`); }
  if (p.states.includes('s_envious')) { g.turn.envious = true; p.states = p.states.filter((s) => s !== 's_envious'); log(g, `${p.name}は嫉妬で、この手番の銀貨と金は 1 金。`); }
});
// 番の犬: 手番の終わりに手札へ戻す
HOOKS.afterCleanup.push(function* (g) { for (const q of g.players) if (q.mats.loyaldog && q.mats.loyaldog.length) q.hand.push(...q.mats.loyaldog.splice(0)); });

defineCards({ id: 'nocturne', name: '夜想曲' }, [...kingdom, ...heirlooms, ...others, ...boons, ...hexes, ...states], [
  { id: 'dance', name: '夜の踊り', cards: ['druid', 'sprite', 'trailer', 'simpleton', 'minstrel', 'luckyvillage', 'holygrove', 'figurine', 'hiddencave', 'emptytown'] },
  { id: 'nightshift', name: '夜番', cards: ['protector', 'priory', 'firewatch', 'demonforge', 'purifier', 'shoemender', 'tombchamber', 'rookery', 'nightthief', 'fairychild'] },
  { id: 'monstermash', name: 'もののけ騒ぎ', cards: ['goblin', 'sneak', 'hauntedvillage', 'bully', 'bloodsucker', 'wolfman', 'deadcaller', 'loyaldog', 'herdsman', 'phantomhorse'] },
]);
