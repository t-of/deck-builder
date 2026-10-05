// 種つき乱数の自己チェック: 同じ種なら同じ盤・同じ手札・同じ山札になる（オンライン対戦のホスト引き継ぎが頼る性質）。
//   node test/seed.mjs
import assert from 'node:assert/strict';
import { newGame } from '../engine.js';
import '../cards-base.js';
import '../cards-darkages.js'; // 避難所・暗黒時代の判定（colony/shelters の抽選）も確かめるため

const kingdom = ['village', 'smithy', 'market', 'mercenary', 'moat', 'workshop', 'warehouse', 'remodel', 'archive', 'assembly'];

// 同じ種 → まったく同じ対局
{
  const a = newGame(3, kingdom, ['あ', 'い', 'う'], { seed: 12345 });
  const b = newGame(3, kingdom, ['あ', 'い', 'う'], { seed: 12345 });
  assert.equal(JSON.stringify(a), JSON.stringify(b), '同じ種なのに盤が違う');
}

// seed を省略しても毎回 rngState を持ち、種が違えば（ふつうは）結果が変わる
{
  const a = newGame(2, kingdom, ['あ', 'い'], { seed: 1 });
  const b = newGame(2, kingdom, ['あ', 'い'], { seed: 2 });
  assert.notEqual(a.rngState, undefined);
  assert.notEqual(JSON.stringify(a.players), JSON.stringify(b.players), '種を変えても手札・山札が同じ');
}

// 暗黒時代の王国（避難所になるかどうかの抽選にも乱数を使う）でも、同じ種なら同じ結果
{
  const darkKingdom = ['knights', 'zealot', 'stronghold', 'marketsquare', 'recluse', 'fief', 'ravager', 'rats', 'waif', 'impostor'];
  const a = newGame(3, darkKingdom, null, { seed: 777 });
  const b = newGame(3, darkKingdom, null, { seed: 777 });
  assert.equal(JSON.stringify(a), JSON.stringify(b), '暗黒時代の王国で同じ種なのに盤が違う');
}

// 古い保存データ（rngState が無い game）を渡しても、rng を呼べばその場で種が振られ、壊れない
{
  const g = newGame(2, kingdom, ['あ', 'い'], { seed: 1 });
  delete g.rngState;
  const { shuffle } = await import('../engine.js');
  assert.doesNotThrow(() => shuffle([...g.players[0].deck], g));
  assert.notEqual(g.rngState, undefined, 'rngState が振り直されていない');
}

console.log('ok: seed');
