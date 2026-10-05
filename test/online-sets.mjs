// 拡張ごとの通信対戦の自己チェック:
//   node test/online-sets.mjs
// test/replay.mjs と同じやり方（控え→JSON 往復→再生）を、全拡張の「はじめての〜」プリセット
// （docs/private 不要、cards-*.js に元からあるプリセット。ランドスケープ込み）に広げる。
// 加えて、viewFor が「どの拡張のどのマット」でも他人の中身を漏らさないこと、
// 配られる問い（questionForAnswerer）が hand 型なら必ず id 入りで届くことを、カードごとに決め打ちせず汎用に見る。
import assert from 'node:assert/strict';
import { newGame, viewFor, PRESETS, questionForAnswerer, PUBLIC_MATS } from '../engine.js';
import { actionGen, replay } from '../actions.js';
import { nextMove as cpuNextMove, answer as cpuAnswer } from '../cpu.js';
import '../cards-base.js';
import '../cards-intrigue.js';
import '../cards-seaside.js';
import '../cards-prosperity.js';
import '../cards-hinterlands.js';
import '../cards-guilds.js';
import '../cards-alchemy.js';
import '../cards-darkages.js';
import '../cards-adventures.js';
import '../cards-empires.js';
import '../cards-nocturne.js';
import '../cards-renaissance.js';
import '../cards-menagerie.js';
import '../cards-promo.js';
import '../cards-allies.js';
import '../cards-plunder.js';
import '../cards-risingsun.js';

// 他人の手札・山札・伏せたマットが viewFor で枚数だけになっているか（拡張のマット名を決め打ちしない）
function assertNoLeak(game) {
  const pub = viewFor(game, null);
  pub.players.forEach((p, i) => {
    assert.ok(!Array.isArray(p.hand), `手札が漏れている（席${i}）`);
    assert.equal(p.hand.length, game.players[i].hand.length);
    assert.ok(!Array.isArray(p.deck), `山札が漏れている（席${i}）`);
    assert.equal(p.deck.length, game.players[i].deck.length);
    for (const name of Object.keys(p.mats)) {
      if (PUBLIC_MATS.includes(name)) continue;
      const real = game.players[i].mats[name];
      assert.ok(!Array.isArray(p.mats[name]), `マット「${name}」の中身が漏れている（席${i}）`);
      assert.equal(p.mats[name].length, real.length, `マット「${name}」の枚数が違う（席${i}）`);
    }
  });
  // 各席の priv は、本人の手札・山札・マットだけ中身のまま
  game.players.forEach((_, seat) => {
    const priv = viewFor(game, seat);
    assert.deepEqual(priv.players[seat].hand, game.players[seat].hand, `本人の手札が priv で隠れている（席${seat}）`);
    assert.deepEqual(priv.players[seat].deck, game.players[seat].deck, `本人の山札が priv で隠れている（席${seat}）`);
    for (const name of Object.keys(priv.players[seat].mats)) {
      assert.deepEqual(priv.players[seat].mats[name], game.players[seat].mats[name], `本人のマット「${name}」が priv で隠れている（席${seat}）`);
    }
  });
}

// 配られる問いが hand 型なら、id 入り（cardsAt）が options と同じ数・中身ありで届くか（main.js の idOf がこれだけで描ける）
function assertQuestionSelfContained(game, q) {
  const delivered = questionForAnswerer(game, q);
  if (q.type !== 'hand') { assert.equal(delivered, q); return; }
  assert.equal(delivered.cardsAt.length, q.options.length, '配られた問いの cardsAt が options と数が違う');
  for (const id of delivered.cardsAt) assert.ok(id != null, '配られた問いの cardsAt に空きがある');
}

function recordedAct(game, type, args, level) {
  const before = structuredClone(game);
  const gen = actionGen(game, type, args);
  const answers = [];
  let step = gen.next();
  while (!step.done) {
    const q = step.value;
    assertQuestionSelfContained(game, q);
    const ans = cpuAnswer(game, q, level);
    answers.push(ans);
    step = gen.next(ans);
  }
  const beforeJson = JSON.parse(JSON.stringify(before));
  const actionJson = JSON.parse(JSON.stringify({ type, args }));
  const answersJson = JSON.parse(JSON.stringify(answers));
  const { game: replayed, question } = replay(beforeJson, actionJson, answersJson);
  assert.equal(JSON.stringify(replayed), JSON.stringify(game), `再生が本物と一致しない（${type} ${JSON.stringify(args)}）`);
  assert.equal(question, null, `全部の答えを流したのに問いが残っている（${type} ${JSON.stringify(args)}）`);
  assertNoLeak(game);
  return step.value;
}

function playOneGame(preset, seed, numPlayers, level) {
  const kingdom = preset.cards;
  const g = newGame(numPlayers, kingdom, null, { seed, landscapes: preset.landscapes || [] });
  for (let i = 0; !g.over && i < 4000; i++) {
    const m = cpuNextMove(g, level);
    if (m.type === 'end') { recordedAct(g, 'endTurn', {}, level); continue; }
    const { type, ...args } = m;
    recordedAct(g, type, args, level);
  }
  return g;
}

let games = 0;
for (const preset of PRESETS) {
  for (const seed of [1, 2]) {
    for (const n of [2, 3]) {
      playOneGame(preset, seed, n, 'normal');
      games++;
    }
  }
}
console.log(`ok: online-sets（${PRESETS.length}個のプリセットで通信対戦の再生・viewFor・問いの自己完結を確認、${games}局）`);
