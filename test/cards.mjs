// カードごとの決まった場面のチェック。 node test/cards.mjs
import assert from 'node:assert/strict';
import { CARDS, newGame, playAction, score, startBuyPhase, playTreasure, buyCard, finalResults } from '../engine.js';
import '../cards-base.js';

const K = ['warehouse', 'moat', 'village', 'command', 'sentinel', 'sorcerer', 'meadow', 'official', 'highwayman', 'moneylender'];
function setup(hand, deck = []) {
  const g = newGame(2, K);
  g.players[0].hand = [...hand];
  g.players[0].deck = [...deck];
  g.players[0].discard = [];
  return g;
}
// 答えを順に返して最後まで回す。出た問いを返す
function run(gen, answers = []) {
  const qs = [];
  let s = gen.next();
  while (!s.done) { qs.push(s.value); s = gen.next(answers.shift()); }
  return qs;
}

// 号令＋集落: +2 カード +4 アクション（号令で1使うので 4）
let g = setup(['command', 'village', 'copper'], ['estate', 'estate', 'estate']);
run(playAction(g, 'command'), [[0]]);
assert.equal(g.turn.actions, 4);
assert.equal(g.players[0].hand.length, 3);

// 呪術師: 相手が災いを得る。水濠を持っていれば防ぐ
g = setup(['sorcerer'], ['copper', 'copper']);
g.players[1].hand = ['moat', 'copper'];
run(playAction(g, 'sorcerer'));
assert.equal(g.players[1].discard.includes('curse'), false);
g = setup(['sorcerer'], ['copper', 'copper']);
g.players[1].hand = ['copper'];
run(playAction(g, 'sorcerer'));
assert.ok(g.players[1].discard.includes('curse'));

// 番兵: 2 枚とも戻して、選んだ方が一番上
g = setup(['sentinel'], ['gold', 'estate', 'copper']); // 末尾が一番上: copper を引き、estate・gold を見る
run(playAction(g, 'sentinel'), ['keep', 'keep', [1]]); // 見た順 [estate, gold] の 1=gold を上に
assert.deepEqual(g.players[0].deck.slice(-2), ['estate', 'gold']);

// 花畑: 20 枚なら 2 点ずつ
g = setup([]);
const p = g.players[0];
p.deck = [...Array(18).fill('copper'), 'meadow', 'meadow'];
assert.equal(score(p), 4);

// 徴税官: 相手は小屋を山札の上に戻す（1 種類しかないので問わない）
g = setup(['official']);
g.players[1].hand = ['estate', 'copper', 'estate'];
const qs = run(playAction(g, 'official'));
assert.equal(qs.length, 0);
assert.equal(g.players[1].deck.at(-1), 'estate');
assert.equal(g.players[0].deck.at(-1), 'silver');

// 追いはぎ: 銀と金なら相手が選ぶ。選ばれた方が廃棄
g = setup(['highwayman']);
g.players[1].deck = ['silver', 'gold'];
const q2 = run(playAction(g, 'highwayman'), [[1]]);
assert.equal(q2[0].player, 1);
assert.deepEqual(g.trash, [q2[0].cards[1]]);

// 両替商 2 枚で最初の銀が +2、次の銀は +0
g = setup(['moneylender', 'moneylender', 'silver', 'silver'], ['estate', 'estate']);
g.turn.actions = 2;
run(playAction(g, 'moneylender')); run(playAction(g, 'moneylender'));
startBuyPhase(g); playTreasure(g, 'silver'); playTreasure(g, 'silver');
assert.equal(g.turn.money, 6);
let b = buyCard(g, 'gold'), bs = b.next(); while (!bs.done) bs = b.next();
assert.ok(bs.value);

// 同点・同手番なら同じ順位
g = newGame(2, K);
const r = finalResults(g);
assert.equal(r[0].rank, 1); assert.equal(r[1].rank, 1);
console.log('ok: cards');

// ---- 陰謀 ----
await import('../cards-intrigue.js');
const { costOf } = await import('../engine.js');
const K2 = ['carnival', 'suspension', 'plotter', 'envoy', 'mansion', 'marquis', 'jailer', 'refine', 'tunnel', 'moat'];
function setup2(hand, deck = []) {
  const g = newGame(2, K2);
  Object.assign(g.players[0], { hand: [...hand], deck: [...deck], discard: [] });
  return g;
}
// つり橋 2 枚で領地が 6
g = setup2(['suspension', 'suspension']); g.turn.actions = 2;
run(playAction(g, 'suspension')); run(playAction(g, 'suspension'));
assert.equal(costOf(g, 'province'), 6); assert.equal(g.turn.buys, 3);
// 仮装行列: 1 枚ずつ左へ
g = setup2(['carnival', 'gold'], ['estate', 'estate']);
g.players[1].hand = ['curse'];
run(playAction(g, 'carnival'), [[0], []]);
assert.ok(g.players[1].hand.includes('gold')); assert.ok(g.players[0].hand.includes('curse'));
// 使節のリアクション: 牢番に見せて 2 引き 3 捨て、そのあと牢番の選択
g = setup2(['jailer'], ['copper', 'copper', 'copper']);
g.players[1].hand = ['envoy', 'copper', 'copper', 'copper', 'estate'];
g.players[1].deck = ['silver', 'silver'];
const q3 = run(playAction(g, 'jailer'), [true, [1, 2, 3], 'curse']);
assert.equal(q3[0].player, 1);
assert.equal(g.players[1].hand.length, 5); // 5+2-3+災い1
assert.ok(g.players[1].hand.includes('curse'));
// 豪邸・侯爵の点
g = setup2([]);
g.players[0].deck = ['mansion', 'marquis', 'duchy', 'duchy'];
g.players[0].discard = [];
assert.equal(score(g.players[0]), 2 + 2 + 6);
// 黒幕: 3 回目なら +1 カード +1 アクション
g = setup2(['plotter'], ['copper']); g.turn.actionsPlayed = 2;
run(playAction(g, 'plotter'));
assert.equal(g.turn.actions, 1); assert.equal(g.turn.money, 2);
console.log('ok: intrigue');

// ---- 海辺 ----
await import('../cards-seaside.js');
const { beginTurn, endTurn } = await import('../engine.js');
const K3 = ['wagon', 'fort', 'beacon', 'coffer', 'privateer', 'sorcerer', 'command', 'cove', 'islet', 'pier'];
function setup3(hand, deck = []) {
  const g = newGame(2, K3);
  Object.assign(g.players[0], { hand: [...hand], deck: [...deck], discard: [] });
  return g;
}
const rest = (g) => { run(endTurn(g)); run(beginTurn(g)); };
// 荷馬車: 場に残り、次の手番の始めに +1 カード、その手番の終わりに捨て札へ
g = setup3(['wagon'], Array(20).fill('copper'));
run(playAction(g, 'wagon'));
run(endTurn(g));
assert.deepEqual(g.players[0].inPlay, ['wagon']);
rest(g); // 相手の手番を終えて自分へ
run(beginTurn(g)); // （rest で相手の beginTurn を回したので、ここで自分の分）
assert.equal(g.players[0].hand.length, 6);
run(endTurn(g));
assert.equal(g.players[0].inPlay.length, 0);
assert.ok(g.players[0].discard.includes('wagon'));
// 出城: 追加の手番は同じ人、手札 3 枚。追加の手番では続かない
g = setup3(['fort'], Array(20).fill('copper'));
run(playAction(g, 'fort'));
run(endTurn(g));
assert.equal(g.current, 0); assert.equal(g.players[0].hand.length, 3); assert.ok(g.extraTurn);
run(beginTurn(g));
run(endTurn(g));
assert.equal(g.current, 1);
// かがり火: 場にあるあいだアタックを受けない
g = setup3(['beacon'], Array(10).fill('copper'));
run(playAction(g, 'beacon'));
run(endTurn(g));
g.players[1].hand = ['sorcerer'];
run(beginTurn(g));
run(playAction(g, 'sorcerer'));
assert.ok(!allCardsOf(g.players[0]).includes('curse'));
function allCardsOf(p) { return [...p.deck, ...p.hand, ...p.discard]; }
// 号令＋荷馬車: 2 回分 +1 カード、号令も場に残る
g = setup3(['command', 'wagon'], Array(20).fill('copper'));
run(playAction(g, 'command'), [[0]]);
run(endTurn(g));
assert.deepEqual(g.players[0].inPlay.sort(), ['command', 'wagon']);
// 私掠船: 相手は最初に出した銀を廃棄
g = setup3(['privateer'], Array(10).fill('copper'));
run(playAction(g, 'privateer'));
run(endTurn(g));
run(beginTurn(g));
g.players[1].hand = ['silver', 'silver'];
startBuyPhase(g); playTreasure(g, 'silver'); playTreasure(g, 'silver');
assert.equal(g.turn.money, 4); assert.deepEqual(g.trash, ['silver']);
// 小島: マットに置いて点に数える
g = setup3(['islet', 'province'], Array(10).fill('copper'));
run(playAction(g, 'islet'));
assert.deepEqual(g.players[0].mats.islet, ['islet', 'province']);
assert.ok(score(g.players[0]) >= 8);
console.log('ok: seaside');

// ---- 繁栄 ----
await import('../cards-prosperity.js');
const { canBuy, playAllTreasures } = await import('../engine.js');
const K4 = ['charlatan', 'hawker', 'firetower', 'council', 'banker', 'stele', 'stash', 'boulevard', 'village', 'smithy'];
function setup4(hand, deck = [], opts = { colony: true }) {
  const g = newGame(2, K4, null, opts);
  Object.assign(g.players[0], { hand: [...hand], deck: [...deck], discard: [] });
  return g;
}
// 新天地・白金の山、まやかし師で災いが財宝
g = setup4(['curse', 'copper', 'banker']);
assert.equal(g.supply.colony, 8); assert.equal(g.supply.platinum, 12);
startBuyPhase(g); playAllTreasures(g);
assert.equal(g.turn.money, 1 + 1 + 3);
// 呼び売り: 場のアクション 2 枚で 4 下がる（購入フェイズだけ）
g = setup4(['village', 'smithy'], Array(10).fill('copper'));
run(playAction(g, 'village')); run(playAction(g, 'smithy'));
assert.equal(costOf(g, 'hawker'), 8);
startBuyPhase(g);
assert.equal(costOf(g, 'hawker'), 4);
// 大通り: 銅を出していると買えない
g.turn.money = 10; g.playArea.push('copper');
assert.equal(canBuy(g, 'boulevard'), false);
// 御前会議＋石碑: +6 金 +3 点
g = setup4(['council', 'stele']);
run(playAction(g, 'council'), [[0]]);
assert.equal(g.turn.money, 6); assert.equal(g.players[0].tokens.vp, 3);
// 火の見やぐら: 獲得した銀を山札の上へ
g = setup4(['firetower']);
startBuyPhase(g); g.turn.money = 3;
run(buyCard(g, 'silver'), ['deck']);
assert.equal(g.players[0].deck.at(-1), 'silver');
// 新天地の山が空になると終わり
g = setup4([]);
g.supply.colony = 0;
run(endTurn(g));
assert.ok(g.over);
console.log('ok: prosperity');

// ---- 異郷 ----
await import('../cards-hinterlands.js');
const K5 = ['silverdealer', 'gatevillage', 'underpass', 'pyrite', 'warehouse', 'fields', 'causeway', 'watchdog', 'mercenary', 'drifter'];
function setup5(hand, deck = []) {
  const g = newGame(2, K5, null, { colony: false });
  Object.assign(g.players[0], { hand: [...hand], deck: [...deck], discard: [] });
  return g;
}
// 銀の商人: 買った関所の村の代わりに銀
g = setup5(['silverdealer']);
startBuyPhase(g); g.turn.money = 6;
run(buyCard(g, 'gatevillage'), ['silver', true]); // 関所の村の獲得時の効果（銀）→ 銀の商人で交換
assert.equal(g.supply.gatevillage, 10); assert.deepEqual(g.players[0].discard, ['silver', 'silver']);
// 関所の村: 獲得したら安いものも
g = setup5([]);
startBuyPhase(g); g.turn.money = 6;
run(buyCard(g, 'gatevillage'), ['drifter']);
assert.deepEqual(g.players[0].discard.sort(), ['drifter', 'gatevillage']);
assert.equal(g.turn.money, 2); // 流れ者を獲得して +2
// 地下道: 倉庫で捨てたら金
g = setup5(['warehouse', 'underpass'], ['copper']);
run(playAction(g, 'warehouse'), [[0], true]);
assert.ok(g.players[0].discard.includes('gold'));
// にせ金: 相手が領地を獲得したら廃棄して金を山札の上
g = setup5([]);
g.players[1].hand = ['pyrite', 'copper'];
startBuyPhase(g); g.turn.money = 8;
run(buyCard(g, 'province'), [true]);
assert.equal(g.players[1].deck.at(-1), 'gold'); assert.ok(g.trash.includes('pyrite'));
// にせ金 3 枚: 1 + 4 + 4
g = setup5(['pyrite', 'pyrite', 'pyrite']);
startBuyPhase(g); playAllTreasures(g);
assert.equal(g.turn.money, 9);
// 見張り犬: 傭兵の前に使って 4 枚引く（手札 5 枚以下なので）
g = setup5(['mercenary']);
g.players[1].hand = ['watchdog', 'copper', 'copper'];
g.players[1].deck = Array(6).fill('estate');
run(playAction(g, 'mercenary'), [true, [0, 1, 2]]);
assert.equal(g.players[1].hand.length, 3); assert.deepEqual(g.players[1].inPlay, ['watchdog']);
console.log('ok: hinterlands');

// ---- 収穫祭＆ギルド ----
await import('../cards-guilds.js');
const { spendCoffers } = await import('../engine.js');
const K6 = ['apprentice', 'duel', 'breadmaker', 'shoer', 'gem', 'mugger', 'ferry', 'sideshow', 'expo', 'tourney'];
g = newGame(2, K6, null, { colony: false });
assert.ok(g.bane && g.supply[g.bane] > 0);
assert.equal(g.players[1].tokens.coffers, 1);
assert.equal(g.nonSupply.courser, 2); assert.equal(g.nonSupply.steed, 1);
assert.ok(g.ferryPile && g.nonSupply[g.ferryPile] > 0);
// 過払い: 逸品に 3 払って銀 3 枚
Object.assign(g.players[0], { hand: [], deck: [], discard: [] });
startBuyPhase(g); g.turn.money = 6;
run(buyCard(g, 'gem'), [3]);
assert.equal(g.players[0].discard.filter((x) => x === 'silver').length, 3);
// 財源を使う
spendCoffers(g, 1);
assert.equal(g.turn.money, 1); assert.equal(g.players[0].tokens.coffers, 0);
// 見習い魔女: 厄よけを見せると災いを受けない
g.players[0].hand = ['apprentice']; g.players[0].deck = ['copper', 'copper'];
g.turn = { ...g.turn, phase: 'action', actions: 1 };
g.players[1].hand = [g.bane];
run(playAction(g, 'apprentice'));
assert.ok(![...g.players[1].discard, ...g.players[1].hand].includes('curse'));
// 博覧会: 10 種で 4 点
assert.equal(CARDS.expo.pointsFn(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']), 4);
console.log('ok: guilds');

// ---- 錬金術 ----
await import('../cards-alchemy.js');
const K7 = ['takeover', 'adept', 'remodel', 'vinerack', 'arcanestone', 'village', 'smithy', 'market', 'moat', 'cellar'].filter((id) => CARDS[id]);
g = newGame(3, K7, null, { colony: false });
assert.equal(g.supply.potion, 16);
// 霊薬がないとポーションの札は買えない
startBuyPhase(g); g.turn.money = 10;
assert.equal(canBuy(g, 'adept'), false);
g.players[0].hand = ['potion']; playAllTreasures(g);
assert.ok(canBuy(g, 'adept'));
// 乗っ取り: 1 人目が使うと、2 人目の追加の手番を 1 人目が操作する
g = newGame(3, K7, null, { colony: false });
g.players[0].hand = ['takeover'];
run(playAction(g, 'takeover'));
run(endTurn(g));
assert.equal(g.current, 1); assert.equal(g.controller, 0);
g.players[1].hand = ['remodel', 'gold'];
const qs7 = run(playAction(g, 'remodel'), [[0], 'province']);
assert.equal(qs7.length === 0 || qs7.every((q) => q.player === 0 && q.owner === 1), true);
assert.ok(g.players[0].discard.includes('province')); // 獲得は操作した人へ
assert.ok(g.players[1].mats.possessed.includes('gold')); // 廃棄は脇へ
const turns1 = g.players[1].turnsTaken;
run(endTurn(g));
assert.equal(g.current, 1); assert.equal(g.controller, null); // 次は 2 人目のふつうの手番
assert.ok(g.players[1].discard.includes('gold'));
assert.equal(g.players[1].turnsTaken, turns1);
console.log('ok: alchemy');

// ---- 暗黒時代 ----
await import('../cards-darkages.js');
const K8 = ['knights', 'zealot', 'stronghold', 'marketsquare', 'recluse', 'fief', 'ravager', 'rats', 'waif', 'impostor'];
g = newGame(3, K8, null, { colony: false, shelters: true });
assert.equal(g.supply.knights, 10); assert.equal(g.stacks.knights.length, 10);
assert.equal(g.supply.ruins, 20); assert.ok(g.players[0].deck.concat(g.players[0].hand).includes('shack'));
// 騎士の山は一番上の札を獲得
const topKnight = g.stacks.knights.at(-1);
Object.assign(g.players[0], { hand: [], deck: [], discard: [] });
startBuyPhase(g); g.turn.money = 5;
run(buyCard(g, 'knights'));
assert.deepEqual(g.players[0].discard, [topKnight]); assert.equal(g.supply.knights, 9);
// 邪教徒: 相手はがれき（重なった山の札）を獲得
g.turn = { ...g.turn, phase: 'action', actions: 1 };
g.players[0].hand = ['zealot']; g.players[0].deck = ['copper', 'copper'];
g.players[1].hand = []; g.players[2].hand = [];
run(playAction(g, 'zealot'));
assert.ok(CARDS[g.players[1].discard.at(-1)].pile === 'ruins');
// 砦: 廃棄すると手札に戻る。広小路で金
g.players[0].hand = ['stronghold', 'marketsquare', 'rats']; g.players[0].deck = ['copper'];
g.turn.actions = 1;
run(playAction(g, 'rats'), [[0], true]); // どぶネズミ: 砦を廃棄 → 広小路を捨てて金
assert.ok(g.players[0].hand.includes('stronghold')); assert.ok(g.players[0].discard.includes('gold'));
// 知行地: 銀 3 枚で 1 点
assert.equal(CARDS.fief.pointsFn(['silver', 'silver', 'silver', 'fief']), 1);
console.log('ok: darkages');

// ---- 冒険 ----
await import('../cards-adventures.js');
const { buyEvent, canBuyEvent } = await import('../engine.js');
const K9 = ['realmcoin', 'lad', 'bridgeogre', 'oldrelic', 'village', 'smithy', 'carriage', 'farland', 'servant', 'harbor'];
const L9 = ['e_errand', 'e_signpost'];
g = newGame(2, K9, null, { colony: false, landscapes: L9 });
Object.assign(g.players[0], { hand: ['realmcoin', 'village'], deck: Array(10).fill('copper'), discard: [] });
// 通用貨: 酒場マットに置き、アクションのあとに呼び出して +2 アクション
startBuyPhase(g); playTreasure(g, 'realmcoin');
assert.deepEqual(g.players[0].mats.tavern, ['realmcoin']);
g.turn.phase = 'action'; g.turn.actions = 1;
run(playAction(g, 'village'), [true]);
assert.equal(g.turn.actions, 4); assert.ok(g.playArea.includes('realmcoin'));
// 小僧 → 探し屋と取り替え
g.players[0].hand = ['lad']; g.turn.actions = 1;
run(playAction(g, 'lad'));
run(endTurn(g), [true]);
assert.ok(g.players[0].discard.includes('seeker')); assert.equal(g.supply.lad, 11); // 山に戻った（テストで手札に置いた分が増える）
// 橋守の鬼: 相手は -1 金の印、自分の手番はコスト 1 下がる
g = newGame(2, K9, null, { colony: false, landscapes: L9 });
g.players[0].hand = ['bridgeogre'];
run(playAction(g, 'bridgeogre'));
assert.equal(costOf(g, 'province'), 7); assert.ok(g.players[1].tokens.minusCoin);
run(endTurn(g)); run(beginTurn(g));
assert.equal(g.turn.money, -1);
// イベント: 道しるべ（+1 カードの印）と使いの旅（追加の手番、買えない）
g = newGame(2, K9, null, { colony: false, landscapes: L9 });
Object.assign(g.players[0], { hand: ['smithy'], deck: Array(20).fill('copper'), discard: [] });
startBuyPhase(g); g.turn.money = 12; g.turn.buys = 2;
run(buyEvent(g, 'e_signpost'), [0]);
run(buyEvent(g, 'e_errand'));
assert.equal(canBuyEvent(g, 'e_errand'), false);
assert.equal(g.players[0].tokens.pile.card, 'servant'); // 並びの最初の山（コストの高い順）
run(endTurn(g));
assert.equal(g.current, 0); assert.ok(g.turn.noBuy);
// 果ての地: 酒場マットにあれば 4 点
assert.equal(CARDS.farland.scoreBonus({ mats: { tavern: ['farland', 'farland'] } }), 8);
console.log('ok: adventures');

// ---- 帝国 ----
await import('../cards-empires.js');
const { payDebt, enterBuyPhase } = await import('../engine.js');
const K10 = ['castles', 'p_settlers', 'townblock', 'villa', 'shrine', 'principal', 'gardener', 'vegmarket', 'temptress', 'mechanic'];
const L10 = ['l_canal', 'l_wall', 'e_unify'];
g = newGame(2, K10, null, { colony: false, landscapes: L10 });
assert.equal(g.stacks.castles.at(-1), 'c_humble'); assert.equal(g.supply.castles, 8);
assert.equal(g.stacks.p_settlers.at(-1), 'colonist'); assert.equal(costOf(g, 'p_settlers'), 2);
assert.equal(g.pileVP.silver, 8);
// 借金: 町並み（借金 8）を買うと借金 8。借金があるあいだは買えず、手番の終わりに残りのお金で返す
Object.assign(g.players[0], { hand: [], deck: Array(10).fill('copper'), discard: [] });
startBuyPhase(g); g.turn.money = 3; g.turn.buys = 2;
run(buyCard(g, 'townblock'));
assert.equal(g.players[0].tokens.debt, 8);
assert.equal(canBuy(g, 'copper'), false);
run(endTurn(g));
assert.equal(g.players[0].tokens.debt, 5);
// 用水路: 銀を獲得すると 1 つ移り、勝利点を獲得すると受け取る
g = newGame(2, K10, null, { colony: false, landscapes: L10 });
startBuyPhase(g); g.turn.money = 11; g.turn.buys = 2;
run(buyCard(g, 'silver')); run(buyCard(g, 'estate'));
assert.equal(g.pileVP.silver, 7); assert.equal(g.players[0].tokens.vp, 1);
// 城壁: 15 枚を超えた分 -1
assert.equal(CARDS.l_wall.score(g, g.players[0], Array(20).fill('copper')), -5);
// 別荘: 購入フェイズに獲得すると手札に入り、アクションフェイズに戻る
g = newGame(2, K10, null, { colony: false, landscapes: [] });
startBuyPhase(g); g.turn.money = 4;
run(buyCard(g, 'villa'));
assert.equal(g.turn.phase, 'action'); assert.ok(g.players[0].hand.includes('villa'));
// 天下統一（イベント 14）: 領地 +9
g = newGame(2, K10, null, { colony: false, landscapes: L10 });
startBuyPhase(g); g.turn.money = 14;
run(buyEvent(g, 'e_unify'));
assert.equal(g.players[0].tokens.vp, 9); // 用水路のトークンは 0 なので領地の獲得では増えない
console.log('ok: empires');

// ---- 夜想曲 ----
await import('../cards-nocturne.js');
const { enterNightPhase, playNight, canPlayNight } = await import('../engine.js');
const K11 = ['trailer', 'minstrel', 'rookery', 'firewatch', 'wolfman', 'bloodsucker', 'hauntedvillage', 'druid', 'herdsman', 'village'];
g = newGame(2, K11, null, { colony: false });
assert.ok(g.boons && g.hexes && g.druidBoons.length === 3);
const all0 = [...g.players[0].deck, ...g.players[0].hand];
assert.ok(all0.includes('purse') && all0.includes('grazing')); assert.equal(all0.filter((x) => x === 'copper').length, 5);
// 悪党の巣窟: 獲得すると手札へ。夜のフェイズに使い、次の手番に +2 カード
Object.assign(g.players[0], { hand: [], deck: Array(20).fill('copper'), discard: [] });
startBuyPhase(g); g.turn.money = 5;
run(buyCard(g, 'rookery'));
assert.deepEqual(g.players[0].hand, ['rookery']);
enterNightPhase(g);
assert.ok(canPlayNight(g, 'rookery'));
run(playNight(g, 'rookery'));
run(endTurn(g));
assert.deepEqual(g.players[0].inPlay, ['rookery']);
// 狼男: 昼は +3 カード、夜は呪詛
g.players[1].hand = ['wolfman']; g.players[1].deck = Array(5).fill('copper');
run(beginTurn(g));
run(playAction(g, 'wolfman'));
assert.equal(g.players[1].hand.length, 3);
// 惑い: 購入フェイズの始めに返し、アクションを買えない
g = newGame(2, K11, null, { colony: false });
g.players[0].states.push('s_deluded');
run(enterBuyPhase(g)); g.turn.money = 5;
assert.equal(canBuy(g, 'village'), false); assert.ok(canBuy(g, 'silver'));
assert.deepEqual(g.players[0].states, []);
// ふしあわせ: -2 点
g.players[0].states.push('s_miserable');
assert.equal(score(g.players[0], g), 3 + 3 - 2); // 小屋 3 点 + 放牧地（小屋 3 枚で 3 点）- ふしあわせ 2
console.log('ok: nocturne');

// ---- ルネサンス ----
await import('../cards-renaissance.js');
const { spendVillager } = await import('../engine.js');
const K12 = ['troupe', 'flagbearer', 'gatekeeper', 'lackeys', 'village', 'smithy', 'market', 'student', 'spices', 'carver'];
const L12 = ['j_barracks', 'j_fleet'];
g = newGame(2, K12, null, { colony: false, landscapes: L12 });
// 旅一座: +4 村人、自分を廃棄。村人で +1 アクション
Object.assign(g.players[0], { hand: ['troupe'], deck: Array(10).fill('copper'), discard: [] });
run(playAction(g, 'troupe'));
assert.equal(g.players[0].tokens.villagers, 4); assert.ok(g.trash.includes('troupe'));
assert.ok(spendVillager(g)); assert.equal(g.turn.actions, 1);
// プロジェクト: 兵営を買うと、次の手番の始めに +1 アクション。2 度は買えない
startBuyPhase(g); g.turn.money = 12; g.turn.buys = 2;
run(buyEvent(g, 'j_barracks'));
assert.equal(canBuyEvent(g, 'j_barracks'), false);
// 旗持ち: 獲得するとのぼり旗を取り、手札を 6 枚引く
run(buyCard(g, 'flagbearer'));
assert.equal(g.artifacts.a_flag, 0);
run(endTurn(g));
assert.equal(g.players[0].hand.length, 6);
run(endTurn(g)); run(beginTurn(g));
assert.equal(g.turn.actions, 2);
// 船団: 終わるとき、持っている人が追加の手番をする
g = newGame(2, K12, null, { colony: false, landscapes: L12 });
g.players[1].projects.push('j_fleet');
g.supply.province = 0;
run(endTurn(g));
assert.equal(g.over, false); assert.equal(g.current, 1);
run(endTurn(g));
assert.equal(g.over, true);
console.log('ok: renaissance');

// ---- 移動動物園 ----
await import('../cards-menagerie.js');
const K13 = ['stablehand', 'bountyman', 'snowvillage', 'beastfair', 'warder', 'village', 'smithy', 'market', 'herddog', 'hoardpile'];
const L13 = ['w_ox', 'm_ride'];
g = newGame(2, K13, null, { colony: false, landscapes: L13 });
assert.equal(g.nonSupply.pony, 30);
// 習性: 鍛冶場を牛のならいで使うと +2 アクション
Object.assign(g.players[0], { hand: ['smithy', 'snowvillage'], deck: Array(10).fill('copper'), discard: [] });
run(playAction(g, 'smithy'), ['w_ox']);
assert.equal(g.turn.actions, 2); assert.equal(g.players[0].hand.length, 1);
// 雪の里: このあとの +アクションは無効
run(playAction(g, 'snowvillage'), [null]);
assert.equal(g.turn.actions, 5);
g.players[0].hand.push('village');
run(playAction(g, 'village'), [null]);
assert.equal(g.turn.actions, 4);
// 懸賞稼ぎ: 追放に同じ札がなければ +3 金
g = newGame(2, K13, null, { colony: false, landscapes: [] });
g.players[0].hand = ['bountyman', 'estate'];
run(playAction(g, 'bountyman'));
assert.deepEqual(g.players[0].mats.exile, ['estate']); assert.equal(g.turn.money, 3);
// 追放の札は、同じ札を獲得したとき捨て札に戻せる
startBuyPhase(g); g.turn.money = 2;
run(buyCard(g, 'estate'), [true]);
assert.deepEqual(g.players[0].mats.exile, []); assert.equal(g.players[0].discard.filter((x) => x === 'estate').length, 2);
// 獣の市: お金の代わりにアクションを廃棄して買える
g = newGame(2, K13, null, { colony: false, landscapes: [] });
g.players[0].hand = ['village'];
startBuyPhase(g);
assert.ok(canBuy(g, 'beastfair'));
run(buyCard(g, 'beastfair'));
assert.ok(g.trash.includes('village')); assert.ok(g.players[0].discard.includes('beastfair'));
console.log('ok: menagerie');

// ---- プロモ ----
await import('../cards-promo.js');
const K14 = ['darkmarket', 'youngload', 'p_sauna', 'fencedvillage', 'village', 'smithy', 'market', 'bugyo', 'borderland', 'dismantle'];
g = newGame(2, K14, null, { colony: false, landscapes: [] });
assert.equal(g.blackMarket.length, 15); assert.equal(g.stacks.p_sauna.at(-1), 'steambath');
// 若殿: 村と一緒に脇に置き、次の手番から毎回使う
Object.assign(g.players[0], { hand: ['youngload', 'village'], deck: Array(20).fill('copper'), discard: [] });
run(playAction(g, 'youngload'), [[0]]);
assert.deepEqual(g.players[0].mats.princed, ['village']); assert.deepEqual(g.players[0].mats.youngload, ['youngload']);
run(endTurn(g)); run(endTurn(g)); run(beginTurn(g));
assert.equal(g.turn.actions, 3); // 村: +2
run(endTurn(g));
assert.deepEqual(g.players[0].mats.princed, ['village']); // また脇へ
console.log('ok: promo');
