'use strict';
// 買い方表（優先リスト）の bot（docs/ai-specialize.md §3-1）。買う判断だけ表で決め、ほかはさいきょう CPU（cpu.js の expert）に任せる。
//   table = { duchyAt, estateAt, rules: [{ card, max, minDeck, minMoney, maxProv }] }
//   属州: 8 金以上なら買う。公領: 5 金以上で 属州の残り ≤ duchyAt。屋敷: 2 金以上で 属州の残り ≤ estateAt。
//   そのあと rules を上から。card を max 枚（持っている枚数）未満で、山札全体が minDeck 枚以上、使えるお金が minMoney 以上
//   （0 ならその札の値段）、属州の残りが maxProv 以下（省略か 99 なら無条件）のとき買う。当てはまる規則がなければ買わない。
//   tableBuy(game, table) → 買う札の id か null（cpu.js の buyChoice と同じ入口）
//   tableActor(table)     → { nextMove, answer }（cpu.js の nextMove・answer と同じ形）
import { currentPlayer, allCards, canBuy } from '../engine.js';
import { nextMove as cpuMove, answer as cpuAnswer } from '../cpu.js';
import { isBuyDecision, noBuyMove } from './player.js';

export function tableBuy(game, table) {
  const p = currentPlayer(game);
  const money = game.turn.money - (p.tokens.debt || 0);
  const mine = [...allCards(p), ...game.playArea];
  const left = game.supply.province;
  const ok = (id) => canBuy(game, id);
  if (money >= 8 && ok('province')) return 'province';
  if (money >= 5 && left <= table.duchyAt && ok('duchy')) return 'duchy';
  if (money >= 2 && left <= table.estateAt && ok('estate')) return 'estate';
  for (const r of table.rules) {
    if (!ok(r.card) || money < (r.minMoney || 0) || left > (r.maxProv ?? 99) || mine.length < (r.minDeck || 0)) continue;
    if (mine.filter((id) => id === r.card).length >= r.max) continue;
    return r.card;
  }
  return null;
}

export function tableActor(table) {
  return {
    nextMove(game) {
      if (!isBuyDecision(game)) return cpuMove(game, 'expert');
      const id = tableBuy(game, table);
      return id ? { type: 'buy', id } : noBuyMove(currentPlayer(game));
    },
    answer: (game, q) => cpuAnswer(game, q, 'expert'),
  };
}

// 手書きの定石（first の札。docs/ai-specialize.md §1）。進化の初期集団であり、測るときの物差し（match.mjs の table:seed:<名前>）でもある
const R = (card, max, o = {}) => ({ card, max, ...o });
export const SEEDS = {
  bigmoney: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('silver', 99)] },
  bigsmithy: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('smithy', 1), R('smithy', 2, { minDeck: 16 }), R('silver', 99)] },
  doublemilitia: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('mercenary', 2), R('silver', 99)] },
  militia: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('mercenary', 1), R('silver', 99)] },
  smithymilitia: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('smithy', 1), R('mercenary', 1), R('smithy', 2, { minDeck: 16 }), R('silver', 99)] },
  merchant: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('smithy', 1), R('moneylender', 2, { minDeck: 10 }), R('silver', 99)] },
  market: { duchyAt: 4, estateAt: 2, rules: [R('gold', 99, { minMoney: 6 }), R('smithy', 1), R('market', 2, { minMoney: 5 }), R('silver', 99)] },
};
