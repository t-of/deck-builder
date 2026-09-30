'use strict';
// デッキ構築ゲームのルール・状態（画面・音・localStorage に触らない）。
// カードの定義は cards-*.js が defineCards() で登録する。ここは流れと、カードの効果から使う道具。
//
// カードの効果は play(game, player, pi) というジェネレータ。選択が要るところで「問い」を yield し、
// 呼び出し側（main.js の人の画面、または CPU）が答えを .next(答え) で返す。
// 問いには必ず player（答える人の番号）と owner（誰の札についての問いか）が入る。ふつうは同じ。
// 手番の人以外が答える問い（アタックで捨てる等）もある。乗っ取られた手番では、手番の人の問いに乗っ取った人が答える。
//   { type: 'hand',   player, owner, purpose, min, max, options: [手札の位置...] }  → 手札の位置の配列（owner の手札）
//   { type: 'supply', player, purpose, options: [id...], optional }        → id（optional なら null も可）
//   { type: 'cards',  player, purpose, cards: [id...], min, max }          → cards の位置の配列
//   { type: 'choose', player, purpose, choices: [{ value, label }], cards? } → value
// 玉座の間のような重ねがけは、効果の中から yield* resolve(game, id) を呼ぶ。

export const CARDS = {};
// 遊ぶカードの組（おすすめの 10 種）。{ id, name, set, cards: [...] }
export const PRESETS = [];
// 拡張ごとのまとまり。{ id, name } 並べる順
export const SETS = [];

export function defineCards(setInfo, list, presets = []) {
  if (!SETS.some((s) => s.id === setInfo.id)) SETS.push(setInfo);
  for (const c of list) {
    c.set = c.set || setInfo.id;
    c.types = c.types || ['action'];
    CARDS[c.id] = c;
  }
  PRESETS.push(...presets.map((p) => ({ ...p, set: setInfo.id })));
}

// どのカードにも関わる決まり（拡張が足す）。gain: 誰かが獲得したあと (game, got)、treasure: 財宝を出したあと (game, id)
// setup: 対局を作ったとき (game)。拡張のカードが「このゲームでは…」を決める
// play: 手札からアクションを使う直前 (game, id)
// cost: コストを下げる量を返す (game, id) → 数（ふつうの関数）
// buy: カードを買ったあと・獲得する前 (game, id, pi)
// buyPhase: 購入フェイズの始め (game)。endTurn: 片付けの前 (game)
// afterCleanup: 片付けで 5 枚引いたあと (game, player, pi)。turnStart: 手番の始め、持続のあと (game, player, pi)
// afterAction: 手札のアクションを使い終えたあと (game, id)
export const HOOKS = { gain: [], treasure: [], setup: [], trash: [], play: [], cost: [], buy: [], buyPhase: [], endTurn: [], afterCleanup: [], turnStart: [], afterAction: [] };
// 札がどの山のものか（重なった山の札は山の id）
export const pileOf = (id) => CARDS[id].pile || id;

export const BASIC_IDS = ['copper', 'silver', 'gold', 'platinum', 'potion', 'estate', 'duchy', 'province', 'colony', 'curse'];

export const is = (id, t) => CARDS[id].types.includes(t);
export const isKingdom = (id) => !BASIC_IDS.includes(id) && !CARDS[id].notSupply && !CARDS[id].types.some((t) => ['event', 'landmark', 'project', 'way', 'ally', 'trait', 'prophecy'].includes(t));
// 見た目の色分けに使う代表の種類（CSS の data-type）
export function styleType(id) {
  const t = CARDS[id].types;
  if (t.includes('curse')) return 'curse';
  if (t.includes('duration')) return 'duration';
  if (t.includes('treasure') && !t.includes('action')) return t.includes('victory') ? 'treasure-victory' : 'treasure';
  if (!t.includes('action')) return 'victory';
  if (t.includes('attack')) return 'action-attack';
  if (t.includes('reaction')) return 'action-reaction';
  if (t.includes('victory')) return 'action-victory';
  return 'action';
}

// イベント・ランドマークなど、サプライの横に置く札（landscape）。types に 'event' など
export const LANDSCAPE_TYPES = ['event', 'landmark', 'project', 'way', 'ally', 'trait', 'prophecy'];
export const isLandscape = (id) => CARDS[id].types.some((t) => LANDSCAPE_TYPES.includes(t));
export function landscapePool(setIds) {
  return Object.values(CARDS).filter((c) => isLandscape(c.id) && !c.notSupply && (!setIds || setIds.includes(c.set))).map((c) => c.id);
}

export function kingdomPool(setIds) {
  return Object.values(CARDS).filter((c) => isKingdom(c.id) && (!setIds || setIds.includes(c.set))).map((c) => c.id);
}

export function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function randomKingdom(pool, n = 10) {
  return shuffle([...pool]).slice(0, n);
}

// kingdom: 王国カード 10 種の id。names: 席の名前（省略すると「1人目」…）
// opts.colony: 新天地・白金を使うか。省略すると、王国カードのうち「繁栄」の割合の確率で使う
// opts.shelters: 初めの小屋 3 枚を避難所にするか。省略すると「暗黒時代」の割合の確率
// opts.landscapes: イベントなど、サプライの横に置く札の id
export function newGame(numPlayers, kingdom, names, opts = {}) {
  const vp = numPlayers === 2 ? 8 : 12;
  const supply = {
    copper: 60 - 7 * numPlayers, silver: 40, gold: 30,
    estate: vp, duchy: vp, province: vp, curse: 10 * (numPlayers - 1),
  };
  const sorted = [...kingdom].sort((a, b) => CARDS[a].cost - CARDS[b].cost || CARDS[a].name.localeCompare(CARDS[b].name, 'ja'));
  for (const id of sorted) supply[id] = is(id, 'victory') ? vp : 10;
  const prosperity = kingdom.filter((id) => CARDS[id].set.startsWith('prosperity')).length;
  const colony = opts.colony ?? (CARDS.colony && Math.random() * kingdom.length < prosperity);
  if (colony && CARDS.colony) { supply.platinum = 12; supply.colony = vp; }
  if (kingdom.some((id) => CARDS[id].potion)) supply.potion = 16;

  const dark = kingdom.filter((id) => CARDS[id].set.startsWith('darkages')).length;
  const shelters = CARDS.shack && (opts.shelters ?? Math.random() * kingdom.length < dark);
  const players = Array.from({ length: numPlayers }, (_, i) => {
    const deck = shuffle([...Array(7).fill('copper'), ...(shelters ? ['shack', 'tombs', 'wildestate'] : Array(3).fill('estate'))]);
    // inPlay: 前の手番から場に残っているカード（持続）。nextTurn: 次の手番の始めに行う効果。mats: 脇に置いたカード。tokens: コインなどの印
    // states: 状態の札（森の迷い子・ふしあわせなど）の id
    // projects: 買ったプロジェクトの id
    const p = { name: (names && names[i]) || `${i + 1}人目`, deck, hand: [], discard: [], turnsTaken: 0, inPlay: [], nextTurn: [], mats: {}, tokens: { journey: true, pile: {} }, lastGains: [], states: [], projects: [] };
    drawCards(p, 5);
    return p;
  });

  const game = {
    players, supply, kingdom: sorted, trash: [], landscapes: [...(opts.landscapes || [])],
    current: 0,
    turn: freshTurn(),
    playArea: [],
    nonSupply: {},    // サプライ外の山（褒賞など）。{ id: 枚数 }。買えないが、効果で獲得できる
    artifacts: {},    // アーティファクトの持ち主（{ id: 席の番号 }）
    traits: {},       // 特性がついた山（{ 特性の id: 山の id }）
    pileVP: {},       // 山に置かれた勝利点トークン（{ 山の id: 数 }）
    landmarkVP: {},   // ランドマークなどに置かれた勝利点トークン（{ id: 数 }）
    pileDebt: {},     // 山に置かれた借金トークン（買った人が受け取る）
    stacks: {},       // ちがう札が重なった山（がれき・騎士など）。{ 山の id: [id...]（末尾が一番上）}。supply[山の id] は残り枚数
    embargo: {},      // サプライの山に置かれた印の数（買うと 1 つにつき災い）
    extraTurn: false, // 今の手番が追加の手番か
    over: false,
    log: [`${players[0].name}の番です。`],
  };
  for (const c of Object.values(CARDS)) if (c.reset) c.reset();
  for (const h of HOOKS.setup) h(game);
  return game;
}

function freshTurn() {
  return {
    phase: 'action', actions: 1, buys: 1, money: 0, potions: 0, silverBonus: 0, copperBonus: 0, costDown: 0, actionCostDown: 0, actionsPlayed: 0,
    banned: [], // この手番に買えないカード
    events: [], // この手番に買ったイベント
    gained: [], bought: [], stay: [], outpost: false,
  };
}

export function currentPlayer(game) { return game.players[game.current]; }
// 手番を操作している人（ふつうは手番の人。乗っ取りの手番では乗っ取った人）
export const turnController = (game) => (game.controller != null ? game.controller : game.current);
const answerer = (game, pi) => (pi === game.current ? turnController(game) : pi);
const log = (game, text) => { game.log.push(text); };

// ---- 山札・手札の道具 ----
// 山札の一番上（末尾）から 1 枚取る。山札が空なら捨て札を混ぜる。どちらも空なら null
export function takeTop(player) {
  if (player.deck.length === 0) {
    if (player.discard.length === 0) return null;
    player.deck = shuffle(player.discard);
    player.discard = [];
    // 星の地図: 混ぜたとき 1 枚を一番上に置いてよい。ponytail: 問わずに、いちばん高い札を上にする（混ぜるのは問いを出せない場所なので）
    // 隠し財布: 混ぜたとき好きな位置に入れてよい。ponytail: 問わずに一番上にする
    for (let i = player.deck.length - 1; i >= 0; i--) if (player.deck[i] === 'nestegg') player.deck.push(...player.deck.splice(i, 1));
    if (player.projects && player.projects.includes('j_starchart') && player.deck.length > 1) {
      let best = 0;
      player.deck.forEach((id, i) => { if (CARDS[id].cost > CARDS[player.deck[best]].cost) best = i; });
      player.deck.push(...player.deck.splice(best, 1));
    }
  }
  return player.deck.pop();
}

export function drawCards(player, n) {
  const drawn = [];
  // -1 カードの印: 次に引くとき 1 枚少なく引いて、印を外す
  if (n > 0 && player.tokens.minusCard) { player.tokens.minusCard = false; n -= 1; }
  for (let i = 0; i < n; i++) {
    const id = takeTop(player);
    if (id == null) break;
    drawn.push(id);
  }
  player.hand.push(...drawn);
  return drawn;
}

// 山札の上に置く（次に引かれる）
export const putOnDeck = (player, id) => { player.deck.push(id); };

// 手札の位置 indices のカードを取り出して返す（手札から消える）
export function takeFromHand(player, indices) {
  const moved = [];
  [...indices].sort((a, b) => b - a).forEach((i) => { moved.unshift(player.hand[i]); player.hand.splice(i, 1); });
  return moved;
}

// 廃棄する。廃棄したときの効果（カードの onTrash、HOOKS.trash）を行う
export function* trashCards(game, player, ids) {
  if (!ids.length) return;
  if (game.controller != null && player === currentPlayer(game)) {
    // 乗っ取られた手番に廃棄した札は脇に置き、手番の終わりに本人の捨て札へ戻す
    (player.mats.possessed = player.mats.possessed || []).push(...ids);
    log(game, `${player.name}の「${ids.map((id) => CARDS[id].name).join('」「')}」を脇に置いた（手番の終わりに捨て札へ）。`);
    return;
  }
  game.trash.push(...ids);
  log(game, `${player.name}が「${ids.map((id) => CARDS[id].name).join('」「')}」を廃棄。`);
  const pi = game.players.indexOf(player);
  if (pi === game.current && game.turn) game.turn.trashed = (game.turn.trashed || 0) + ids.length;
  for (const id of ids) {
    if (CARDS[id].onTrash) yield* CARDS[id].onTrash(game, player, pi, id);
    for (const h of HOOKS.trash) yield* h(game, player, pi, id);
  }
}

// 捨て札にする（片付け以外）。捨てたときの効果（カードの onDiscard）を行う
export function* discardCards(game, player, ids, silent) {
  player.discard.push(...ids);
  if (!silent && ids.length) log(game, `${player.name}が${ids.length}枚捨てた。`);
  const pi = game.players.indexOf(player);
  for (const id of ids) if (CARDS[id].onDiscard && player.discard.includes(id)) yield* CARDS[id].onDiscard(game, player, pi, id);
}

export const emptyPiles = (game) => Object.values(game.supply).filter((n) => n <= 0).length;

// この手番でのコスト（コストを下げる効果を反映）。買う・獲得の上限・比べるときは必ずこれを使う
export function costOf(game, id) {
  const st = game.stacks && game.stacks[id];
  if (st) return st.length ? costOf(game, st[st.length - 1]) : CARDS[id].cost;
  const c = CARDS[id];
  const t = game.turn;
  let cost = c.cost;
  if (t) cost -= t.costDown + (c.types.includes('action') ? t.actionCostDown : 0);
  if (c.costAdjust) cost -= c.costAdjust(game);
  const tok = game.players && game.players[game.current] && game.players[game.current].tokens.pile;
  if (t && tok && tok.cost && tok.cost === pileOf(id)) cost -= 2; // 舟便の印（自分の手番だけ）
  for (const h of HOOKS.cost) cost -= h(game, id);
  return Math.max(0, cost);
}

// 借金のコストがある札（重なった山は一番上）は「コスト X 以下」に入らない
// ponytail: 借金のコストの札を廃棄して獲得する場面（同じ借金まで許す）は扱っていない
const debtCost = (game, id) => { const st = game.stacks[id]; const top = st ? st.at(-1) : id; return top ? (CARDS[top].debt || 0) : 0; };
// maxPotion: ポーションのコストをいくつまで許すか（ふつうは 0。廃棄した札にポーションがあれば、その数）
// ponytail: 「ちょうどコスト +1」系はポーションを見ずにお金だけで比べる。ポーションの札を廃棄して使う場面は少ないので、要るときに直す
export function supplyOptions(game, maxCost, pred, maxPotion = 0) {
  return Object.keys(game.supply)
    .filter((id) => game.supply[id] > 0 && costOf(game, id) <= maxCost && (CARDS[id].potion || 0) <= maxPotion && !debtCost(game, id) && (!pred || pred(id)))
    .sort((a, b) => costOf(game, b) - costOf(game, a));
}

// to: 'discard'（ふつう）/ 'hand' / 'deck'（山札の上）。獲得できたら true。
// 獲得したときの効果（カード自身の onGain、手札の reactGain、場の whenGain）を順に解決する。
// 効果の中で獲得したカードを動かすときは relocate() を使う。
export function* gain(game, pi, id, to = 'discard') {
  if (game.controller != null && pi === game.current) pi = game.controller; // 乗っ取られた人の獲得は、乗っ取った人のものになる
  const player = game.players[pi];
  const piles = id in game.supply ? game.supply : game.nonSupply;
  if (!id || !(piles[id] > 0)) return false;
  piles[id] -= 1;
  if (game.stacks[id]) id = game.stacks[id].pop(); // 重なった山は一番上の札
  const where = to === 'hand' ? '（手札へ）' : to === 'deck' ? '（山札の上へ）' : '';
  log(game, `${player.name}が「${CARDS[id].name}」を獲得${where}。`);
  yield* receive(game, pi, id, to);
  return true;
}

// サプライ以外（廃棄置き場など）から来たカードを、獲得として受け取る
export function* receive(game, pi, id, to = 'discard') {
  const player = game.players[pi];
  if (to === 'hand') player.hand.push(id);
  else if (to === 'deck') player.deck.push(id);
  else player.discard.push(id);
  if (pi === game.current) game.turn.gained.push(id);
  const got = { id, to, pi };
  if (CARDS[id].onGain) yield* CARDS[id].onGain(game, got);
  if (pi === game.current) for (const c of [...game.playArea]) if (CARDS[c].whenGain && got.to !== 'gone') yield* CARDS[c].whenGain(game, got);
  for (const c of [...new Set(player.hand)]) if (CARDS[c].reactGain && got.to !== 'gone' && player.hand.includes(c)) yield* CARDS[c].reactGain(game, got);
  for (const h of HOOKS.gain) yield* h(game, got);
  // この手番に獲得した札を山札の上に置いてよい（髪飾り・旅回りの市）
  if (game.turn.topdeckGains && got.pi === game.current && (got.to === 'discard' || got.to === 'hand')
    && (yield* askYesNo(game, got.pi, `獲得した「${CARDS[got.id].name}」を山札の上に置きますか？`, '山札の上へ', 'そのまま', [got.id]))) yield* relocate(game, got, 'deck');
}

// 獲得したカードを、今ある場所から dest（'discard' / 'hand' / 'deck' / 'trash' / 'gone'=呼び出し側が持つ）へ動かす
export function* relocate(game, got, dest) {
  const p = game.players[got.pi];
  const from = got.to === 'hand' ? p.hand : got.to === 'deck' ? p.deck : got.to === 'discard' ? p.discard : null;
  if (!from) return false;
  const i = from.lastIndexOf(got.id);
  if (i < 0) return false;
  from.splice(i, 1);
  if (dest === 'hand') p.hand.push(got.id);
  else if (dest === 'deck') p.deck.push(got.id);
  else if (dest === 'discard') p.discard.push(got.id);
  else if (dest === 'trash') yield* trashCards(game, p, [got.id]);
  got.to = dest;
  return true;
}

// 持続: この手番の片付けでカード id を場に残し、次の自分の手番の始めに fn を行う
export function later(game, id, fn) {
  const p = currentPlayer(game);
  game.turn.stay.push(id);
  p.nextTurn.push(fn);
}

// 「次に〜したとき」まで場に残る札。entry.done を true にすると、次のその人の片付けで捨てられる
export function hold(game, pi, id) {
  const e = { id, done: false };
  (game.players[pi].holds = game.players[pi].holds || []).push(e);
  return e;
}

// 手番以外に使った持続（護衛兵など）にも使える later。手番の人なら later と同じ
export function laterFor(game, pi, id, fn) {
  if (pi === game.current) { later(game, id, fn); return; }
  game.players[pi].nextTurn.push(fn); // 札は playOutOfTurn で inPlay にあるので、次のその人の手番まで残る
}

// 旅の印を裏返す。表になったら true
export function flipJourney(p) { p.tokens.journey = !p.tokens.journey; return p.tokens.journey; }

// ---- 問いを出す道具（yield* で使う） ----
const handIdx = (player, pred) => player.hand.reduce((acc, id, i) => (!pred || pred(id) ? [...acc, i] : acc), []);

// 手札から min〜max 枚選ばせる。選べる札がなければ問わずに [] を返す
export function* askHand(game, pi, purpose, min, max, pred) {
  const player = game.players[pi];
  const options = handIdx(player, pred);
  if (!options.length || max <= 0) return [];
  const lo = Math.min(min, options.length);
  const hi = Math.min(max, options.length);
  // 選び方が 1 通りしかない（全部選ぶしかない・同じ札しかない）ときは問わない
  if (lo === hi && (lo === options.length || new Set(options.map((i) => player.hand[i])).size === 1)) return options.slice(0, lo);
  const ans = yield { type: 'hand', player: answerer(game, pi), owner: pi, purpose, min: lo, max: hi, options };
  return (ans || []).filter((i) => options.includes(i)).slice(0, hi);
}

export function* askSupply(game, pi, purpose, maxCost, pred, optional = false, maxPotion = 0) {
  const options = supplyOptions(game, maxCost, pred, maxPotion);
  if (!options.length) return null;
  const ans = yield { type: 'supply', player: answerer(game, pi), owner: pi, purpose, options, optional };
  if (ans == null && optional) return null;
  return options.includes(ans) ? ans : options[0];
}

export function* askCards(game, pi, purpose, cards, min, max) {
  if (!cards.length || max <= 0) return [];
  const lo = Math.min(min, cards.length);
  const hi = Math.min(max, cards.length);
  if (lo === hi && (lo === cards.length || new Set(cards).size === 1)) return cards.map((_, i) => i).slice(0, lo);
  const ans = yield { type: 'cards', player: answerer(game, pi), owner: pi, purpose, cards, min: lo, max: hi };
  return [...new Set(ans || [])].filter((i) => i >= 0 && i < cards.length).slice(0, hi);
}

export function* askChoose(game, pi, purpose, choices, cards) {
  const ans = yield { type: 'choose', player: answerer(game, pi), owner: pi, purpose, choices, cards };
  return choices.some((c) => c.value === ans) ? ans : choices[0].value;
}

export const askYesNo = (game, pi, purpose, yes = 'はい', no = 'いいえ', cards) =>
  askChoose(game, pi, purpose, [{ value: true, label: yes }, { value: false, label: no }], cards);

// 手番の人以外に、席順で fn(pi) を行う。
// リアクション: onAttack（見せてよい・効果あり）を持つ札は見せるか問う。blocksAttack（水濠）は見せても損がないので自動で見せて防ぐ
export function* attackOthers(game, fn) {
  const n = game.players.length;
  for (let k = 1; k < n; k++) {
    const pi = (game.current + k) % n;
    const target = game.players[pi];
    for (const rid of [...new Set(target.hand)]) {
      const r = CARDS[rid];
      if (!r.onAttack || !target.hand.includes(rid)) continue;
      if (r.canReact && !r.canReact(game, target)) continue;
      if (yield* askYesNo(game, pi, `アタックされた。「${r.name}」を見せますか？`, '見せる', '見せない', [rid])) {
        log(game, `${target.name}が「${r.name}」を見せた。`);
        yield* r.onAttack(game, target, pi);
      }
    }
    const blocker = target.hand.find((id) => CARDS[id].blocksAttack) || target.inPlay.find((id) => CARDS[id].protects);
    if (blocker) {
      log(game, `${target.name}が「${CARDS[blocker].name}」を見せて防いだ。`);
      continue;
    }
    yield* fn(pi);
  }
}

// cards を山札の上に好きな順で戻す。選んだ順に上から並ぶ（1 種類だけなら問わない）
export function* putBackInOrder(game, pi, cards) {
  const rest = [...cards];
  const top = [];
  while (rest.length > 1 && new Set(rest).size > 1) {
    const [i] = yield* askCards(game, pi, top.length ? '次に上に置く札を選ぶ' : '山札の一番上に置く札を選ぶ', rest, 1, 1);
    top.push(...rest.splice(i ?? 0, 1));
  }
  top.push(...rest);
  for (const id of top.reverse()) game.players[pi].deck.push(id);
}

// 山札の上から n 枚めくって取り出す（めくった札はどこにも入っていない状態）
export function reveal(player, n) {
  const out = [];
  for (let i = 0; i < n; i++) { const id = takeTop(player); if (id == null) break; out.push(id); }
  return out;
}

// 手番の人以外（アタックでない）
// 循環: 重なった山の一番上の札と同じ名前の札を、すべて山の一番下へ移す
export function rotatePile(game, pile) {
  const st = game.stacks[pile];
  if (!st || !st.length) return;
  const top = st.at(-1);
  game.stacks[pile] = [...st.filter((x) => x === top), ...st.filter((x) => x !== top)];
}

// サプライから 1 枚取り出す（獲得ではない。廃棄するときなど）。重なった山なら一番上。取れた札の id か null
export function takeFromSupply(game, id) {
  if (!(game.supply[id] > 0)) return null;
  game.supply[id] -= 1;
  return game.stacks[id] ? game.stacks[id].pop() : id;
}

// 札を元の山に戻す（どこから取り出したかは呼び出し側が消しておく）。戻す山がなければ false
export function returnCard(game, id) {
  const pile = CARDS[id].pile;
  if (pile && game.stacks[pile]) { game.stacks[pile].push(id); if (pile in game.supply) game.supply[pile] += 1; else game.nonSupply[pile] += 1; return true; }
  if (id in game.nonSupply) { game.nonSupply[id] += 1; return true; }
  if (id in game.supply) { game.supply[id] += 1; return true; }
  return false;
}

// 場から自分の山に戻す（サプライ外の山・サプライの山）。戻せたら true
export function returnToPile(game, id) {
  const at = game.playArea.lastIndexOf(id);
  if (at < 0 || !returnCard(game, id)) return false;
  game.playArea.splice(at, 1);
  return true;
}

export function* eachOther(game, fn) {
  const n = game.players.length;
  for (let k = 1; k < n; k++) yield* fn((game.current + k) % n);
}

// ---- 手番の流れ ----
// 場に出ているカードの効果を解決する（手札から出す・もう一度使うの両方から呼ぶ）
// pi: 使う人（省略すると手番の人。手番以外に使うカードもある）
export function* resolve(game, id, pi = game.current) {
  const card = CARDS[id];
  // 向こう見ずな（特性）: 効果を 2 回使う
  const times = game.traits && game.traits.t_reckless && pileOf(id) === game.traits.t_reckless && !game.turn.recklessInner ? 2 : 1;
  if (times === 2) {
    game.turn.recklessInner = true;
    yield* resolve(game, id, pi);
    yield* resolve(game, id, pi);
    game.turn.recklessInner = false;
    return;
  }
  if (card.types.includes('action') && pi === game.current && game.turn.phase === 'action') {
    game.turn.actionsPlayed += 1;
    // 山に置いた自分の印: その山の札を使うたび、先に +1 カード / +1 アクション / +1 購入 / +1 金
    const tok = game.players[pi].tokens.pile;
    const pile = pileOf(id);
    if (tok.card === pile) drawCards(game.players[pi], 1);
    if (tok.action === pile) game.turn.actions += 1;
    if (tok.buy === pile) game.turn.buys += 1;
    if (tok.coin === pile) game.turn.money += 1;
  }
  if (card.play) yield* card.play(game, game.players[pi], pi);
}

// 酒場マット（p.mats.tavern）の札を呼び出す。when: 'start' / 'afterAction' / 'gain' / 'buyEnd'
// 札の call = { when, can(game, p, ctx), *run(game, p, pi, ctx) }。呼び出した札は場に出て、その手番の片付けで捨てる
export function* offerCalls(game, pi, when, ctx) {
  const p = game.players[pi];
  const tavern = p.mats.tavern || [];
  for (const id of [...new Set(tavern)]) {
    const call = CARDS[id].call;
    if (!call || call.when !== when) continue;
    while (tavern.includes(id) && (!call.can || call.can(game, p, ctx))) {
      if (!(yield* askYesNo(game, pi, `酒場マットの「${CARDS[id].name}」を呼び出しますか？`, '呼び出す', 'しない', [id]))) break;
      tavern.splice(tavern.indexOf(id), 1);
      if (pi === game.current) game.playArea.push(id); else p.inPlay.push(id);
      log(game, `${p.name}が「${CARDS[id].name}」を呼び出した。`);
      yield* call.run(game, p, pi, ctx);
      if (call.once) break;
    }
  }
}

// 場の札を酒場マットに置く（リザーブ）
export function toTavern(game, p, id) {
  const at = game.playArea.lastIndexOf(id);
  if (at < 0) return false;
  (p.mats.tavern = p.mats.tavern || []).push(...game.playArea.splice(at, 1));
  return true;
}

// 手番の人以外が手札などから使うとき: その人の場（inPlay）に置き、次のその人の手番の片付けで捨てる
export function* playOutOfTurn(game, pi, id) {
  const p = game.players[pi];
  if (pi === game.current) game.playArea.push(id); else p.inPlay.push(id);
  log(game, `${p.name}が「${CARDS[id].name}」を使用。`);
  yield* resolve(game, id, pi);
}

// 手札のアクションを使う（アクション権を 1 使う）
// 手札のアクションを今使えるか（総大将の印・船出の手番の 3 枚まで などを見る）
export function canPlayAction(game, cardId) {
  const player = currentPlayer(game);
  if (game.turn.phase !== 'action' || game.turn.actions <= 0 || !is(cardId, 'action') || !player.hand.includes(cardId)) return false;
  if (player.tokens.warlorded > 0 && game.playArea.filter((id) => id === cardId).length >= 2) return false;
  if (game.turn.handPlayLimit != null && (game.turn.handPlays || 0) >= game.turn.handPlayLimit) return false;
  return true;
}

export function* playAction(game, cardId) {
  const player = currentPlayer(game);
  const idx = player.hand.indexOf(cardId);
  if (idx === -1 || !canPlayAction(game, cardId)) return;
  game.turn.handPlays = (game.turn.handPlays || 0) + 1;
  player.hand.splice(idx, 1);
  game.playArea.push(cardId);
  game.turn.actions -= 1;
  log(game, `${player.name}が「${CARDS[cardId].name}」を使用。`);
  for (const h of HOOKS.play) yield* h(game, cardId);
  // 魅入られた人（tokens.enchanted）: この手番に最初に使うアクションは、効果の代わりに +1 カード +1 アクション
  if (player.tokens.enchanted > 0 && !game.turn.enchantUsed) {
    game.turn.enchantUsed = true;
    log(game, `${player.name}の「${CARDS[cardId].name}」は、魅入られて +1 カード +1 アクションになった。`);
    game.turn.actionsPlayed += 1;
    drawCards(player, 1);
    game.turn.actions += 1;
    return;
  }
  // 習性（way）: 対局に習性があれば、札の効果の代わりに習性の効果で使ってよい
  const ways = game.landscapes.filter((id) => CARDS[id].types.includes('way'));
  const way = ways.length ? yield* askChoose(game, game.current, `「${CARDS[cardId].name}」をどう使いますか？`,
    [{ value: null, label: 'ふつうに使う' }, ...ways.map((w) => ({ value: w, label: CARDS[w].name }))], [cardId]) : null;
  if (way) {
    log(game, `${player.name}が「${CARDS[cardId].name}」を${CARDS[way].name}で使った。`);
    game.turn.actionsPlayed += 1;
    yield* CARDS[way].use(game, player, game.current, cardId);
    return;
  }
  yield* resolve(game, cardId);
  game.turn.handActions = (game.turn.handActions || 0) + 1;
  if (game.turn.handActions === 1 && player.projects.includes('j_citadel') && game.playArea.includes(cardId)) {
    log(game, `山城で「${CARDS[cardId].name}」をもう一度使う。`);
    yield* resolve(game, cardId);
  }
  yield* offerCalls(game, game.current, 'afterAction', { id: cardId });
  for (const h of HOOKS.afterAction) yield* h(game, cardId);
}

// 財宝を出す。効果（ジェネレータ）を持つ財宝は、問いがあれば yield する
export function* playTreasureGen(game, cardId) {
  const player = currentPlayer(game);
  const idx = player.hand.indexOf(cardId);
  if (idx === -1 || !is(cardId, 'treasure')) return;
  if (game.turn.handPlayLimit != null && (game.turn.handPlays || 0) >= game.turn.handPlayLimit) return;
  game.turn.handPlays = (game.turn.handPlays || 0) + 1;
  player.hand.splice(idx, 1);
  game.playArea.push(cardId);
  yield* treasureEffect(game, cardId);
}

// 場に出した財宝の効果（手札以外から出すとき・2 回使うときもこれ）
export function* treasureEffect(game, cardId) {
  // 妬み心の手番は、銀と金が 1 金しか出さない
  const reck = game.traits && game.traits.t_reckless && pileOf(cardId) === game.traits.t_reckless ? 2 : 1;
  game.turn.money += reck * (game.turn.envious && (cardId === 'silver' || cardId === 'gold') ? 1 : CARDS[cardId].value || 0);
  game.turn.potions += CARDS[cardId].potionValue || 0;
  if (cardId === 'silver' && game.turn.silverBonus) {
    game.turn.money += game.turn.silverBonus; // 両替商 1 枚につき、最初の銀で +1
    game.turn.silverBonus = 0;
  }
  if (cardId === 'copper') game.turn.money += game.turn.copperBonus;
  if (CARDS[cardId].play) yield* resolve(game, cardId);
  for (const h of HOOKS.treasure) yield* h(game, cardId);
}

// 問いのない財宝をすぐ出す（問いがあれば最初の選択肢で答える）
export function playTreasure(game, cardId) {
  const gen = playTreasureGen(game, cardId);
  let step = gen.next();
  while (!step.done) step = gen.next(undefined);
}

export function playAllTreasures(game) {
  const player = currentPlayer(game);
  for (const id of [...player.hand]) if (is(id, 'treasure') && (!CARDS[id].play || CARDS[id].autoPlay)) playTreasure(game, id);
}

export function startBuyPhase(game) { game.turn.phase = 'buy'; }
// 夜のフェイズ: 購入のあと、片付けの前。夜行（night）の札を手札から好きなだけ使える（アクション権は使わない）
export function enterNightPhase(game) { game.turn.phase = 'night'; }
export const canPlayNight = (game, id) => game.turn.phase === 'night' && is(id, 'night') && currentPlayer(game).hand.includes(id);
export function* playNight(game, cardId) {
  if (!canPlayNight(game, cardId)) return;
  const player = currentPlayer(game);
  player.hand.splice(player.hand.indexOf(cardId), 1);
  game.playArea.push(cardId);
  log(game, `${player.name}が「${CARDS[cardId].name}」を使用（夜）。`);
  yield* resolve(game, cardId);
}

// 購入フェイズに入る（購入フェイズの始めの効果を行う）。画面はこちらを使う
export function* enterBuyPhase(game) {
  if (game.turn.phase === 'buy') return;
  game.turn.phase = 'buy';
  for (const h of HOOKS.buyPhase) yield* h(game);
}

// 手番の始め: 前の手番から残っていたカードを場に戻し、その効果を行う
export function* beginTurn(game) {
  const p = currentPlayer(game);
  game.playArea.push(...p.inPlay.splice(0));
  // -1 金の印: 次に得るお金が 1 少ない（お金を -1 から始め、手番の終わりにまだ 0 未満なら印を戻す）
  // ponytail: 「次にお金を得るとき」を、手番の始めのお金 -1 で近似している。財宝を 1 枚も出さずに 0 金の札を買えない、などの差が出る
  if (p.tokens.minusCoin) { p.tokens.minusCoin = false; game.turn.money -= 1; }
  for (const job of p.nextTurn.splice(0)) yield* job(game, p, game.current);
  yield* offerCalls(game, game.current, 'start');
  for (const h of HOOKS.turnStart) yield* h(game, p, game.current);
  for (const id of [...new Set(p.hand)]) if (CARDS[id].atTurnStart && p.hand.includes(id)) yield* CARDS[id].atTurnStart(game, p, game.current);
}

// 村人を使って +1 アクションにする（アクションフェイズ）
export function spendVillager(game) {
  const p = currentPlayer(game);
  if (!(p.tokens.villagers > 0) || game.turn.phase !== 'action') return false;
  p.tokens.villagers -= 1;
  game.turn.actions += 1;
  return true;
}

// 財源（コイントークン）を使ってお金にする（購入フェイズ）
export function spendCoffers(game, n) {
  const p = currentPlayer(game);
  const k = Math.min(n, p.tokens.coffers || 0);
  p.tokens.coffers -= k;
  game.turn.money += k;
  return k;
}

// 借金: player.tokens.debt。借金があるあいだは買えない。買うときに残りのお金で先に自動で返す
const debtOf = (game) => currentPlayer(game).tokens.debt || 0;
export function payDebt(game) {
  const p = currentPlayer(game);
  const k = Math.min(p.tokens.debt || 0, Math.max(0, game.turn.money));
  p.tokens.debt = (p.tokens.debt || 0) - k;
  game.turn.money -= k;
  return k;
}

export function canBuy(game, cardId) {
  const alt = CARDS[cardId].altCost && CARDS[cardId].altCost(game);
  if (alt && game.turn.phase === 'buy' && game.turn.buys > 0 && game.supply[cardId] > 0 && !game.turn.noBuy && !debtOf(game)) return true;
  return game.turn.phase === 'buy' && game.turn.buys > 0 && game.supply[cardId] > 0 && !game.turn.banned.includes(cardId) && !game.turn.noBuy
    && game.turn.potions >= (CARDS[cardId].potion || 0)
    && !(game.turn.noBuyActions && is(game.stacks[cardId] ? (game.stacks[cardId].at(-1) || cardId) : cardId, 'action'))
    && game.turn.money - debtOf(game) >= costOf(game, cardId) && !(CARDS[cardId].canBuy && !CARDS[cardId].canBuy(game));
}

// 買う。買ったときの効果（カード自身の onBuy、場の whenBuy、山の印）→ 獲得 の順
export function* buyCard(game, cardId) {
  if (!canBuy(game, cardId)) return false;
  payDebt(game);
  game.turn.buys -= 1;
  // 別の払い方（動物の市: 手札のアクションを廃棄して払う）
  const altOk = CARDS[cardId].altCost && CARDS[cardId].altCost(game);
  const canPay = game.turn.money >= costOf(game, cardId);
  if (altOk && (!canPay || (yield* askYesNo(game, game.current, `「${CARDS[cardId].name}」: お金の代わりに手札のアクションを廃棄して払いますか？`, '廃棄して払う', 'お金で払う', [cardId])))) {
    yield* CARDS[cardId].payAlt(game, currentPlayer(game), game.current);
  } else game.turn.money -= costOf(game, cardId);
  const top = game.stacks[cardId] ? game.stacks[cardId].at(-1) : cardId;
  const buyer = currentPlayer(game);
  if (CARDS[top].debt) buyer.tokens.debt = (buyer.tokens.debt || 0) + CARDS[top].debt;
  if (game.pileDebt[cardId]) { buyer.tokens.debt = (buyer.tokens.debt || 0) + game.pileDebt[cardId]; game.pileDebt[cardId] = 0; }
  game.turn.potions -= CARDS[cardId].potion || 0;
  game.turn.bought.push(cardId);
  const pi = game.current;
  // 過払い: 残りのお金から好きなだけ余分に払い、その分の効果を得る
  if (CARDS[cardId].overpay && game.turn.money > 0) {
    const max = game.turn.money;
    const x = yield* askChoose(game, pi, `「${CARDS[cardId].name}」に余分に払いますか？`,
      Array.from({ length: max + 1 }, (_, k) => ({ value: k, label: k ? `+${k} 金 払う` : '払わない' })), [cardId]);
    game.turn.money -= x;
    if (x) yield* CARDS[cardId].overpay(game, pi, x);
  }
  const me0 = game.players[pi];
  if (me0.tokens.pile.trash === pileOf(cardId)) {
    const [i] = yield* askHand(game, pi, '段取りの印: 手札を 1 枚廃棄してよい', 0, 1);
    if (i != null) yield* trashCards(game, me0, takeFromHand(me0, [i]));
  }
  if (CARDS[cardId].onBuy) yield* CARDS[cardId].onBuy(game, pi);
  const me = game.players[pi];
  for (const c of [...new Set(me.hand)]) if (CARDS[c].reactBuy && me.hand.includes(c)) yield* CARDS[c].reactBuy(game, cardId, pi);
  for (const c of [...game.playArea]) if (CARDS[c].whenBuy) yield* CARDS[c].whenBuy(game, cardId, pi);
  for (const h of HOOKS.buy) yield* h(game, cardId, pi);
  for (let k = 0; k < (game.embargo[cardId] || 0); k++) yield* gain(game, pi, 'curse');
  yield* gain(game, pi, cardId);
  return true;
}

// イベントなどを買う（カードの購入ではない）。once: 1 手番に 1 度だけ
export function canBuyEvent(game, id) {
  const c = CARDS[id];
  return game.landscapes.includes(id) && !!c.buy && game.turn.phase === 'buy' && game.turn.buys > 0 && !game.turn.noBuyEvents
    && game.turn.money - debtOf(game) >= costOf(game, id) && !(c.once && game.turn.events.includes(id)) && !(c.canBuy && !c.canBuy(game));
}
export function* buyEvent(game, id) {
  if (!canBuyEvent(game, id)) return false;
  payDebt(game);
  game.turn.buys -= 1;
  game.turn.money -= costOf(game, id);
  if (CARDS[id].debt) currentPlayer(game).tokens.debt = (currentPlayer(game).tokens.debt || 0) + CARDS[id].debt;
  game.turn.events.push(id);
  const p = currentPlayer(game);
  log(game, `${p.name}がイベント「${CARDS[id].name}」を買った。`);
  yield* CARDS[id].buy(game, p, game.current);
  return true;
}

export function gameShouldEnd(game) {
  if (game.supply.province <= 0 || game.supply.colony <= 0) return true;
  return emptyPiles(game) >= 3;
}

// 片付け → 5 枚引く → 終了の判定 → 次の人（追加の手番なら同じ人）
export function* endTurn(game) {
  const player = currentPlayer(game);
  yield* offerCalls(game, game.current, 'buyEnd');
  payDebt(game); // 残ったお金は消えるので、借金に回す
  for (const h of HOOKS.endTurn) yield* h(game);
  if (game.turn.money < 0) { player.tokens.minusCoin = true; game.turn.money = 0; }
  for (const id of [...game.playArea]) if (CARDS[id].onCleanup && game.playArea.includes(id)) yield* CARDS[id].onCleanup(game, player, game.current);
  for (const id of game.turn.stay) {
    const i = game.playArea.indexOf(id);
    if (i >= 0) player.inPlay.push(...game.playArea.splice(i, 1));
  }
  player.holds = (player.holds || []).filter((e) => !e.done);
  for (const e of player.holds) {
    const i = game.playArea.indexOf(e.id);
    if (i >= 0) player.inPlay.push(...game.playArea.splice(i, 1));
  }
  player.discard.push(...player.hand, ...game.playArea);
  player.hand = [];
  game.playArea = [];
  if (!game.extraTurn) player.turnsTaken += 1;
  player.lastGains = game.turn.gained;
  player.lastTrashed = game.turn.trashed || 0;
  const extra = (game.turn.outpost || game.turn.mission || game.turn.seize || game.turn.voyage) && !game.extraTurn;
  const possess = !extra && !game.extraTurn && game.turn.possess;
  const wasPossessed = game.controller != null;
  if (wasPossessed) { player.discard.push(...(player.mats.possessed || []).splice(0)); game.controller = null; }
  drawCards(player, (extra && game.turn.outpost ? 3 : 5) + (game.turn.extraDraw || 0));
  if (player.mats.keep && player.mats.keep.length) player.hand.push(...player.mats.keep.splice(0)); // 取り置き
  for (const h of HOOKS.afterCleanup) yield* h(game, player, game.current);

  if (gameShouldEnd(game) || game.fleet) {
    // 船団: 終わるとき、船団を持つ人は順に 1 回ずつ追加の手番をする
    if (!game.fleet) {
      const n = game.players.length;
      game.fleet = [];
      for (let k = 1; k <= n; k++) { const i = (game.current + k) % n; if (game.players[i].projects.includes('j_fleet')) game.fleet.push(i); }
    }
    if (!game.fleet.length) { game.over = true; return; }
    game.current = game.fleet.shift();
    game.controller = null;
    game.extraTurn = true;
    game.turn = freshTurn();
    log(game, `${currentPlayer(game).name}の船団の手番です。`);
    return;
  }

  // 乗っ取りの手番のあとは、同じ人のふつうの手番
  if (!extra && !wasPossessed) {
    game.current = (game.current + 1) % game.players.length;
    // 屍術師: 手番を 1 回飛ばす
    for (let k = 0; k < game.players.length && game.players[game.current].tokens.skip > 0; k++) {
      game.players[game.current].tokens.skip -= 1;
      log(game, `${currentPlayer(game).name}は手番を飛ばす。`);
      game.current = (game.current + 1) % game.players.length;
    }
  }
  if (possess) game.controller = (game.current - 1 + game.players.length) % game.players.length;
  game.extraTurn = extra || possess;
  const noBuy = extra && game.turn.mission && !game.turn.outpost && !game.turn.seize;
  const wasVoyage = extra && game.turn.voyage;
  game.turn = freshTurn();
  game.turn.noBuy = noBuy; // 使いの旅の追加の手番は買えない
  if (extra && wasVoyage) game.turn.handPlayLimit = 3; // 船出の追加の手番は手札から 3 枚まで
  const who = possess ? `${game.players[game.controller].name}が操作する${currentPlayer(game).name}の追加の` : `${currentPlayer(game).name}の${extra ? '追加の' : ''}`;
  log(game, `${who}番です。`);
}

export const allCards = (player) => [...player.deck, ...player.hand, ...player.discard, ...player.inPlay, ...Object.values(player.mats).flat()];

// game を渡すと、ランドマークなど対局全体で決まる点も数える
export function score(player, game) {
  const all = allCards(player);
  let sum = all.reduce((acc, id) => {
    const c = CARDS[id];
    return acc + (c.points || 0) + (c.pointsFn ? c.pointsFn(all) : 0);
  }, player.tokens.vp || 0);
  // 置き場所で決まる点（果ての地など）は、札の種類ごとに 1 回数える
  for (const id of new Set(all)) if (CARDS[id].scoreBonus) sum += CARDS[id].scoreBonus(player);
  if (game) for (const id of game.landscapes) if (CARDS[id].score) sum += CARDS[id].score(game, player, all);
  for (const id of player.states || []) sum += CARDS[id].points || 0; // 状態（ふしあわせなど）
  return sum;
}

// 点が同じなら手番の少ない人が上。それも同じなら同じ順位
export function finalResults(game) {
  const rows = game.players
    .map((p, i) => ({ index: i, name: p.name, score: score(p, game), turns: p.turnsTaken }))
    .sort((a, b) => b.score - a.score || a.turns - b.turns);
  rows.forEach((r, i) => {
    const prev = rows[i - 1];
    r.rank = prev && prev.score === r.score && prev.turns === r.turns ? prev.rank : i + 1;
  });
  return rows;
}
