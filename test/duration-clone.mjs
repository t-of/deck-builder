// 持続の効果が残った game（p.nextTurn に関数）を写しても落ちないことの自己チェック:
//   node test/duration-clone.mjs
import assert from 'node:assert/strict';
import { newGame, viewFor, cloneGame, later, currentPlayer } from '../engine.js';
import { actionGen, replay } from '../actions.js';
import '../cards-base.js';
import '../cards-seaside.js';

const g = newGame(2, ['fishtown', 'beacon', 'compass', 'wagon', 'pier', 'tradeship', 'strategist', 'village', 'smithy', 'market'], null, { seed: 1 });
// 実際に持続札（漁村）を使う。人が使ったあとの act() と同じ状況
currentPlayer(g).hand.push('fishtown');
const gen = actionGen(g, 'action', { id: 'fishtown' });
for (let s = gen.next(); !s.done; s = gen.next([])) ;
assert.equal(typeof currentPlayer(g).nextTurn[0], 'function');
assert.throws(() => structuredClone(g), 'structuredClone が通る（再現の前提が変わった）');
const c = cloneGame(g);
assert.equal(c.players[0].nextTurn.length, 1);
assert.notEqual(c.players[0], g.players[0]);
assert.deepEqual(c.players[0].hand, g.players[0].hand);
viewFor(g, null); viewFor(g, 0);
// 控えが JSON 往復で関数を失っても、次の手番の始めで落ちない
const before = JSON.parse(JSON.stringify(g));
const { game } = replay(before, { type: 'endTurn', args: {} }, []);
assert.ok(game);
console.log('ok: duration-clone');
