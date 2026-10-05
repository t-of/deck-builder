// ホスト引き継ぎの再生の自己チェック:
//   node test/replay.mjs [局数]
// 種を固定して CPU 同士で手を進め、毎手「控え（before/action/answers）→ JSON 往復 → 再生」した game が、
// 実際に進めた game と JSON.stringify で一致することを見る。viewFor が他人の手札・山札を漏らさないことも見る。
import assert from 'node:assert/strict';
import { newGame, viewFor } from '../engine.js';
import { actionGen, replay } from '../actions.js';
import { nextMove as cpuNextMove, answer as cpuAnswer } from '../cpu.js';
import '../cards-base.js';
import '../cards-seaside.js'; // 島（islet）マットの王国に足す
import '../cards-prosperity.js';

// アタック（民兵・堀）・反応・山札を見る（衛兵）札を含む王国
const kingdom = ['village', 'smithy', 'market', 'mercenary', 'moat', 'workshop', 'warehouse', 'remodel', 'sentinel', 'sorcerer'];

// 1手 = act() の1回ぶん。before/action/answers を控え、CPU の答えで最後まで進め、
// 控えから再生した game が本物と一致するか見る（JSON 往復も通す）
function recordedAct(game, type, args, level) {
  const before = structuredClone(game);
  const gen = actionGen(game, type, args);
  const answers = [];
  let step = gen.next();
  while (!step.done) {
    const q = step.value;
    // 答える人が CPU 席でなくても、この自己チェックでは全席 CPU として答えさせる
    const ans = cpuAnswer(game, q, level);
    answers.push(ans);
    step = gen.next(ans);
  }
  // JSON 往復（Firebase に積んで読み直すのと同じ扱い）をしてから再生する
  const beforeJson = JSON.parse(JSON.stringify(before));
  const actionJson = JSON.parse(JSON.stringify({ type, args }));
  const answersJson = JSON.parse(JSON.stringify(answers));
  const replayed = replay(beforeJson, actionJson, answersJson);
  assert.equal(JSON.stringify(replayed), JSON.stringify(game), `再生が本物と一致しない（${type} ${JSON.stringify(args)}）`);
  return step.value;
}

// main.js の doCpuMove と同じ組み合わせ: nextMove が返す1手ずつを、毎回 act() 相当（recordedAct）で進める
function playOneGame(seed, numPlayers, level) {
  const g = newGame(numPlayers, kingdom, null, { seed });
  for (let i = 0; !g.over && i < 4000; i++) {
    const m = cpuNextMove(g, level);
    if (m.type === 'end') { recordedAct(g, 'endTurn', {}, level); continue; }
    const { type, ...args } = m;
    recordedAct(g, type, args, level);
  }
  return g;
}

for (const seed of [1, 2, 3]) for (const n of [2, 3]) for (const level of ['weak', 'normal', 'strong']) playOneGame(seed, n, level);
console.log('ok: replay（控え→JSON 往復→再生が一致）');

// ---- viewFor: 他人の手札・山札・伏せたマットの中身を漏らさない ----
{
  const g = newGame(2, kingdom, ['あ', 'い'], { seed: 42 });
  const seaside = kingdom.includes('island') ? 'island' : null; // islet（島）マットを使う王国なら足す
  const pub = viewFor(g, null);
  pub.players.forEach((p, i) => {
    assert.equal(typeof p.hand.length, 'number', '手札が隠れていない');
    assert.ok(!Array.isArray(p.hand), 'pub に手札の中身が残っている');
    assert.equal(p.hand.length, g.players[i].hand.length, '手札の枚数が違う');
    assert.ok(!Array.isArray(p.deck), 'pub に山札の中身が残っている');
    assert.equal(p.deck.length, g.players[i].deck.length, '山札の枚数が違う');
  });
  const priv = viewFor(g, 0);
  assert.deepEqual(priv.players[0].hand, g.players[0].hand, '本人の手札が priv で隠れている');
  assert.deepEqual(priv.players[0].deck, g.players[0].deck, '本人の山札が priv で隠れている');
  assert.ok(!Array.isArray(priv.players[1].hand), '他人の手札が priv に漏れている');

  // 中身を伏せるマット（島など）があれば、本人以外には枚数だけになる
  g.players[1].mats.islet = ['estate', 'copper'];
  const pub2 = viewFor(g, null);
  assert.ok(!Array.isArray(pub2.players[1].mats.islet), '伏せたマットの中身が pub に漏れている');
  assert.equal(pub2.players[1].mats.islet.length, 2);
  // 酒場マット・追放は公開なので中身のまま
  g.players[1].mats.tavern = ['village'];
  const pub3 = viewFor(g, null);
  assert.deepEqual(pub3.players[1].mats.tavern, ['village'], '公開マットまで隠してしまった');
}
console.log('ok: viewFor（他人の手札・山札・伏せたマットを隠す）');
