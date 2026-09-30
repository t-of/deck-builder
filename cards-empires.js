'use strict';
// 拡張「帝国」のカード（王国 24 山: 単独 19・上下で 2 種の山 5・城 8 種）、イベント 13 種、ランドマーク 21 種。名前は本家と別の言い回し。
// debt: コストのうち借金の数（買うと借金トークンを受け取る）。上下で 2 種の山と城は、重なった山（game.stacks）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  treasureEffect, later, relocate, returnCard, supplyOptions, pileOf, currentPlayer, allCards, shuffle, payDebt,
  takeFromSupply,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const vp = (g, p, n) => { if (!n) return; p.tokens.vp = (p.tokens.vp || 0) + n; log(g, `${p.name}が勝利点トークンを ${n} 得た。`); };
const T = ['treasure'];
const G = ['action', 'gathering'];
const lm = (g, id) => g.landscapes.includes(id);
function takeLm(g, p, id, n) {
  const k = Math.min(n, g.landmarkVP[id] || 0);
  if (!k) return;
  g.landmarkVP[id] -= k;
  vp(g, p, k);
}
function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
function* playTwice(g, p, pi, purpose, pred) {
  const [i] = yield* askHand(g, pi, purpose, 0, 1, pred);
  if (i == null) return false;
  const [id] = takeFromHand(p, [i]);
  g.playArea.push(id);
  log(g, `${p.name}が${nm(id)}を 2 回使う。`);
  const before = p.nextTurn.length;
  for (let k = 0; k < 2; k++) { if (is(id, 'action') && g.turn.phase === 'action') yield* resolve(g, id); else yield* treasureEffect(g, id); }
  return p.nextTurn.length > before;
}

// ---- 上下で 2 種の山（上の 5 枚・下の 5 枚） ----
const SPLIT = {
  p_settlers: ['colonist', 'busyvillage'],
  p_catapult: ['trebuchet', 'pebbles'],
  p_patrician: ['notable', 'emporium'],
  p_encampment: ['bivouac', 'spoil'],
  p_gladiator: ['fightman', 'fortune'],
};
const splitPiles = [
  { id: 'p_settlers', name: '入植者／にぎわう村', cost: 2, main: '上下 2 種の山', desc: '上に入植者 5 枚、下ににぎわう村 5 枚。一番上の札だけ買える' },
  { id: 'p_catapult', name: '石弓／石ころ', types: ['action', 'attack'], cost: 3, main: '上下 2 種の山', desc: '上に石弓 5 枚、下に石ころ 5 枚。一番上の札だけ買える' },
  { id: 'p_patrician', name: '名士／大商店', cost: 2, main: '上下 2 種の山', desc: '上に名士 5 枚、下に大商店 5 枚。一番上の札だけ買える' },
  { id: 'p_encampment', name: '野営／戦利の品', cost: 2, main: '上下 2 種の山', desc: '上に野営 5 枚、下に戦利の品 5 枚。一番上の札だけ買える' },
  { id: 'p_gladiator', name: '闘士／一財産', cost: 3, main: '上下 2 種の山', desc: '上に闘士 5 枚、下に一財産 5 枚。一番上の札だけ買える' },
];
const inSplit = (pile) => ({ pile, notSupply: true });
const splitCards = [
  {
    id: 'colonist', ...inSplit('p_settlers'), name: '入植者', cost: 2, main: '+1 カード\n+1 アクション', desc: '捨て札の銅を 1 枚、手札に入れてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      if (p.discard.includes('copper') && (yield* askYesNo(g, pi, '捨て札の銅を手札に入れますか？', '入れる', 'しない', ['copper']))) p.hand.push(...p.discard.splice(p.discard.indexOf('copper'), 1));
    },
  },
  {
    id: 'busyvillage', ...inSplit('p_settlers'), name: 'にぎわう村', cost: 5, main: '+1 カード\n+3 アクション', desc: '捨て札の入植者を 1 枚、手札に入れてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 3;
      if (p.discard.includes('colonist') && (yield* askYesNo(g, pi, '捨て札の入植者を手札に入れますか？', '入れる', 'しない', ['colonist']))) p.hand.push(...p.discard.splice(p.discard.indexOf('colonist'), 1));
    },
  },
  {
    id: 'trebuchet', ...inSplit('p_catapult'), name: '石弓', types: ['action', 'attack'], cost: 3, main: '+1 金', desc: '手札を 1 枚廃棄する。コスト 3 以上なら他の人は災いを獲得。財宝なら他の人は手札が 3 枚になるまで捨てる',
    *play(g, p, pi) {
      g.turn.money += 1;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (id) yield* trashCards(g, p, [id]);
      yield* attackOthers(g, function* (ti) {
        if (!id) return;
        if (costOf(g, id) >= 3) yield* gain(g, ti, 'curse');
        if (is(id, 'treasure')) yield* discardDownTo(g, ti, 3);
      });
    },
  },
  {
    id: 'pebbles', ...inSplit('p_catapult'), name: '石ころ', types: T, cost: 4, value: 1, main: '+1 金', desc: '獲得したとき・廃棄したとき、銀を獲得する（購入フェイズなら山札の上、ほかは手札へ）',
    *onGain(g, got) { yield* gain(g, got.pi, 'silver', got.pi === g.current && g.turn.phase === 'buy' ? 'deck' : 'hand'); },
    *onTrash(g, p, pi) { yield* gain(g, pi, 'silver', pi === g.current && g.turn.phase === 'buy' ? 'deck' : 'hand'); },
  },
  {
    id: 'notable', ...inSplit('p_patrician'), name: '名士', cost: 2, main: '+1 カード\n+1 アクション', desc: '山札の一番上をめくり、コスト 5 以上なら手札に入れる',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (costOf(g, id) >= 5) p.hand.push(id); else putOnDeck(p, id);
    },
  },
  {
    id: 'emporium', ...inSplit('p_patrician'), name: '大商店', cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: 'これを獲得したとき、場にアクションが 5 枚以上あれば +2 勝利点トークン',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1; },
    *onGain(g, got) { if (got.pi === g.current && g.playArea.filter((id) => is(id, 'action')).length >= 5) vp(g, g.players[got.pi], 2); },
  },
  {
    id: 'bivouac', ...inSplit('p_encampment'), name: '野営', cost: 2, main: '+2 カード\n+2 アクション', desc: '手札の金か戦利の品を見せてよい。見せなければ、片付けの始めにこれを山に戻す',
    *play(g, p, pi) {
      drawCards(p, 2); g.turn.actions += 2;
      const can = p.hand.some((id) => id === 'gold' || id === 'spoil');
      if (can && (yield* askYesNo(g, pi, '金か戦利の品を見せますか？', '見せる', '見せない'))) return;
      g.turn.bivouacBack = (g.turn.bivouacBack || 0) + 1;
    },
    *onCleanup(g) {
      while (g.turn.bivouacBack > 0 && g.playArea.includes('bivouac')) {
        g.turn.bivouacBack -= 1;
        const [c] = g.playArea.splice(g.playArea.indexOf('bivouac'), 1);
        if (!returnCard(g, c)) currentPlayer(g).discard.push(c); // 山がなくなっていれば捨て札へ
      }
    },
  },
  { id: 'spoil', ...inSplit('p_encampment'), name: '戦利の品', types: T, cost: 5, value: 2, autoPlay: true, main: '+2 金\n+1 勝利点トークン', desc: '', *play(g, p) { vp(g, p, 1); } },
  {
    id: 'fightman', ...inSplit('p_gladiator'), name: '闘士', cost: 3, main: '+2 金', desc: '手札を 1 枚見せる。左の人が同じ札を見せなければ、+1 金して、サプライの闘士を 1 枚廃棄する',
    *play(g, p, pi) {
      g.turn.money += 2;
      const [i] = yield* askHand(g, pi, '見せる 1 枚', 1, 1);
      if (i == null) return;
      const id = p.hand[i];
      const li = (pi + 1) % g.players.length;
      const left = g.players[li];
      if (left.hand.includes(id) && (yield* askYesNo(g, li, `${p.name}が${nm(id)}を見せた。同じ札を見せますか？`, '見せる', '見せない', [id]))) return;
      g.turn.money += 1;
      const st = g.stacks.p_gladiator;
      if (st && st.at(-1) === 'fightman') yield* trashCards(g, p, [takeFromSupply(g, 'p_gladiator')]);
    },
  },
  {
    id: 'fortune', ...inSplit('p_gladiator'), name: '一財産', types: T, cost: 8, debt: 8, main: '+1 購入\nお金を 2 倍', desc: '1 手番に 1 度、お金を 2 倍にする。獲得したとき、場の闘士 1 枚につき金を獲得する',
    *play(g) { g.turn.buys += 1; if (!g.turn.fortuneUsed) { g.turn.fortuneUsed = true; g.turn.money *= 2; } },
    *onGain(g, got) { if (got.pi === g.current) for (const id of g.playArea) if (id === 'fightman') yield* gain(g, got.pi, 'gold'); },
  },
];

// ---- 城（コストの安い順に重ねた山） ----
const castle = (id, name, types, cost, main, desc, more = {}) => ({ id, pile: 'castles', notSupply: true, name, types: [...types, 'castle'], cost, main, desc, ...more });
const castleCount = (all) => all.filter((id) => is(id, 'castle')).length;
const castles = [
  castle('c_humble', 'あばら城', ['treasure', 'victory'], 3, '+1 金', '持っている城 1 枚につき 1 点', { value: 1, pointsFn: castleCount }),
  castle('c_crumbling', '朽ちた城', ['victory'], 4, '1 点', '獲得したとき・廃棄したとき、+1 勝利点トークンと銀を獲得', {
    points: 1,
    *onGain(g, got) { vp(g, g.players[got.pi], 1); yield* gain(g, got.pi, 'silver'); },
    *onTrash(g, p, pi) { vp(g, p, 1); yield* gain(g, pi, 'silver'); },
  }),
  castle('c_small', 'こぢんまり城', ['action', 'victory'], 5, '城を格上げ', 'これか手札の城を廃棄する。廃棄したら城を 1 枚獲得する。2 点', {
    points: 2,
    *play(g, p, pi) {
      const v = !p.hand.some((id) => is(id, 'castle')) ? 'self' : yield* askChoose(g, pi, 'どれを廃棄しますか？', [{ value: 'self', label: 'このこぢんまり城' }, { value: 'hand', label: '手札の城' }]);
      let ok = false;
      if (v === 'self') ok = yield* trashSelf(g, p, 'c_small');
      else { const [i] = yield* askHand(g, pi, '廃棄する城', 1, 1, (id) => is(id, 'castle')); if (i != null) { yield* trashCards(g, p, takeFromHand(p, [i])); ok = true; } }
      if (ok) yield* gain(g, pi, 'castles');
    },
  }),
  castle('c_haunted', '亡霊の城', ['victory'], 6, '2 点', '自分の手番に獲得したとき、金を獲得し、手札が 5 枚以上の他の人は 2 枚を山札の上に置く', {
    points: 2,
    *onGain(g, got) {
      if (got.pi !== g.current) return;
      yield* gain(g, got.pi, 'gold');
      const n = g.players.length;
      for (let k = 1; k < n; k++) {
        const ti = (got.pi + k) % n;
        const t = g.players[ti];
        if (t.hand.length >= 5) for (const id of takeFromHand(t, yield* askHand(g, ti, '山札の上に置く 2 枚', 2, 2))) putOnDeck(t, id);
      }
    },
  }),
  castle('c_opulent', 'きらびやか城', ['action', 'victory'], 7, '勝利点を捨てて\n+2 金ずつ', '好きな枚数の勝利点カードを捨て、1 枚につき +2 金。3 点', {
    points: 3,
    *play(g, p, pi) {
      const idx = yield* askHand(g, pi, '捨てる勝利点カード（好きな枚数）', 0, p.hand.length, (id) => is(id, 'victory'));
      yield* discardCards(g, p, takeFromHand(p, idx));
      g.turn.money += 2 * idx.length;
    },
  }),
  castle('c_sprawling', 'だだっ広い城', ['victory'], 8, '4 点', '獲得したとき、荘園 1 枚か小屋 3 枚を獲得する', {
    points: 4,
    *onGain(g, got) {
      if (yield* askYesNo(g, got.pi, 'どちらを獲得しますか？', '荘園 1 枚', '小屋 3 枚')) yield* gain(g, got.pi, 'duchy');
      else for (let k = 0; k < 3; k++) yield* gain(g, got.pi, 'estate');
    },
  }),
  castle('c_grand', '堂々たる城', ['victory'], 9, '5 点', '獲得したとき、手札を見せ、手札と場の勝利点カード 1 枚につき +1 勝利点トークン', {
    points: 5,
    *onGain(g, got) {
      const p = g.players[got.pi];
      vp(g, p, p.hand.filter((id) => is(id, 'victory')).length + (got.pi === g.current ? g.playArea.filter((id) => is(id, 'victory')).length : 0));
    },
  }),
  castle('c_king', '王の城', ['victory'], 10, '城 1 枚につき 2 点', '持っている城 1 枚につき 2 点', { pointsFn: (all) => 2 * castleCount(all) }),
];

const kingdom = [
  ...splitPiles,
  { id: 'castles', name: '城々', types: ['victory', 'castle'], cost: 3, main: '城の山', desc: '8 種の城をコストの安い順に重ねた山。一番上の城だけ買える' },
  {
    id: 'chariot', name: '馬車競べ', cost: 3, main: '+1 アクション', desc: '山札の一番上を手札に入れる。左の人も山札の一番上をめくり、あなたの札のほうが高ければ +1 金 +1 勝利点トークン',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [mine] = reveal(p, 1);
      if (mine == null) return;
      p.hand.push(mine);
      const left = g.players[(pi + 1) % g.players.length];
      const [theirs] = reveal(left, 1);
      if (theirs != null) putOnDeck(left, theirs);
      if (theirs == null || costOf(g, mine) > costOf(g, theirs)) { g.turn.money += 1; vp(g, p, 1); }
    },
  },
  {
    id: 'temptress', name: '魔性の女', types: ['action', 'attack', 'duration'], cost: 3, main: '次の手番に\n+2 カード', desc: '次の手番の始めまで、他の人がその手番に最初に使うアクションは、効果の代わりに +1 カード +1 アクションになる。次の手番の始めに +2 カード',
    *play(g, p) {
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.enchanted = (g.players[ti].tokens.enchanted || 0) + 1; });
      later(g, 'temptress', function* () { for (const ti of hit) g.players[ti].tokens.enchanted -= 1; drawCards(p, 2); });
    },
  },
  {
    id: 'vegmarket', name: '野菜市', types: G, cost: 3, main: '+1 購入', desc: 'この山の勝利点トークンが 4 以上なら、それを受け取りこれを廃棄する。そうでなければ山に 1 つ足し、山のトークン 1 つにつき +1 金',
    *play(g, p) {
      g.turn.buys += 1;
      if ((g.pileVP.vegmarket || 0) >= 4) { vp(g, p, g.pileVP.vegmarket); g.pileVP.vegmarket = 0; yield* trashSelf(g, p, 'vegmarket'); return; }
      g.pileVP.vegmarket = (g.pileVP.vegmarket || 0) + 1;
      g.turn.money += g.pileVP.vegmarket;
    },
  },
  {
    id: 'mechanic', name: '技師', cost: 0, debt: 4, main: 'コスト 4 以下を獲得', desc: 'コスト 4 以下を獲得する。これを廃棄してよい。そうしたら、もう 1 枚コスト 4 以下を獲得する',
    *play(g, p, pi) {
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4));
      if (g.playArea.includes('mechanic') && (yield* askYesNo(g, pi, '技師を廃棄して、もう 1 枚獲得しますか？', '廃棄する', 'しない'))) {
        if (yield* trashSelf(g, p, 'mechanic')) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4));
      }
    },
  },
  {
    id: 'oblation', name: '捧げ物', cost: 4, main: '廃棄して得をする', desc: '手札を 1 枚廃棄する。アクションなら +2 カード +2 アクション、財宝なら +2 金、勝利点なら +2 勝利点トークン',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (is(id, 'action')) { drawCards(p, 2); g.turn.actions += 2; }
      if (is(id, 'treasure')) g.turn.money += 2;
      if (is(id, 'victory')) vp(g, p, 2);
    },
  },
  {
    id: 'shrine', name: 'お社', types: G, cost: 4, main: '+1 勝利点トークン', desc: 'ちがう名前の手札を 1〜3 枚廃棄する。この山に勝利点トークンを 1 つ足す。これを獲得したとき、この山のトークンをすべて受け取る',
    *play(g, p, pi) {
      vp(g, p, 1);
      const picked = [];
      for (let k = 0; k < 3; k++) {
        const [i] = yield* askHand(g, pi, `廃棄する札（ちがう名前・${k + 1}/3${k ? '、やめてもよい' : ''}）`, k ? 0 : 1, 1, (id) => !picked.includes(id));
        if (i == null) break;
        const [id] = takeFromHand(p, [i]);
        picked.push(id);
      }
      yield* trashCards(g, p, picked);
      g.pileVP.shrine = (g.pileVP.shrine || 0) + 1;
    },
    *onGain(g, got) { vp(g, g.players[got.pi], g.pileVP.shrine || 0); g.pileVP.shrine = 0; },
  },
  {
    id: 'villa', name: '別荘', cost: 4, main: '+2 アクション　+1 購入\n+1 金', desc: 'これを獲得したとき、手札に入れて +1 アクション。購入フェイズならアクションフェイズに戻る',
    *play(g) { g.turn.actions += 2; g.turn.buys += 1; g.turn.money += 1; },
    *onGain(g, got) {
      yield* relocate(g, got, 'hand');
      if (got.pi !== g.current) return;
      g.turn.actions += 1;
      if (g.turn.phase === 'buy') { g.turn.phase = 'action'; log(g, 'アクションフェイズに戻った。'); }
    },
  },
  {
    id: 'archivist', name: '書庫番', types: ['action', 'duration'], cost: 5, main: '+1 アクション', desc: '山札の上 3 枚を脇に置く。今と次の 2 回の手番の始めに、その中の 1 枚を手札に入れる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const aside = reveal(p, 3);
      (p.mats.archivist = p.mats.archivist || []).push(...aside);
      const pick = function* () {
        const left = aside.filter(Boolean);
        if (!left.length) return;
        const [i] = yield* askCards(g, pi, '手札に入れる 1 枚', left, 1, 1);
        const id = left[i ?? 0];
        aside.splice(aside.indexOf(id), 1);
        p.mats.archivist.splice(p.mats.archivist.indexOf(id), 1);
        p.hand.push(id);
        if (aside.length) later(g, 'archivist', pick);
      };
      yield* pick();
    },
  },
  {
    id: 'principal', name: '元金', types: T, cost: 5, value: 6, autoPlay: true, main: '+6 金　+1 購入', desc: '場から捨てるとき、借金 6 を受け取る（そのあと返してよい）',
    *play(g) { g.turn.buys += 1; },
    *onCleanup(g, p) {
      for (const id of g.playArea) if (id === 'principal') p.tokens.debt = (p.tokens.debt || 0) + 6;
      payDebt(g);
    },
  },
  {
    id: 'luckycharm', name: '縁起物', types: T, cost: 5, main: '+1 購入 +2 金 か\n同じコストをもう 1 枚', desc: '+1 購入 +2 金か、「この手番、次にカードを買うとき、同じコストのちがう札を 1 枚獲得してよい」を選ぶ',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'coin', label: '+1 購入 +2 金' }, { value: 'copy', label: '次の購入で同じコストをもう 1 枚' }]);
      if (v === 'coin') { g.turn.buys += 1; g.turn.money += 2; } else g.turn.luckycharm = (g.turn.luckycharm || 0) + 1;
    },
  },
  {
    id: 'scepter', name: '玉冠', types: ['action', 'treasure'], cost: 5, main: '2 回使う', desc: 'アクションフェイズなら手札のアクションを 1 枚 2 回、購入フェイズなら手札の財宝を 1 枚 2 回使ってよい',
    *play(g, p, pi) {
      if (g.turn.phase === 'action') { if (yield* playTwice(g, p, pi, '2 回使うアクション（なしでもよい）', (id) => is(id, 'action'))) g.turn.stay.push('scepter'); }
      else yield* playTwice(g, p, pi, '2 回使う財宝（なしでもよい）', (id) => is(id, 'treasure'));
    },
  },
  {
    id: 'meetinghall', name: '寄り合い所', cost: 5, main: '+3 カード\n+1 アクション', desc: '手札を 2 枚捨てる。これを買ったとき +1 購入',
    *play(g, p, pi) { drawCards(p, 3); g.turn.actions += 1; yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚', 2, 2))); },
    *onBuy(g) { g.turn.buys += 1; },
  },
  {
    id: 'gardener', name: '植木屋', cost: 5, main: '+1 カード\n+1 アクション', desc: '場にあるあいだ、勝利点カードを獲得するたびに +1 勝利点トークン',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; },
    *whenGain(g, got) { if (is(got.id, 'victory')) vp(g, g.players[got.pi], 1); },
  },
  {
    id: 'hoplite', name: '重装兵', types: ['action', 'attack'], cost: 5, main: '+3 金', desc: '手札の金を見せてよい。見せたら、他の人は手札が 2 枚になるまで捨て、1 枚引く',
    *play(g, p, pi) {
      g.turn.money += 3;
      const show = p.hand.includes('gold') && (yield* askYesNo(g, pi, '金を見せますか？', '見せる', '見せない', ['gold']));
      yield* attackOthers(g, function* (ti) { if (show) { yield* discardDownTo(g, ti, 2); drawCards(g.players[ti], 1); } });
    },
  },
  {
    id: 'wildchase', name: '狩り立て', types: G, cost: 5, main: '+3 カード か\n小屋で総取り', desc: '「+3 カード、この山に勝利点トークンを 1 つ足す」か「小屋を獲得し、獲得したらこの山のトークンをすべて受け取る」',
    *play(g, p, pi) {
      if (yield* askYesNo(g, pi, 'どちらにしますか？', '+3 カード', '小屋を獲得して総取り')) { drawCards(p, 3); g.pileVP.wildchase = (g.pileVP.wildchase || 0) + 1; return; }
      if (yield* gain(g, pi, 'estate')) { vp(g, p, g.pileVP.wildchase || 0); g.pileVP.wildchase = 0; }
    },
  },
  {
    id: 'townblock', name: '町並み', cost: 0, debt: 8, main: '+2 アクション', desc: '手札を見せ、アクション 1 枚につき +1 カード',
    *play(g, p) { g.turn.actions += 2; drawCards(p, p.hand.filter((id) => is(id, 'action')).length); },
  },
  {
    id: 'overking', name: '覇王', types: ['action', 'command'], cost: 0, debt: 8, main: 'サプライの札として使う', desc: 'サプライの、コスト 5 以下の命令でないアクションを 1 つ選び、それとして使う（札はサプライに残る）',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, '使うアクション（コスト 5 以下）', 5, (x) => is(x, 'action') && !is(x, 'command'));
      if (!id) return;
      const real = g.stacks[id] ? g.stacks[id].at(-1) : id;
      log(g, `覇王が${nm(real)}として使われた。`);
      yield* resolve(g, real);
    },
  },
  {
    id: 'royalsmith', name: '御用鍛冶', cost: 0, debt: 8, main: '+5 カード', desc: '手札を見せ、銅をすべて捨てる',
    *play(g, p) {
      drawCards(p, 5);
      const idx = p.hand.map((id, i) => (id === 'copper' ? i : -1)).filter((i) => i >= 0);
      yield* discardCards(g, p, takeFromHand(p, idx));
    },
  },
];

// ---- イベント ----
const E = ['event'];
const events = [
  {
    id: 'e_promote', name: '出世', types: E, cost: 0, main: 'アクションを格上げ', desc: '手札のアクションを 1 枚廃棄してよい。そうしたらコスト 6 以下のアクションを獲得する',
    *buy(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄するアクション（しなくてもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      yield* trashCards(g, p, takeFromHand(p, [i]));
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 6 以下のアクションを獲得', 6, (id) => is(id, 'action')));
    },
  },
  { id: 'e_dig', name: '掘り下げ', types: E, cost: 2, main: '+1 購入\n銀を獲得', desc: '', *buy(g, p, pi) { g.turn.buys += 1; yield* gain(g, pi, 'silver'); } },
  {
    id: 'e_levy', name: '年貢', types: E, cost: 2, main: '山に借金', desc: 'サプライの山 1 つに借金トークンを 2 つ置く（買った人が受け取る）。はじめはすべての山に 1 つずつ置く',
    *buy(g, p, pi) {
      const piles = Object.keys(g.supply);
      const [i] = yield* askCards(g, pi, '借金を 2 つ置く山', piles, 1, 1);
      const id = piles[i ?? 0];
      g.pileDebt[id] = (g.pileDebt[id] || 0) + 2;
    },
  },
  {
    id: 'e_feast', name: '祝い膳', types: E, cost: 3, main: '銅 2 枚と\nコスト 5 以下', desc: '銅を 2 枚と、コスト 5 以下の勝利点でないカードを 1 枚獲得する',
    *buy(g, p, pi) { yield* gain(g, pi, 'copper'); yield* gain(g, pi, 'copper'); yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下（勝利点以外）を獲得', 5, (id) => !is(id, 'victory'))); },
  },
  { id: 'e_marriage', name: '祝言', types: E, cost: 4, debt: 3, main: '+1 勝利点トークン\n金を獲得', desc: '', *buy(g, p, pi) { vp(g, p, 1); yield* gain(g, pi, 'gold'); } },
  {
    id: 'e_rite', name: '祭祀', types: E, cost: 4, main: '災いと引き換えに点', desc: '災いを獲得する。獲得したら手札を 1 枚廃棄し、そのコスト 1 につき +1 勝利点トークン',
    *buy(g, p, pi) {
      if (!(yield* gain(g, pi, 'curse'))) return;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      vp(g, p, costOf(g, id));
    },
  },
  {
    id: 'e_scorch', name: '焦土', types: E, cost: 4, main: '+1 勝利点トークン', desc: 'サプライの勝利点カードを 1 枚廃棄する',
    *buy(g, p, pi) {
      vp(g, p, 1);
      const id = yield* askSupply(g, pi, 'サプライから廃棄する勝利点カード', 99, (x) => is(x, 'victory'));
      const c = id && takeFromSupply(g, id);
      if (c) yield* trashCards(g, p, [c]);
    },
  },
  { id: 'e_luck', name: '思わぬ幸運', types: E, cost: 5, main: '金 3 枚', desc: '山札と捨て札が空なら、金を 3 枚獲得する', *buy(g, p, pi) { if (!p.deck.length && !p.discard.length) for (let k = 0; k < 3; k++) yield* gain(g, pi, 'gold'); } },
  {
    id: 'e_warcry', name: '勝ちどき', types: E, cost: 0, debt: 5, main: '小屋を獲得', desc: '小屋を獲得する。獲得したら、この手番に獲得した札 1 枚につき +1 勝利点トークン',
    *buy(g, p, pi) { if (yield* gain(g, pi, 'estate')) vp(g, p, g.turn.gained.length); },
  },
  {
    id: 'e_subdue', name: '平定', types: E, cost: 6, main: '銀 2 枚', desc: '銀を 2 枚獲得する。この手番に獲得した銀 1 枚につき +1 勝利点トークン',
    *buy(g, p, pi) { yield* gain(g, pi, 'silver'); yield* gain(g, pi, 'silver'); vp(g, p, g.turn.gained.filter((id) => id === 'silver').length); },
  },
  {
    id: 'e_absorb', name: '取り込み', types: E, cost: 0, debt: 8, main: '捨て札を混ぜる\n荘園を獲得', desc: '捨て札のうち 5 枚までを残し、ほかを山札に混ぜる。荘園を獲得する',
    *buy(g, p, pi) {
      const keep = yield* askCards(g, pi, '捨て札に残す札（5 枚まで）', [...p.discard], 0, 5);
      const stay = p.discard.filter((_, i) => keep.includes(i));
      p.deck.push(...p.discard.filter((_, i) => !keep.includes(i)));
      p.discard = stay;
      shuffle(p.deck);
      yield* gain(g, pi, 'duchy');
    },
  },
  {
    id: 'e_alms2', name: '喜捨', types: E, cost: 0, debt: 8, main: '手番のあとに\nまとめて廃棄', desc: 'この手番のあと、山札と捨て札をすべて手札に入れ、好きな枚数廃棄し、残りを山札にして混ぜ、5 枚引く',
    *buy(g) { g.turn.donate = true; },
  },
  {
    id: 'e_unify', name: '天下統一', types: E, cost: 14, main: '領地 +9 点', desc: '領地を獲得する。獲得したら +9 勝利点トークン',
    *buy(g, p, pi) { if (yield* gain(g, pi, 'province')) vp(g, p, 9); },
  },
];

// ---- ランドマーク（買わない。ゲーム中ずっと効く） ----
const L = ['landmark'];
const countOf = (all, id) => all.filter((x) => x === id).length;
const landmarks = [
  { id: 'l_canal', name: '用水路', types: L, cost: 0, main: '財宝で貯め\n勝利点で受け取る', desc: '財宝を獲得したら、その山の勝利点トークンを 1 つここへ。勝利点カードを獲得したら、ここのトークンをすべて受け取る（はじめ銀と金の山に 8 つずつ）' },
  { id: 'l_ring', name: '土俵', types: L, cost: 0, main: 'アクションを捨てて\n2 点', desc: '購入フェイズの始めに、アクションを 1 枚捨ててよい。そうしたらここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_banditden', name: '賊の隠れ里', types: L, cost: 0, main: '銀・金 1 枚につき\n-2 点', desc: 'ゲームの終わりに、持っている銀と金 1 枚につき -2 点', score: (g, p, all) => -2 * (countOf(all, 'silver') + countOf(all, 'gold')) },
  { id: 'l_hall', name: '会所', types: L, cost: 0, main: '2 金残して買うと\n2 点', desc: 'カードを買って 2 金以上残っていたら、ここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_bathhouse', name: '湯屋', types: L, cost: 0, main: '何も獲得しない\n手番に 2 点', desc: '何も獲得せずに手番を終えたら、ここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_battleground', name: '古戦場', types: L, cost: 0, main: '勝利点を獲得して\n2 点', desc: '勝利点カードを獲得したら、ここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_arcade', name: '回廊', types: L, cost: 0, main: '場にある札を買って\n2 点', desc: 'アクションを買ったとき、同じ札が場にあれば、ここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_ruinedtemple', name: '荒れ寺', types: L, cost: 0, main: 'アクションで貯め\n災いで受け取る', desc: 'アクションを獲得したら、その山の勝利点トークンを 1 つここへ。災いを買ったら、ここのトークンをすべて受け取る（はじめアクションの山に 2 つずつ）' },
  { id: 'l_fountain', name: '泉水', types: L, cost: 0, main: '銅 10 枚で 15 点', desc: 'ゲームの終わりに、銅を 10 枚以上持っていれば 15 点', score: (g, p, all) => (countOf(all, 'copper') >= 10 ? 15 : 0) },
  {
    id: 'l_donjon', name: '天守', types: L, cost: 0, main: '財宝の最多で\n5 点ずつ', desc: 'ゲームの終わりに、財宝の名前ごとに、いちばん多く持っている人（同数も）は 5 点',
    score: (g, p, all) => {
      const names = [...new Set(all.filter((id) => is(id, 'treasure')))];
      return 5 * names.filter((id) => g.players.every((q) => countOf(allCards(q), id) <= countOf(all, id))).length;
    },
  },
  { id: 'l_maze', name: '迷路', types: L, cost: 0, main: '1 手番に 2 枚目を\n獲得して 2 点', desc: '自分の手番に 2 枚目のカードを獲得したら、ここから勝利点トークンを 2 つ受け取る' },
  { id: 'l_pass', name: '関所越え', types: L, cost: 0, main: '最初の領地で\n入札', desc: '誰かが最初に領地を獲得した手番のあと、全員が 1 回ずつ借金で入札する（40 まで）。いちばん高い人は +8 勝利点トークンと、その額の借金を受け取る' },
  { id: 'l_treasury', name: '宝物殿', types: L, cost: 0, main: '種類ごとに 2 点', desc: 'ゲームの終わりに、持っているちがう名前の札 1 種につき 2 点', score: (g, p, all) => 2 * new Set(all).size },
  { id: 'l_pillar', name: '石柱', types: L, cost: 0, main: '選ばれた山の札で\n2 点ずつ', desc: 'ゲームの終わりに、対局の始めに選ばれたアクションの山の札 1 枚につき 2 点', score: (g, p, all) => (g.pillar ? 2 * all.filter((id) => pileOf(id) === g.pillar).length : 0) },
  { id: 'l_fruitfield', name: '果物畑', types: L, cost: 0, main: 'アクション 3 枚で\n4 点', desc: 'ゲームの終わりに、3 枚以上持っているアクションの名前 1 種につき 4 点', score: (g, p, all) => 4 * [...new Set(all.filter((id) => is(id, 'action')))].filter((id) => countOf(all, id) >= 3).length },
  { id: 'l_palace', name: '御殿', types: L, cost: 0, main: '銅銀金のそろいで\n3 点', desc: 'ゲームの終わりに、銅・銀・金の組 1 つにつき 3 点', score: (g, p, all) => 3 * Math.min(countOf(all, 'copper'), countOf(all, 'silver'), countOf(all, 'gold')) },
  { id: 'l_mound', name: '塚', types: L, cost: 0, main: '廃棄するたび\n+1 点', desc: '札を廃棄するたびに +1 勝利点トークン' },
  { id: 'l_tower', name: '高楼', types: L, cost: 0, main: '空の山の札で\n1 点ずつ', desc: 'ゲームの終わりに、空になったサプライの山の、勝利点でない札 1 枚につき 1 点', score: (g, p, all) => all.filter((id) => !is(id, 'victory') && g.supply[pileOf(id)] === 0).length },
  {
    id: 'l_gate', name: '大門', types: L, cost: 0, main: '2 番目に多い\nアクションで 3 点', desc: 'ゲームの終わりに、2 番目に多く持っているアクションの枚数 1 枚につき 3 点',
    score: (g, p, all) => { const c = [...new Set(all.filter((id) => is(id, 'action')))].map((id) => countOf(all, id)).sort((a, b) => b - a); return 3 * (c[1] || 0); },
  },
  { id: 'l_wall', name: '城壁', types: L, cost: 0, main: '15 枚を超えた分\n-1 点', desc: 'ゲームの終わりに、15 枚を超えて持っている札 1 枚につき -1 点', score: (g, p, all) => -Math.max(0, all.length - 15) },
  { id: 'l_lair', name: '獣の巣', types: L, cost: 0, main: '1 枚だけの札で\n-3 点', desc: 'ゲームの終わりに、ちょうど 1 枚だけ持っている札 1 種につき -3 点', score: (g, p, all) => -3 * [...new Set(all)].filter((id) => countOf(all, id) === 1).length },
];

// ---- どのカードにも関わる決まり ----
HOOKS.setup.push((g) => {
  const n = g.players.length;
  for (const [pile, [top, bottom]] of Object.entries(SPLIT)) {
    if (!g.kingdom.includes(pile)) continue;
    g.stacks[pile] = [...Array(5).fill(bottom), ...Array(5).fill(top)];
    g.supply[pile] = 10;
  }
  if (g.kingdom.includes('castles')) {
    const two = ['c_humble', 'c_small', 'c_opulent', 'c_king'];
    const list = castles.flatMap((c) => (n > 2 && two.includes(c.id) ? [c.id, c.id] : [c.id]));
    g.stacks.castles = list.sort((a, b) => CARDS[b].cost - CARDS[a].cost); // 末尾（一番上）が安い
    g.supply.castles = list.length;
  }
  for (const id of g.landscapes) if (CARDS[id].types.includes('landmark') && ['l_ring', 'l_hall', 'l_bathhouse', 'l_battleground', 'l_arcade', 'l_maze'].includes(id)) g.landmarkVP[id] = 6 * n;
  if (lm(g, 'l_canal')) { g.pileVP.silver = 8; g.pileVP.gold = 8; g.landmarkVP.l_canal = 0; }
  if (lm(g, 'l_ruinedtemple')) {
    g.landmarkVP.l_ruinedtemple = 0;
    for (const id of Object.keys(g.supply)) if (is(id, 'action') && !is(id, 'gathering')) g.pileVP[id] = (g.pileVP[id] || 0) + 2;
  }
  if (lm(g, 'l_pillar')) { const acts = Object.keys(g.supply).filter((id) => is(id, 'action')); g.pillar = acts.length ? shuffle(acts)[0] : null; }
  if (lm(g, 'e_levy')) for (const id of Object.keys(g.supply)) g.pileDebt[id] = 1;
});
HOOKS.gain.push(function* (g, got) {
  const p = g.players[got.pi];
  const pile = pileOf(got.id);
  if (lm(g, 'l_canal')) {
    if (is(got.id, 'treasure') && g.pileVP[pile] > 0) { g.pileVP[pile] -= 1; g.landmarkVP.l_canal += 1; }
    if (is(got.id, 'victory')) takeLm(g, p, 'l_canal', g.landmarkVP.l_canal);
  }
  if (lm(g, 'l_ruinedtemple') && is(got.id, 'action') && g.pileVP[pile] > 0) { g.pileVP[pile] -= 1; g.landmarkVP.l_ruinedtemple += 1; }
  if (lm(g, 'l_battleground') && is(got.id, 'victory')) takeLm(g, p, 'l_battleground', 2);
  if (lm(g, 'l_maze') && got.pi === g.current && g.turn.gained.length === 2) takeLm(g, p, 'l_maze', 2);
  if (lm(g, 'l_pass') && got.id === 'province' && !g.passDone) { g.passDone = true; g.passPending = true; }
});
HOOKS.buy.push(function* (g, id, pi) {
  const p = g.players[pi];
  if (lm(g, 'l_hall') && g.turn.money >= 2) takeLm(g, p, 'l_hall', 2);
  if (lm(g, 'l_arcade') && is(id, 'action') && g.playArea.includes(id)) takeLm(g, p, 'l_arcade', 2);
  if (lm(g, 'l_ruinedtemple') && id === 'curse') takeLm(g, p, 'l_ruinedtemple', g.landmarkVP.l_ruinedtemple);
  // 縁起物: 次に買ったとき、同じコストのちがう札を獲得してよい
  while (g.turn.luckycharm > 0) {
    g.turn.luckycharm -= 1;
    const c = costOf(g, id);
    yield* gain(g, pi, yield* askSupply(g, pi, `縁起物: コスト ${c} のちがう札を獲得してよい`, c, (x) => x !== id && costOf(g, x) === c, true));
  }
});
HOOKS.trash.push(function* (g, p) { if (lm(g, 'l_mound')) vp(g, p, 1); });
HOOKS.buyPhase.push(function* (g) {
  if (!lm(g, 'l_ring') || !(g.landmarkVP.l_ring > 0)) return;
  const p = currentPlayer(g);
  const [i] = yield* askHand(g, g.current, '土俵: アクションを 1 枚捨てて 2 点にしてよい', 0, 1, (id) => is(id, 'action'));
  if (i == null) return;
  yield* discardCards(g, p, takeFromHand(p, [i]));
  takeLm(g, p, 'l_ring', 2);
});
HOOKS.endTurn.push(function* (g) {
  if (lm(g, 'l_bathhouse') && !g.turn.gained.length) takeLm(g, currentPlayer(g), 'l_bathhouse', 2);
});
HOOKS.afterCleanup.push(function* (g, p, pi) {
  // 喜捨: 山札と捨て札をすべて手札に入れ、好きなだけ廃棄し、残りを混ぜて 5 枚引く
  if (g.turn.donate) {
    g.turn.donate = false;
    p.hand.push(...p.deck.splice(0), ...p.discard.splice(0));
    yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '喜捨: 廃棄する札（好きな枚数）', 0, p.hand.length)));
    p.deck = shuffle(p.hand.splice(0));
    drawCards(p, 5);
  }
  // 関所越え: 最初の領地が獲得された手番のあと、左の人から順に 1 回ずつ入札
  if (g.passPending) {
    g.passPending = false;
    const n = g.players.length;
    let high = 0;
    let winner = null;
    for (let k = 1; k <= n; k++) {
      const bi = (pi + k) % n;
      const opts = [{ value: 0, label: 'パス' }];
      for (const v of [1, 2, 3, 5, 8, 10, 15, 20, 30, 40]) if (v > high) opts.push({ value: v, label: `借金 ${v}` });
      const bid = yield* askChoose(g, bi, `関所越えの入札（今の最高 ${high}）`, opts);
      if (bid > high) { high = bid; winner = bi; }
    }
    if (winner != null) {
      const w = g.players[winner];
      vp(g, w, 8);
      w.tokens.debt = (w.tokens.debt || 0) + high;
      log(g, `${w.name}が関所越えを借金 ${high} で落札した。`);
    }
  }
});

defineCards({ id: 'empires', name: '帝国' }, [...kingdom, ...splitCards, ...castles, ...events, ...landmarks], [
  { id: 'basicintro', name: 'はじめての帝国', cards: ['castles', 'chariot', 'p_catapult', 'townblock', 'p_encampment', 'mechanic', 'meetinghall', 'p_gladiator', 'royalsmith', 'wildchase'], landscapes: ['e_feast', 'l_canal'] },
  { id: 'advancedintro', name: '腕利きの帝国', cards: ['archivist', 'principal', 'luckycharm', 'scepter', 'gardener', 'hoplite', 'overking', 'p_patrician', 'oblation', 'villa'], landscapes: ['e_warcry', 'l_hall'] },
  { id: 'everythingneed', name: '欲しいもの全部', cards: ['p_settlers', 'temptress', 'vegmarket', 'shrine', 'townblock', 'chariot', 'oblation', 'wildchase', 'castles', 'gardener'], landscapes: ['e_promote', 'l_bathhouse'] },
]);
