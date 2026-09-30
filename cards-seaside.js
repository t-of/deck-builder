'use strict';
// 拡張「海辺」のカード（第二版の 27 種と、初版だけにある 8 種）。名前は本家と別の言い回し。
// 持続（duration）: 使った手番の片付けで場に残り、次の自分の手番の始めに効果がある。later() で登録する。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, resolve, reveal,
  putBackInOrder, supplyOptions, later, relocate, currentPlayer, takeFromSupply, returnCard,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const D = ['action', 'duration'];
const mat = (p, name) => (p.mats[name] = p.mats[name] || []);
function takeFromMat(p, name, id) {
  const m = mat(p, name);
  const i = m.indexOf(id);
  return i >= 0 ? m.splice(i, 1)[0] : null;
}
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'cove', name: '隠し港', types: D, cost: 2, main: '+1 カード\n+1 アクション', desc: '手札を 1 枚、裏向きで脇に置く。次の手番の始めに、それを手札に入れる',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '次の手番まで取っておく 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      mat(p, 'cove').push(id);
      later(g, 'cove', function* () { const c = takeFromMat(p, 'cove', id); if (c) p.hand.push(c); });
    },
  },
  {
    id: 'beacon', name: 'かがり火', types: D, cost: 2, protects: true, main: '+1 アクション\n+1 金', desc: '次の手番の始めに +1 金。それまで、他の人のアタックを受けない',
    *play(g) { g.turn.actions += 1; g.turn.money += 1; later(g, 'beacon', function* () { g.turn.money += 1; }); },
  },
  {
    id: 'shorevillage', name: '浜の集落', cost: 2, main: '+2 アクション', desc: '山札の一番上を自分のマットに裏向きで置くか、マットの札をすべて手札に入れるかを選ぶ',
    *play(g, p, pi) {
      g.turn.actions += 2;
      const m = mat(p, 'shorevillage');
      const v = !m.length ? 'put' : yield* askChoose(g, pi, `マットには ${m.length} 枚。どちらにしますか？`, [
        { value: 'put', label: '山札の上をマットへ' }, { value: 'take', label: 'マットの札を手札へ' },
      ], m);
      if (v === 'take') { p.hand.push(...m.splice(0)); return; }
      const [id] = reveal(p, 1);
      if (id != null) m.push(id);
    },
  },
  // ---- コスト 3 ----
  {
    id: 'fishtown', name: '漁師町', types: D, cost: 3, main: '+2 アクション\n+1 金', desc: '次の手番の始めに +1 アクション +1 金',
    *play(g) { g.turn.actions += 2; g.turn.money += 1; later(g, 'fishtown', function* () { g.turn.actions += 1; g.turn.money += 1; }); },
  },
  {
    id: 'overlook', name: '見晴らし台', cost: 3, main: '+1 アクション', desc: '山札の上 3 枚を見て、1 枚を廃棄、1 枚を捨て、残り 1 枚を山札の上に戻す',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const seen = reveal(p, 3);
      if (!seen.length) return;
      const [t] = yield* askCards(g, pi, '廃棄する 1 枚を選ぶ', seen, 1, 1);
      yield* trashCards(g, p, seen.splice(t ?? 0, 1));
      if (!seen.length) return;
      const [d] = yield* askCards(g, pi, '捨てる 1 枚を選ぶ', seen, 1, 1);
      yield* discardCards(g, p, seen.splice(d ?? 0, 1));
      for (const id of seen) putOnDeck(p, id);
    },
  },
  {
    id: 'contraband', name: '抜け荷', cost: 3, main: '右の人の\n獲得をまねる', desc: '右の人が前の手番に獲得した、コスト 6 以下のカードと同じものを 1 枚獲得する',
    *play(g, p, pi) {
      const right = g.players[(pi - 1 + g.players.length) % g.players.length];
      const ok = [...new Set(right.lastGains)].filter((id) => costOf(g, id) <= 6 && g.supply[id] > 0);
      if (!ok.length) { log(g, `${right.name}が前の手番に獲得した中に、もらえる札はなかった。`); return; }
      const id = yield* askSupply(g, pi, `${right.name}が獲得した札から 1 枚`, 6, (c) => ok.includes(c));
      yield* gain(g, pi, id);
    },
  },
  {
    id: 'storeroom', name: '納戸', cost: 3, main: '+3 カード\n+1 アクション', desc: '手札を 3 枚捨てる',
    *play(g, p, pi) {
      drawCards(p, 3);
      g.turn.actions += 1;
      yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚を選ぶ', 3, 3)));
    },
  },
  {
    id: 'compass', name: '羅針盤', types: ['treasure', 'duration'], cost: 3, value: 1, autoPlay: true, main: '+1 金　+1 購入', desc: '今と、次の手番の始めに：+1 金 +1 購入',
    *play(g) { g.turn.buys += 1; later(g, 'compass', function* () { g.turn.money += 1; g.turn.buys += 1; }); },
  },
  {
    id: 'gibbon', name: '手長猿', types: D, cost: 3, main: '右の人が獲得\nするたび +1 カード', desc: '次の手番まで、右の人がカードを獲得するたびに +1 カード。次の手番の始めに +1 カード',
    *play(g, p) {
      p.tokens.gibbon = (p.tokens.gibbon || 0) + 1;
      later(g, 'gibbon', function* () { p.tokens.gibbon -= 1; drawCards(p, 1); });
    },
  },
  {
    id: 'searoute', name: '航路図', cost: 3, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくる。同じ名前の札が場にあれば、それを手札に入れる',
    *play(g, p) {
      drawCards(p, 1);
      g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (g.playArea.includes(id)) { p.hand.push(id); log(g, `${p.name}が${nm(id)}を手札に入れた。`); } else putOnDeck(p, id);
    },
  },
  // ---- コスト 4 ----
  {
    id: 'wagon', name: '荷馬車', types: D, cost: 4, main: '+1 カード\n+1 アクション', desc: '次の手番の始めに +1 カード',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; later(g, 'wagon', function* () { drawCards(p, 1); }); },
  },
  {
    id: 'snatcher', name: 'ひったくり', types: ['action', 'attack'], cost: 4, main: '+2 金', desc: '他の人は手札の銅を 1 枚捨てる（なければ手札を見せる）',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const i = t.hand.indexOf('copper');
        if (i >= 0) yield* discardCards(g, t, takeFromHand(t, [i]));
        else log(g, `${t.name}の手札に銅はなかった。`);
      });
    },
  },
  {
    id: 'islet', name: '小島', types: ['action', 'victory'], cost: 4, points: 2, main: '2 点', desc: 'このカードと手札 1 枚を、小島マットに置く（ゲームの終わりまで残り、点に数える）',
    *play(g, p, pi) {
      const at = g.playArea.lastIndexOf('islet');
      if (at >= 0) mat(p, 'islet').push(...g.playArea.splice(at, 1));
      const [i] = yield* askHand(g, pi, '小島マットに置く 1 枚を選ぶ', 1, 1);
      if (i != null) mat(p, 'islet').push(...takeFromHand(p, [i]));
    },
  },
  {
    id: 'salvor', name: '引き上げ屋', cost: 4, main: '+1 購入', desc: '手札を 1 枚廃棄し、そのコストだけ +金',
    *play(g, p, pi) {
      g.turn.buys += 1;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ', 1, 1);
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* trashCards(g, p, [id]);
      g.turn.money += costOf(g, id);
    },
  },
  {
    id: 'oldmap', name: '宝の絵図', cost: 4, main: '2 枚そろえば\n金 4 枚', desc: 'このカードと手札の宝の絵図 1 枚を廃棄する。2 枚とも廃棄したら、金を 4 枚山札の上に獲得する',
    *play(g, p, pi) {
      const self = yield* trashSelf(g, p, 'oldmap');
      const i = p.hand.indexOf('oldmap');
      if (i < 0) return;
      yield* trashCards(g, p, takeFromHand(p, [i]));
      if (self) for (let k = 0; k < 4; k++) yield* gain(g, pi, 'gold', 'deck');
    },
  },
  {
    id: 'barricade', name: '通せんぼ', types: ['action', 'duration', 'attack'], cost: 4, main: 'カードを獲得\n（次の手番に手札へ）',
    desc: 'コスト 4 以下を 1 枚獲得し脇に置く。次の手番の始めに手札へ。脇にあるあいだ、他の人が自分の手番に同じ札を獲得すると災いも獲得する',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下を 1 枚獲得（脇に置く）', 4);
      const got = id && takeFromSupply(g, id);
      if (!got) return;
      g.turn.gained.push(got);
      log(g, `${p.name}が${nm(got)}を獲得して脇に置いた。`);
      mat(p, 'barricade').push(got);
      const affected = [];
      yield* attackOthers(g, function* (ti) { affected.push(ti); });
      const entry = { owner: pi, id: got, affected };
      (g.barricades = g.barricades || []).push(entry);
      later(g, 'barricade', function* () {
        g.barricades.splice(g.barricades.indexOf(entry), 1);
        const c = takeFromMat(p, 'barricade', got);
        if (c) p.hand.push(c);
      });
    },
  },
  {
    id: 'deckhand', name: '水夫', types: D, cost: 4, main: '+1 アクション', desc: 'この手番に 1 度、持続カードを獲得したとき、それを使ってよい。次の手番の始めに +2 金、手札を 1 枚廃棄してよい',
    *play(g, p, pi) {
      g.turn.actions += 1;
      g.turn.deckhand = (g.turn.deckhand || 0) + 1;
      later(g, 'deckhand', function* () {
        g.turn.money += 2;
        const [i] = yield* askHand(g, pi, '廃棄する 1 枚を選ぶ（しなくてもよい）', 0, 1);
        if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
      });
    },
  },
  {
    id: 'rockpool', name: '磯', types: D, cost: 4, main: '+3 カード\n+1 アクション', desc: '次の手番の始めに、手札を 2 枚捨てる',
    *play(g, p, pi) {
      drawCards(p, 3);
      g.turn.actions += 1;
      later(g, 'rockpool', function* () { yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2))); });
    },
  },
  // ---- コスト 5 ----
  {
    id: 'openmarket', name: '朝市', cost: 5, main: '+1 カード\n+2 アクション　+1 金', desc: '',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 2; g.turn.money += 1; },
  },
  {
    id: 'tradeship', name: '交易船', types: D, cost: 5, main: '+2 金', desc: '今と、次の手番の始めに +2 金',
    *play(g) { g.turn.money += 2; later(g, 'tradeship', function* () { g.turn.money += 2; }); },
  },
  {
    id: 'fort', name: '出城', types: D, cost: 5, main: '追加の手番', desc: 'この手番のあとに、手札 3 枚で追加の手番を行う（追加の手番の中では起きない）',
    *play(g) {
      if (g.extraTurn || g.turn.outpost) return;
      g.turn.outpost = true;
      later(g, 'fort', function* () {});
    },
  },
  {
    id: 'strategist', name: '軍師', types: D, cost: 5, main: '手札を捨てて\n次の手番に備える', desc: '手札があれば全部捨てる。そうしたら次の手番の始めに +5 カード +1 アクション +1 購入',
    *play(g, p) {
      if (!p.hand.length) return;
      yield* discardCards(g, p, p.hand.splice(0));
      later(g, 'strategist', function* () { drawCards(p, 5); g.turn.actions += 1; g.turn.buys += 1; });
    },
  },
  {
    id: 'coffer', name: '金蔵', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: 'この手番に勝利点カードを獲得していなければ、片付けのときに山札の上に戻してよい',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1; },
    *onCleanup(g, p, pi) {
      if (g.turn.gained.some((id) => is(id, 'victory'))) return;
      if (!(yield* askYesNo(g, pi, '「金蔵」を山札の上に戻しますか？', '戻す', '戻さない', ['coffer']))) return;
      const at = g.playArea.indexOf('coffer');
      if (at >= 0) putOnDeck(p, g.playArea.splice(at, 1)[0]);
    },
  },
  {
    id: 'pier', name: '波止場', types: D, cost: 5, main: '+2 カード\n+1 購入', desc: '今と、次の手番の始めに +2 カード +1 購入',
    *play(g, p) { drawCards(p, 2); g.turn.buys += 1; later(g, 'pier', function* () { drawCards(p, 2); g.turn.buys += 1; }); },
  },
  {
    id: 'privateer', name: '私掠船', types: ['action', 'duration', 'attack'], cost: 5, main: '+2 金', desc: '次の手番の始めに +1 カード。それまで他の人は、各手番に最初に出した銀か金を廃棄する',
    *play(g, p) {
      g.turn.money += 2;
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.privateer = (g.players[ti].tokens.privateer || 0) + 1; });
      later(g, 'privateer', function* () {
        for (const ti of hit) g.players[ti].tokens.privateer -= 1;
        drawCards(p, 1);
      });
    },
  },
  {
    id: 'buccaneer', name: '海の荒くれ', types: ['action', 'duration', 'reaction'], cost: 5, main: '財宝を手札に', desc: '次の手番の始めに、コスト 6 以下の財宝を 1 枚手札に獲得する。誰かが財宝を獲得したとき、手札から使ってよい',
    *play(g, p, pi) { later(g, 'buccaneer', buccaneerJob(p, pi)); },
  },
  {
    id: 'siren', name: '人魚の呪い', types: ['action', 'duration', 'attack'], cost: 5, main: '+2 カード', desc: '他の人は災いを獲得する。次の手番の始めに +2 カード、そのあと手札を 2 枚捨てる',
    *play(g, p, pi) {
      drawCards(p, 2);
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, 'curse'); });
      later(g, 'siren', function* () {
        drawCards(p, 2);
        yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚を選ぶ', 2, 2)));
      });
    },
  },
];

function buccaneerJob(p, pi) {
  return function* (g) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 6 以下の財宝を手札に獲得', 6, (c) => is(c, 'treasure')), 'hand'); };
}

// ---- どのカードにも関わる決まり ----
HOOKS.gain.push(function* (g, got) {
  const n = g.players.length;
  // 通せんぼ: 脇にある札と同じ札を、影響を受ける人が自分の手番に獲得したら災い
  for (const b of g.barricades || []) {
    if (got.id === b.id && got.pi === g.current && got.pi !== b.owner && b.affected.includes(got.pi)) {
      log(g, `${g.players[got.pi].name}は通せんぼで災いも獲得する。`);
      yield* gain(g, got.pi, 'curse');
    }
  }
  // 手長猿: 自分の右の人（自分の前の席）が獲得するたびに +1 カード
  for (let k = 0; k < n; k++) {
    const owner = g.players[k];
    if (owner.tokens.gibbon > 0 && got.pi === (k - 1 + n) % n) drawCards(owner, owner.tokens.gibbon);
  }
  // 海の荒くれ: 誰かが財宝を獲得したとき、手札から使ってよい
  if (is(got.id, 'treasure')) {
    for (let k = 0; k < n; k++) {
      const pi = (g.current + k) % n;
      const q = g.players[pi];
      if (!q.hand.includes('buccaneer')) continue;
      if (!(yield* askYesNo(g, pi, `${g.players[got.pi].name}が財宝を獲得した。「海の荒くれ」を使いますか？`, '使う', '使わない', ['buccaneer']))) continue;
      q.hand.splice(q.hand.indexOf('buccaneer'), 1);
      log(g, `${q.name}が「海の荒くれ」を使用。`);
      if (pi === g.current) { g.playArea.push('buccaneer'); later(g, 'buccaneer', buccaneerJob(q, pi)); } else { q.inPlay.push('buccaneer'); q.nextTurn.push(buccaneerJob(q, pi)); }
    }
  }
});

HOOKS.treasure.push(function* (g, id) {
  const p = currentPlayer(g);
  // 私掠船: その手番で最初に出した銀か金を廃棄（お金は入る）
  if (p.tokens.privateer > 0 && !g.turn.privateerDone && (id === 'silver' || id === 'gold')) {
    g.turn.privateerDone = true;
    yield* trashSelf(g, p, id);
  }
});

// 水夫: この手番に 1 度、持続カードを獲得したら使ってよい
kingdom.find((c) => c.id === 'deckhand').whenGain = function* (g, got) {
  if (!(g.turn.deckhand > 0) || got.pi !== g.current || !is(got.id, 'duration') || !is(got.id, 'action')) return;
  if (!(yield* askYesNo(g, got.pi, `獲得した${nm(got.id)}を今すぐ使いますか？`, '使う', '使わない', [got.id]))) return;
  if (!(yield* relocate(g, got, 'gone'))) return;
  g.turn.deckhand -= 1;
  g.playArea.push(got.id);
  log(g, `${currentPlayer(g).name}が${nm(got.id)}を使用。`);
  yield* resolve(g, got.id);
};

const firstEdition = [
  {
    id: 'diver', name: '海女', cost: 2, main: '+1 カード\n+1 アクション', desc: '山札の一番下を見て、一番上に移してよい',
    *play(g, p, pi) {
      drawCards(p, 1);
      g.turn.actions += 1;
      if (!p.deck.length) return;
      const id = p.deck[0];
      if (yield* askYesNo(g, pi, `山札の一番下は${nm(id)}。一番上に移しますか？`, '移す', 'そのまま', [id])) p.deck.push(p.deck.shift());
    },
  },
  {
    id: 'injunction', name: '差し止め', cost: 2, main: '+2 金', desc: 'このカードを廃棄し、サプライの山 1 つに印を置く。印のある山のカードを買うと、印 1 つにつき災いを獲得する',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* trashSelf(g, p, 'injunction');
      const piles = Object.keys(g.supply);
      const [i] = yield* askCards(g, pi, '印を置く山を選ぶ', piles, 1, 1);
      const id = piles[i ?? 0];
      g.embargo[id] = (g.embargo[id] || 0) + 1;
      log(g, `${p.name}が${nm(id)}の山に印を置いた。`);
    },
  },
  {
    id: 'emissary', name: '特使', types: ['action', 'attack'], cost: 3, main: 'カードを押しつける', desc: '手札を 1 枚見せ、同じ札を手札から 2 枚までサプライに戻す。他の人はその札を 1 枚ずつ獲得する',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '見せる 1 枚を選ぶ', 1, 1, (id) => g.supply[id] != null);
      if (i == null) return;
      const id = p.hand[i];
      const same = p.hand.map((c, k) => (c === id ? k : -1)).filter((k) => k >= 0);
      const max = Math.min(2, same.length);
      const n = yield* askChoose(g, pi, `${nm(id)}を何枚サプライに戻しますか？`, Array.from({ length: max + 1 }, (_, k) => ({ value: max - k, label: `${max - k} 枚` })), [id]);
      for (const c of takeFromHand(p, same.slice(0, n))) returnCard(g, c);
      if (n) log(g, `${p.name}が${nm(id)}を ${n} 枚サプライに戻した。`);
      yield* attackOthers(g, function* (ti) { yield* gain(g, ti, id); });
    },
  },
  {
    id: 'pilot', name: '水先案内', cost: 4, main: '+2 金', desc: '山札の上 5 枚を見て、すべて捨てるか、好きな順に戻すかを選ぶ',
    *play(g, p, pi) {
      g.turn.money += 2;
      const seen = reveal(p, 5);
      if (!seen.length) return;
      if (yield* askYesNo(g, pi, '見た札をすべて捨てますか？', '全部捨てる', '戻す', seen)) yield* discardCards(g, p, seen);
      else yield* putBackInOrder(g, pi, seen);
    },
  },
  {
    id: 'raidship', name: '略奪船', types: ['action', 'attack'], cost: 4, main: '財宝を奪うか\n貯めた分 +金', desc: '他の人の山札の上 2 枚から財宝を 1 枚ずつ廃棄させ、誰かが廃棄したらコインの印を 1 つ得る。または印 1 つにつき +1 金',
    *play(g, p, pi) {
      const coins = p.tokens.raidship || 0;
      const v = yield* askChoose(g, pi, 'どちらにしますか？', [{ value: 'raid', label: '財宝を奪う' }, { value: 'coin', label: `+${coins} 金` }]);
      if (v === 'coin') { g.turn.money += coins; return; }
      let any = false;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const shown = reveal(t, 2);
        const idx = shown.map((id, i) => (is(id, 'treasure') ? i : -1)).filter((i) => i >= 0);
        if (idx.length) {
          const pick = idx.length === 1 || shown[idx[0]] === shown[idx[1]] ? idx[0]
            : idx[(yield* askCards(g, pi, `${t.name}の財宝から廃棄する 1 枚`, idx.map((i) => shown[i]), 1, 1))[0] ?? 0];
          yield* trashCards(g, t, shown.splice(pick, 1));
          any = true;
        }
        yield* discardCards(g, t, shown, true);
      });
      if (any) { p.tokens.raidship = coins + 1; log(g, `${p.name}がコインの印を得た（${coins + 1}）。`); }
    },
  },
  {
    id: 'crone', name: '磯の老婆', types: ['action', 'attack'], cost: 4, main: '災いを山札に', desc: '他の人は山札の一番上を捨て、災いを 1 枚山札の上に獲得する',
    *play(g) {
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id != null) yield* discardCards(g, t, [id], true);
        yield* gain(g, ti, 'curse', 'deck');
      });
    },
  },
  {
    id: 'pioneer', name: '開墾者', cost: 5, main: '財宝を手札に', desc: '手札の領地を見せてよい。見せたら金を、見せなければ銀を、手札に獲得する',
    *play(g, p, pi) {
      const show = p.hand.includes('province') && (yield* askYesNo(g, pi, '領地を見せて金をもらいますか？', '見せる', '見せない', ['province']));
      yield* gain(g, pi, show ? 'gold' : 'silver', 'hand');
    },
  },
  {
    id: 'fogship', name: '霧の船', types: ['action', 'attack'], cost: 5, main: '+2 カード', desc: '手札が 4 枚以上の他の人は、3 枚になるまで手札を山札の上に置く',
    *play(g, p) {
      drawCards(p, 2);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const need = t.hand.length - 3;
        if (need <= 0) return;
        const idx = yield* askHand(g, ti, `山札の上に置く ${need} 枚を選ぶ`, need, need);
        yield* putBackInOrder(g, ti, takeFromHand(t, idx));
      });
    },
  },
].map((c) => ({ ...c, set: 'seaside1' }));

defineCards({ id: 'seaside', name: '海辺' }, kingdom, [
  { id: 'highseas', name: '外海', cards: ['openmarket', 'wagon', 'shorevillage', 'fort', 'contraband', 'coffer', 'pier', 'overlook', 'islet', 'buccaneer'] },
  { id: 'buriedtreasure', name: '埋もれた宝', cards: ['oldmap', 'cove', 'salvor', 'fishtown', 'compass', 'strategist', 'tradeship', 'searoute', 'storeroom', 'snatcher'] },
  { id: 'shipwrecks', name: '難破船', cards: ['siren', 'privateer', 'barricade', 'gibbon', 'deckhand', 'rockpool', 'beacon', 'islet', 'cove', 'openmarket'] },
  { id: 'reachforthetide', name: '潮に手を（基本と混ぜる）', cards: ['archive', 'market', 'sentinel', 'craftsman', 'command', 'wagon', 'fishtown', 'tradeship', 'pier', 'overlook'] },
]);
defineCards({ id: 'seaside1', name: '海辺（初版）' }, firstEdition, [
  { id: 'seasideclassic', name: '初版の海辺', cards: ['diver', 'injunction', 'emissary', 'pilot', 'raidship', 'crone', 'pioneer', 'fogship', 'openmarket', 'fishtown'] },
]);
