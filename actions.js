'use strict';
// 盤を動かす「1手」を、type/args という小さな JSON から作る場所。main.js の act() と、
// オンライン対戦のホスト引き継ぎ（再生）の両方がここを通る（画面・音には一切触らない）。
//
// type/args は JSON にできる値だけ（カード id・数など）。CPU の自動の判断（どのカードを買うか等）は
// act() を呼ぶ前に決め切ってから args に入れる。actionGen 自身は Math.random を呼ばない。

import {
  beginTurn, playAction, playShadow, spendVillager, spendCoffers, payDebt, enterBuyPhase,
  playTreasureGen, playAllTreasures, enterNightPhase, playNight, buyCard, buyEvent, endTurn,
  currentPlayer, is, CARDS, playTreasure,
} from './engine.js';

// 「財宝を自動で出す」設定用。効果のある財宝（手で出す順番・可否に意味があるもの）は残す
export function autoPlayPlainTreasures(game) {
  const p = currentPlayer(game);
  for (const id of [...p.hand]) if (is(id, 'treasure') && !CARDS[id].play) playTreasure(game, id);
}

// type/args から、その手を進めるジェネレータを作る。buy/event は獲得できたか（true/false）を返す
export function* actionGen(game, type, args = {}) {
  switch (type) {
    case 'beginTurn': yield* beginTurn(game); return;
    case 'action': yield* playAction(game, args.id); return;
    case 'shadow': yield* playShadow(game, args.id); return;
    case 'villager': spendVillager(game); return;
    case 'coffers': spendCoffers(game, args.n); return;
    case 'payDebt': payDebt(game); return;
    case 'buyPhase':
      yield* enterBuyPhase(game);
      // args.auto: ホスト（答える本人）の「財宝を自動で出す」設定。再生がホストの設定に左右されないよう、
      // 判断そのものを args に記録しておく（設定を読み直すのではなく、記録された値をそのまま使う）
      if (args.auto) autoPlayPlainTreasures(game);
      return;
    case 'treasure': yield* playTreasureGen(game, args.id); return;
    case 'allTreasures': playAllTreasures(game); return;
    case 'nightPhase': enterNightPhase(game); return;
    case 'night': yield* playNight(game, args.id); return;
    case 'buy': return yield* buyCard(game, args.id);
    case 'event': return yield* buyEvent(game, args.id);
    case 'endTurn': yield* endTurn(game); return;
    default: return;
  }
}

// ホストの引き継ぎ用の再生: before（直前の控え）に action を打ち直し、answers を順に流し込む。
// 種つき乱数のおかげで、同じ山札・同じ結果になる（CPU の自動応答はここでは一切呼ばない。記録された答えをそのまま使う）
export function replay(before, action, answers) {
  const game = structuredClone(before);
  for (const p of game.players) Object.defineProperty(p, 'game', { value: game, enumerable: false });
  const gen = actionGen(game, action.type, action.args);
  let step = gen.next();
  for (const ans of answers) {
    if (step.done) break;
    step = gen.next(ans);
  }
  return game;
}
