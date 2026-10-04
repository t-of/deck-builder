// 間違えて購入フェイズに入ったときの「戻る」ロジックの自己チェック。
//   node test/undo-buy.mjs
import assert from 'node:assert/strict';
import { newGame, currentPlayer, enterBuyPhase, canUndoToAction, buyCard } from '../engine.js';
import '../cards-base.js';

function run(gen) {
  let step = gen.next();
  while (!step.done) step = gen.next(); // 基本の王国なら購入フェイズの始めに問いは出ない
  return step.value;
}

// 基本の王国（HOOKS.buyPhase を使う拡張の特性・ランドマークがないので、戻れるはず）
const kingdom = ['village', 'smithy', 'market', 'mercenary', 'moat', 'workshop', 'warehouse', 'remodel', 'archive', 'assembly'];

{
  const g = newGame(2, kingdom, ['あ', 'い']);
  const pre = structuredClone(g);
  const p = currentPlayer(g);
  const handBefore = [...p.hand];
  run(enterBuyPhase(g));
  assert.equal(g.turn.phase, 'buy');
  assert.ok(canUndoToAction(g, pre), '何も買っていなければ戻れるはず');

  // main.js の restoreToActionPhase と同じやり方（複製をかぶせる）で戻す
  for (const k of Object.keys(g)) delete g[k];
  Object.assign(g, pre);
  assert.equal(g.turn.phase, 'action', 'アクションフェイズに戻っている');
  assert.deepEqual(currentPlayer(g).hand, handBefore, '手札が元どおり');
}

{
  const g = newGame(2, kingdom, ['あ', 'い']);
  const pre = structuredClone(g);
  run(enterBuyPhase(g));
  run(buyCard(g, 'copper')); // 何か買うと戻れなくなる
  assert.ok(!canUndoToAction(g, pre), '買ったあとは戻れないはず');
}

console.log('undo-buy: OK');
