'use strict';
// デッキ構築ゲームのルール・状態（画面・音・localStorage に触らない）。
// カードを使う処理は playCard(game, cardId) というジェネレータにしてある。
// 選択が要る効果は yield で止まり、呼び出し側（main.js）が選ばせた結果を .next(答え) で渡す。
// 玉座の間のように「アクションをもう一度使う」カードを将来足すときは、
// その効果の中から yield* playCard(game, otherId) を呼べば、同じ仕組みのまま重ねがけできる。

export const CARDS = {
  copper:   { id: 'copper',   name: '銅',   type: 'treasure', cost: 0, value: 1 },
  silver:   { id: 'silver',   name: '銀',   type: 'treasure', cost: 3, value: 2 },
  gold:     { id: 'gold',     name: '金',   type: 'treasure', cost: 6, value: 3 },
  estate:   { id: 'estate',   name: '小屋', type: 'victory', cost: 2, points: 1 },
  duchy:    { id: 'duchy',    name: '荘園', type: 'victory', cost: 5, points: 3 },
  province: { id: 'province', name: '領地', type: 'victory', cost: 8, points: 6 },

  warehouse:  { id: 'warehouse',  name: '倉庫',   type: 'action',          cost: 2, desc: '+1アクション。手札を好きな枚数捨て、同じ枚数引く' },
  moat:       { id: 'moat',       name: '水濠',   type: 'action-reaction', cost: 2, desc: '+2カード。他の人のアタックを、手札から見せると受けない' },
  moneylender:{ id: 'moneylender',name: '両替商', type: 'action',          cost: 3, desc: '+1カード +1アクション。この手番で最初に銀を出すと+1金' },
  village:    { id: 'village',    name: '集落',   type: 'action',          cost: 3, desc: '+1カード +2アクション' },
  workshop:   { id: 'workshop',   name: '作業場', type: 'action',          cost: 3, desc: 'コスト4以下のカードを1枚獲得' },
  mercenary:  { id: 'mercenary',  name: '傭兵',   type: 'action-attack',   cost: 4, desc: '+2金。他の全員は手札が3枚になるまで捨てる' },
  remodel:    { id: 'remodel',    name: '建て替え', type: 'action',        cost: 4, desc: '手札を1枚廃棄し、そのコスト+2以下のカードを1枚獲得' },
  smithy:     { id: 'smithy',     name: '鍛冶場', type: 'action',          cost: 4, desc: '+3カード' },
  market:     { id: 'market',     name: '露店',   type: 'action',          cost: 5, desc: '+1カード +1アクション +1購入 +1金' },
  mine:       { id: 'mine',       name: '鉱脈',   type: 'action',          cost: 5, desc: '手札の財宝を1枚廃棄してよい。そのコスト+3以下の財宝を1枚獲得し手札へ' },
};

export const KINGDOM_IDS = ['warehouse', 'moat', 'moneylender', 'village', 'workshop', 'mercenary', 'remodel', 'smithy', 'market', 'mine'];

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export function newGame(numPlayers) {
  const vp = numPlayers === 2 ? 8 : 12;
  const supply = { copper: 60 - 7 * numPlayers, silver: 40, gold: 30, estate: vp, duchy: vp, province: vp };
  for (const id of KINGDOM_IDS) supply[id] = 10;

  const players = Array.from({ length: numPlayers }, (_, i) => {
    const deck = shuffle([...Array(7).fill('copper'), ...Array(3).fill('estate')]);
    const p = { name: `${i + 1}人目`, deck, hand: [], discard: [], turnsTaken: 0 };
    drawCards(p, 5);
    return p;
  });

  return {
    players, supply, current: 0,
    turn: freshTurn(),
    playArea: [],
    attack: null,   // { queue: [playerIdx...], from: idx }
    over: false,
    log: [`${players[0].name}の番です。`],
  };
}

function freshTurn() {
  return { phase: 'action', actions: 1, buys: 1, money: 0, silverBonusArmed: false, silverBonusUsed: false };
}

export function currentPlayer(game) { return game.players[game.current]; }

export function drawCards(player, n) {
  const drawn = [];
  for (let i = 0; i < n; i++) {
    if (player.deck.length === 0) {
      if (player.discard.length === 0) break;
      player.deck = shuffle(player.discard);
      player.discard = [];
    }
    drawn.push(player.deck.pop());
  }
  player.hand.push(...drawn);
  return drawn;
}

function moveByIndices(from, to, indices) {
  const moved = [];
  [...indices].sort((a, b) => b - a).forEach((i) => { moved.push(from[i]); from.splice(i, 1); });
  to.push(...moved);
  return moved;
}

export function supplyOptions(game, maxCost, typeFilter) {
  return Object.keys(game.supply)
    .filter((id) => game.supply[id] > 0 && CARDS[id].cost <= maxCost && (!typeFilter || CARDS[id].type === typeFilter))
    .sort((a, b) => CARDS[b].cost - CARDS[a].cost);
}

function gainCard(game, player, cardId, toHand) {
  if (!cardId || game.supply[cardId] <= 0) return;
  game.supply[cardId] -= 1;
  (toHand ? player.hand : player.discard).push(cardId);
  game.log.push(`${player.name}が「${CARDS[cardId].name}」を獲得。`);
}

// ---- アクションカードの効果。選択が要るところで yield する ----
export function* playCard(game, cardId) {
  const player = currentPlayer(game);
  const idx = player.hand.indexOf(cardId);
  if (idx === -1) return;
  player.hand.splice(idx, 1);
  game.playArea.push(cardId);
  game.turn.actions -= 1;
  game.log.push(`${player.name}が「${CARDS[cardId].name}」を使用。`);

  switch (cardId) {
    case 'warehouse': {
      game.turn.actions += 1;
      const indices = yield { type: 'select-hand', purpose: '捨てる枚数を選ぶ（好きな枚数）', min: 0, max: player.hand.length };
      const discarded = moveByIndices(player.hand, player.discard, indices);
      drawCards(player, discarded.length);
      break;
    }
    case 'moat':
      drawCards(player, 2);
      break;
    case 'moneylender':
      drawCards(player, 1);
      game.turn.actions += 1;
      game.turn.silverBonusArmed = true;
      break;
    case 'village':
      drawCards(player, 1);
      game.turn.actions += 2;
      break;
    case 'workshop': {
      const options = supplyOptions(game, 4);
      if (options.length) {
        const pick = yield { type: 'select-supply', purpose: 'コスト4以下を1枚獲得', options };
        gainCard(game, player, pick, false);
      }
      break;
    }
    case 'mercenary':
      game.turn.money += 2;
      game.attack = { queue: game.players.map((_, i) => i).filter((i) => i !== game.current), from: game.current };
      break;
    case 'remodel': {
      if (!player.hand.length) break;
      const [trashIdx] = yield { type: 'select-hand', purpose: '廃棄する1枚を選ぶ', min: 1, max: 1 };
      if (trashIdx == null) break;
      const [trashed] = moveByIndices(player.hand, [], [trashIdx]);
      const options = supplyOptions(game, CARDS[trashed].cost + 2);
      if (options.length) {
        const pick = yield { type: 'select-supply', purpose: `コスト${CARDS[trashed].cost + 2}以下を1枚獲得`, options };
        gainCard(game, player, pick, false);
      }
      break;
    }
    case 'smithy':
      drawCards(player, 3);
      break;
    case 'market':
      drawCards(player, 1);
      game.turn.actions += 1;
      game.turn.buys += 1;
      game.turn.money += 1;
      break;
    case 'mine': {
      const treasureIdx = player.hand.reduce((acc, id, i) => (CARDS[id].type === 'treasure' ? [...acc, i] : acc), []);
      if (!treasureIdx.length) break;
      const picked = yield { type: 'select-hand', purpose: '廃棄する財宝を選ぶ（しなくてもよい）', min: 0, max: 1, options: treasureIdx };
      if (!picked.length) break;
      const [trashed] = moveByIndices(player.hand, [], picked);
      const options = supplyOptions(game, CARDS[trashed].cost + 3, 'treasure');
      if (options.length) {
        const pick = yield { type: 'select-supply', purpose: `コスト${CARDS[trashed].cost + 3}以下の財宝を1枚、手札へ獲得`, options };
        gainCard(game, player, pick, true);
      }
      break;
    }
    default:
      break;
  }
}

export function playTreasure(game, cardId) {
  const player = currentPlayer(game);
  const idx = player.hand.indexOf(cardId);
  if (idx === -1) return;
  player.hand.splice(idx, 1);
  game.playArea.push(cardId);
  game.turn.money += CARDS[cardId].value;
  if (cardId === 'silver' && game.turn.silverBonusArmed && !game.turn.silverBonusUsed) {
    game.turn.money += 1;
    game.turn.silverBonusUsed = true;
  }
}

export function playAllTreasures(game) {
  const player = currentPlayer(game);
  for (const id of [...player.hand]) if (CARDS[id].type === 'treasure') playTreasure(game, id);
}

export function buyCard(game, cardId) {
  if (game.turn.phase !== 'buy' || game.turn.buys <= 0) return false;
  const cost = CARDS[cardId].cost;
  if (game.turn.money < cost || game.supply[cardId] <= 0) return false;
  game.turn.buys -= 1;
  game.turn.money -= cost;
  gainCard(game, currentPlayer(game), cardId, false);
  return true;
}

// 攻撃を受ける側が捨てる枚数を決める（3枚になるまで）。indices は player.hand の位置。
export function resolveAttackDiscard(player, indices) {
  moveByIndices(player.hand, player.discard, indices);
}

function gameShouldEnd(game) {
  if (game.supply.province <= 0) return true;
  const emptyPiles = Object.values(game.supply).filter((n) => n <= 0).length;
  return emptyPiles >= 3;
}

export function endTurn(game) {
  const player = currentPlayer(game);
  player.discard.push(...player.hand, ...game.playArea);
  player.hand = [];
  game.playArea = [];
  player.turnsTaken += 1;
  drawCards(player, 5);

  if (gameShouldEnd(game)) { game.over = true; return; }

  game.current = (game.current + 1) % game.players.length;
  game.turn = freshTurn();
  game.log.push(`${currentPlayer(game).name}の番です。`);
}

export function score(player) {
  const all = [...player.deck, ...player.hand, ...player.discard];
  return all.reduce((sum, id) => sum + (CARDS[id].points || 0), 0);
}

export function finalResults(game) {
  return game.players
    .map((p, i) => ({ index: i, name: p.name, score: score(p), turns: p.turnsTaken }))
    .sort((a, b) => b.score - a.score || a.turns - b.turns);
}
