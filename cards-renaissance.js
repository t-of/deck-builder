'use strict';
// 拡張「ルネサンス」のカード（王国 25 種）、アーティファクト 5 種、プロジェクト 19 種。名前は本家と別の言い回し。
// 村人: player.tokens.villagers（spendVillager で +1 アクション）。財源: tokens.coffers。
// プロジェクト: 買うと player.projects に入り、ずっと効く。アーティファクト: game.artifacts[id] = 持ち主。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, treasureEffect, later, returnCard, returnToPile, currentPlayer, receive,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const tok = (g, p, key, n, label) => { p.tokens[key] = (p.tokens[key] || 0) + n; log(g, `${p.name}が${label}を ${n} 得た（${p.tokens[key]}）。`); };
const villagers = (g, p, n) => tok(g, p, 'villagers', n, '村人');
const coffers = (g, p, n) => tok(g, p, 'coffers', n, '財源');
function takeArtifact(g, pi, id) {
  if (g.artifacts[id] === pi) return;
  g.artifacts[id] = pi;
  log(g, `${g.players[pi].name}が${nm(id)}を取った。`);
}
const has = (g, pi, id) => g.artifacts[id] === pi;
const owns = (p, id) => p.projects.includes(id);
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'gatekeeper', name: '関守', cost: 2, main: '+1 アクション', desc: '山札の上 2 枚（提灯があれば 3 枚）をめくり、1 枚を手札に、残りを捨てる。全部アクションなら提灯か法螺貝を取る',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const n = has(g, pi, 'a_lantern') ? 3 : 2;
      const shown = reveal(p, n);
      if (!shown.length) return;
      const [i] = yield* askCards(g, pi, '手札に入れる 1 枚', shown, 1, 1);
      p.hand.push(...shown.splice(i ?? 0, 1));
      yield* discardCards(g, p, shown, true);
      if (shown.length + 1 === n && [...shown, p.hand.at(-1)].every((id) => is(id, 'action'))) {
        const opts = ['a_lantern', 'a_horn'].filter((a) => !has(g, pi, a) && (a !== 'a_lantern' || n === 2));
        if (!opts.length) return;
        const [k] = yield* askCards(g, pi, '取るアーティファクト', opts, 1, 1);
        takeArtifact(g, pi, opts[k ?? 0]);
      }
    },
    *onCleanup(g, p, pi) {
      if (!has(g, pi, 'a_horn') || g.turn.hornUsed || !g.playArea.includes('gatekeeper')) return;
      if (!(yield* askYesNo(g, pi, '法螺貝: 関守を山札の上に戻しますか？', '戻す', 'しない', ['gatekeeper']))) return;
      g.turn.hornUsed = true;
      putOnDeck(p, g.playArea.splice(g.playArea.indexOf('gatekeeper'), 1)[0]);
    },
  },
  {
    id: 'koban', name: '小判', types: ['treasure'], cost: 2, autoPlay: true, main: '+1 財源\n+1 購入', desc: '獲得したとき、手札の銅を 1 枚廃棄してよい',
    *play(g, p) { coffers(g, p, 1); g.turn.buys += 1; },
    *onGain(g, got) {
      const p = g.players[got.pi];
      if (p.hand.includes('copper') && (yield* askYesNo(g, got.pi, '手札の銅を廃棄しますか？', '廃棄する', 'しない', ['copper']))) yield* trashCards(g, p, takeFromHand(p, [p.hand.indexOf('copper')]));
    },
  },
  {
    id: 'lackeys', name: '手下衆', cost: 2, main: '+2 カード', desc: '獲得したとき +2 村人',
    *play(g, p) { drawCards(p, 2); },
    *onGain(g, got) { villagers(g, g.players[got.pi], 2); },
  },
  // ---- コスト 3 ----
  {
    id: 'troupe', name: '旅一座', cost: 3, main: '+4 村人', desc: 'これを廃棄する',
    *play(g, p) { villagers(g, p, 4); yield* trashSelf(g, p, 'troupe'); },
  },
  {
    id: 'cargo', name: '荷船', types: ['action', 'duration'], cost: 3, main: '+2 金', desc: 'この手番に 1 度、獲得した札を脇に置いてよい。次の手番の始めにそれを手札に入れる',
    *play(g) { g.turn.money += 2; g.turn.cargo = (g.turn.cargo || 0) + 1; g.turn.cargoStay = (g.turn.cargoStay || 0); },
  },
  {
    id: 'trial2', name: '試し', cost: 3, main: '+2 カード\n+1 アクション', desc: 'これをサプライに戻す。獲得したとき、もう 1 枚獲得する（その 1 枚では増えない）',
    *play(g, p) { drawCards(p, 2); g.turn.actions += 1; returnToPile(g, 'trial2'); },
    *onGain(g, got) { if (g.turn.trialChain) return; g.turn.trialChain = true; yield* gain(g, got.pi, 'trial2'); g.turn.trialChain = false; },
  },
  {
    id: 'improve', name: '手入れ', cost: 3, main: '+2 金', desc: '片付けの始めに、場から捨てるアクションを 1 枚廃棄してよい。そうしたら、ちょうどコスト +1 の札を獲得する',
    *play(g) { g.turn.money += 2; },
    *onCleanup(g, p, pi) {
      const acts = g.playArea.filter((id) => is(id, 'action') && !g.turn.stay.includes(id));
      const [i] = yield* askCards(g, pi, '手入れ: 廃棄するアクション（なしでもよい）', acts, 0, 1);
      if (i == null) return;
      const id = acts[i];
      g.playArea.splice(g.playArea.indexOf(id), 1);
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id) + 1;
      yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c));
    },
  },
  // ---- コスト 4 ----
  {
    id: 'flagbearer', name: '旗持ち', cost: 4, main: '+2 金', desc: '獲得したとき・廃棄したとき、のぼり旗を取る',
    *play(g) { g.turn.money += 2; },
    *onGain(g, got) { takeArtifact(g, got.pi, 'a_flag'); },
    *onTrash(g, p, pi) { takeArtifact(g, pi, 'a_flag'); },
  },
  {
    id: 'lair2', name: '隠れ家', cost: 4, main: '+1 カード\n+2 アクション', desc: '手札を 1 枚廃棄する。それが勝利点カードなら災いを獲得する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 2;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (is(id, 'victory')) yield* gain(g, pi, 'curse');
    },
  },
  {
    id: 'inventor', name: '発明の人', cost: 4, main: 'コスト 4 以下を獲得', desc: 'そのあと、この手番のあいだ、カードのコストが 1 下がる',
    *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4)); g.turn.costDown += 1; },
  },
  {
    id: 'mountainvillage', name: '山里', cost: 4, main: '+2 アクション', desc: '捨て札を見て 1 枚を手札に入れる。捨て札がなければ +1 カード',
    *play(g, p, pi) {
      g.turn.actions += 2;
      if (!p.discard.length) { drawCards(p, 1); return; }
      const [i] = yield* askCards(g, pi, '手札に入れる 1 枚', [...p.discard], 1, 1);
      p.hand.push(p.discard.splice(i ?? 0, 1)[0]);
    },
  },
  {
    id: 'backer', name: '後ろ盾', types: ['action', 'reaction'], cost: 4, main: '+1 村人\n+2 金', desc: '効果で見せられたとき +1 財源（手札を見せる・山札をめくる など）',
    *play(g, p) { villagers(g, p, 1); g.turn.money += 2; },
  },
  {
    id: 'kannushi', name: '神主', cost: 4, main: '+2 金', desc: '手札を 1 枚廃棄する。この手番のあいだ、このあと札を廃棄するたびに +2 金',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)));
      g.turn.kannushi = (g.turn.kannushi || 0) + 1;
    },
  },
  {
    id: 'research', name: '調べもの', types: ['action', 'duration'], cost: 4, main: '+1 アクション', desc: '手札を 1 枚廃棄し、そのコスト 1 につき山札の上から 1 枚を脇に置く。次の手番の始めに、それを手札に入れる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const aside = reveal(p, costOf(g, id));
      if (!aside.length) return;
      (p.mats.research = p.mats.research || []).push(...aside);
      later(g, 'research', function* () { for (const c of aside) { const k = p.mats.research.indexOf(c); if (k >= 0) p.hand.push(...p.mats.research.splice(k, 1)); } });
    },
  },
  {
    id: 'draper', name: '呉服屋', cost: 4, main: '+2 カード\n+1 購入', desc: '獲得したとき・廃棄したとき、+1 財源 +1 村人',
    *play(g, p) { drawCards(p, 2); g.turn.buys += 1; },
    *onGain(g, got) { const p = g.players[got.pi]; coffers(g, p, 1); villagers(g, p, 1); },
    *onTrash(g, p) { coffers(g, p, 1); villagers(g, p, 1); },
  },
  // ---- コスト 5 ----
  {
    id: 'yamauba', name: '山姥', types: ['action', 'attack'], cost: 5, main: '+3 カード', desc: '他の人は災いを獲得する。そのあと、手札の災いを 1 枚廃棄してよい',
    *play(g, p) {
      drawCards(p, 3);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        yield* gain(g, ti, 'curse');
        if (t.hand.includes('curse') && (yield* askYesNo(g, ti, '手札の災いを 1 枚廃棄しますか？', '廃棄する', 'しない', ['curse']))) yield* trashCards(g, t, takeFromHand(t, [t.hand.indexOf('curse')]));
      });
    },
  },
  {
    id: 'recruiter', name: '口入れ屋', cost: 5, main: '+2 カード', desc: '手札を 1 枚廃棄し、そのコスト 1 につき +1 村人',
    *play(g, p, pi) {
      drawCards(p, 2);
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      villagers(g, p, costOf(g, id));
    },
  },
  {
    id: 'baton', name: '采配', types: ['treasure', 'command'], cost: 5, main: '+2 金 か\nアクションをもう一度', desc: '+2 金か、この手番に使って場に残っているアクションを 1 枚もう一度使うかを選ぶ',
    *play(g, p, pi) {
      const acts = [...new Set(g.playArea.filter((id) => is(id, 'action')))];
      const v = !acts.length ? 'coin' : yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'coin', label: '+2 金' }, { value: 'again', label: 'アクションをもう一度使う' }]);
      if (v === 'coin') { g.turn.money += 2; return; }
      const [i] = yield* askCards(g, pi, 'もう一度使うアクション', acts, 1, 1);
      log(g, `${nm(acts[i ?? 0])}をもう一度使う。`);
      yield* resolve(g, acts[i ?? 0]);
    },
  },
  {
    id: 'student', name: '書生', cost: 5, main: '手札を捨てて\n+7 カード', desc: '',
    *play(g, p) { yield* discardCards(g, p, p.hand.splice(0), true); drawCards(p, 7); },
  },
  {
    id: 'carver', name: '彫り師', cost: 5, main: '手札に獲得', desc: 'コスト 4 以下を手札に獲得する。それが財宝なら +1 村人',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下を手札に獲得', 4);
      if ((yield* gain(g, pi, id, 'hand')) && is(id, 'treasure')) villagers(g, p, 1);
    },
  },
  {
    id: 'clairvoyant', name: '千里眼', cost: 5, main: '+1 カード\n+1 アクション', desc: '山札の上 3 枚をめくり、コスト 2〜4 を手札に、残りを好きな順に戻す',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const shown = reveal(p, 3);
      const take = shown.filter((id) => costOf(g, id) >= 2 && costOf(g, id) <= 4);
      p.hand.push(...take);
      yield* putBackInOrder(g, pi, shown.filter((id) => !take.includes(id)));
    },
  },
  {
    id: 'spices', name: '香辛の品', types: ['treasure'], cost: 5, value: 2, autoPlay: true, main: '+2 金　+1 購入', desc: '獲得したとき +2 財源',
    *play(g) { g.turn.buys += 1; },
    *onGain(g, got) { coffers(g, g.players[got.pi], 2); },
  },
  {
    id: 'swordsman', name: '剣豪', cost: 5, main: '+3 カード', desc: '捨て札があれば +1 財源。そのあと財源が 4 以上なら千両箱を取る',
    *play(g, p, pi) {
      drawCards(p, 3);
      if (!p.discard.length) return;
      coffers(g, p, 1);
      if (p.tokens.coffers >= 4) takeArtifact(g, pi, 'a_chest');
    },
  },
  {
    id: 'treasurer', name: '勘定方', cost: 5, main: '+3 金', desc: '手札の財宝を 1 枚廃棄する / 廃棄置き場の財宝を 1 枚手札に獲得する / 合鍵を取る から 1 つ',
    *play(g, p, pi) {
      g.turn.money += 3;
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 't', label: '手札の財宝を廃棄' }, { value: 'g', label: '廃棄置き場の財宝を手札へ' }, { value: 'k', label: '合鍵を取る' }]);
      if (v === 't') yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する財宝', 1, 1, (id) => is(id, 'treasure'))));
      else if (v === 'k') takeArtifact(g, pi, 'a_key');
      else {
        const opts = [...new Set(g.trash.filter((id) => is(id, 'treasure')))];
        if (!opts.length) return;
        const [i] = yield* askCards(g, pi, '獲得する財宝', opts, 1, 1);
        const id = opts[i ?? 0];
        g.trash.splice(g.trash.lastIndexOf(id), 1);
        yield* receive(g, pi, id, 'hand');
      }
    },
  },
  {
    id: 'badguy', name: '悪玉', types: ['action', 'attack'], cost: 5, main: '+2 財源', desc: '手札が 5 枚以上の他の人は、コスト 2 以上の札を 1 枚捨てる（なければ手札を見せる）',
    *play(g, p) {
      coffers(g, p, 2);
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 5) return;
        const [i] = yield* askHand(g, ti, '捨てるコスト 2 以上の札', 1, 1, (id) => costOf(g, id) >= 2);
        if (i != null) yield* discardCards(g, t, takeFromHand(t, [i]));
      });
    },
  },
];

// ---- アーティファクト ----
const A = ['artifact'];
const artifacts = [
  { id: 'a_flag', name: 'のぼり旗', types: A, cost: 0, notSupply: true, main: '手札を引くとき\n+1 枚', desc: '片付けで手札を引くとき、1 枚多く引く' },
  { id: 'a_horn', name: '法螺貝', types: A, cost: 0, notSupply: true, main: '関守を山札に', desc: '1 手番に 1 度、場から関守を捨てるとき、山札の上に置いてよい' },
  { id: 'a_key', name: '合鍵', types: A, cost: 0, notSupply: true, main: '手番の始めに\n+1 金', desc: '' },
  { id: 'a_lantern', name: '提灯', types: A, cost: 0, notSupply: true, main: '関守が 3 枚見る', desc: '自分の関守は 3 枚めくり、2 枚捨てる（全部アクションなら法螺貝を取る）' },
  { id: 'a_chest', name: '千両箱', types: A, cost: 0, notSupply: true, main: '購入フェイズに\n金を獲得', desc: '購入フェイズの始めに金を獲得する' },
];

// ---- プロジェクト（買うと自分の印を置き、ずっと効く） ----
const P = ['project'];
const project = (id, name, cost, main, desc) => ({
  id, name, types: P, cost, main, desc,
  canBuy: (g) => !currentPlayer(g).projects.includes(id),
  *buy(g, p) { p.projects.push(id); },
});
const projects = [
  project('j_cathedral', '大伽藍', 3, '手番の始めに\n1 枚廃棄', '手番の始めに、手札を 1 枚廃棄する'),
  project('j_citygate', '町門', 3, '手番の始めに\n1 引いて 1 戻す', '手番の始めに +1 カードし、手札を 1 枚山札の上に置く'),
  project('j_pageant', '山車', 3, '1 金で 1 財源', '購入フェイズの終わりに、1 金払って +1 財源にしてよい'),
  project('j_sewers', '下水', 3, '廃棄したら\nもう 1 枚', '（この効果以外で）札を廃棄したとき、手札をもう 1 枚廃棄してよい'),
  project('j_starchart', '星の地図', 3, '混ぜたら 1 枚上に', '山札を混ぜたとき、1 枚を一番上に置く（いちばん高い札を自動で上にする）'),
  project('j_exploration', '見聞', 4, '買わなければ\n財源と村人', '購入フェイズの終わりに、何も買っていなければ +1 財源 +1 村人'),
  project('j_marketday', '市日', 4, '手番の始めに\n+1 購入', ''),
  project('j_silos', '穀物倉', 4, '銅を捨てて引く', '手番の始めに、好きな枚数の銅を捨て、同じ枚数引く'),
  project('j_plot', '陰の企て', 4, '印を貯めて\nまとめて引く', '手番の始めに、ここに印を 1 つ置くか、自分の印をすべて取って 1 つにつき +1 カード'),
  project('j_academy', '学問所', 5, 'アクションを\n獲得して +1 村人', ''),
  project('j_fleet', '船団', 5, '終わりに\n追加の手番', 'ゲームが終わるとき、これを持つ人は 1 回ずつ追加の手番をする'),
  project('j_guildhall', '組合の館', 5, '財宝を獲得して\n+1 財源', ''),
  project('j_piazza', '芝居小屋', 5, '手番の始めに\n山札の上を使う', '手番の始めに山札の一番上をめくり、アクションなら使う'),
  project('j_roads', '街道網', 5, '他の人が勝利点を\n獲得して +1 カード', ''),
  project('j_barracks', '兵営', 6, '手番の始めに\n+1 アクション', ''),
  project('j_croprotation', '畑まわし', 6, '勝利点を捨てて\n+2 カード', '手番の始めに、勝利点カードを 1 枚捨てて +2 カードにしてよい'),
  project('j_innovation', '新機軸', 6, '最初に獲得した\nアクションを使う', '各手番で最初に獲得したアクションを、脇に置いて使ってよい'),
  project('j_canal', '掘割', 7, '自分の手番は\nコスト -1', ''),
  project('j_citadel', '山城', 8, '最初のアクションを\n2 回', '各手番で手札から最初に使ったアクションを、もう一度使う'),
];

// ---- 決まり ----
HOOKS.turnStart.push(function* (g, p, pi) {
  if (has(g, pi, 'a_key')) g.turn.money += 1;
  if (owns(p, 'j_barracks')) g.turn.actions += 1;
  if (owns(p, 'j_marketday')) g.turn.buys += 1;
  if (owns(p, 'j_citygate')) {
    drawCards(p, 1);
    const [i] = yield* askHand(g, pi, '町門: 山札の上に置く 1 枚', 1, 1);
    if (i != null) putOnDeck(p, takeFromHand(p, [i])[0]);
  }
  if (owns(p, 'j_cathedral')) yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '大伽藍: 廃棄する 1 枚', 1, 1)));
  if (owns(p, 'j_croprotation') && p.hand.some((id) => is(id, 'victory'))) {
    const [i] = yield* askHand(g, pi, '畑まわし: 勝利点を捨てて +2 カード（しなくてもよい）', 0, 1, (id) => is(id, 'victory'));
    if (i != null) { yield* discardCards(g, p, takeFromHand(p, [i])); drawCards(p, 2); }
  }
  if (owns(p, 'j_silos') && p.hand.includes('copper')) {
    const idx = yield* askHand(g, pi, '穀物倉: 捨てる銅（好きな枚数）', 0, 99, (id) => id === 'copper');
    yield* discardCards(g, p, takeFromHand(p, idx));
    drawCards(p, idx.length);
  }
  if (owns(p, 'j_plot')) {
    const mine = p.tokens.plot || 0;
    if (mine && (yield* askYesNo(g, pi, `陰の企て: 印 ${mine} つを取って ${mine} 枚引きますか？`, '引く', '印を足す'))) { p.tokens.plot = 0; drawCards(p, mine); } else p.tokens.plot = mine + 1;
  }
  if (owns(p, 'j_piazza')) {
    const [id] = reveal(p, 1);
    if (id != null) {
      if (is(id, 'action')) { g.playArea.push(id); log(g, `芝居小屋で${nm(id)}を使う。`); yield* resolve(g, id); } else putOnDeck(p, id);
    }
  }
});
HOOKS.buyPhase.push(function* (g) { if (has(g, g.current, 'a_chest')) yield* gain(g, g.current, 'gold'); });
HOOKS.endTurn.push(function* (g) {
  const p = currentPlayer(g);
  if (owns(p, 'j_exploration') && !g.turn.bought.length) { coffers(g, p, 1); villagers(g, p, 1); }
  if (owns(p, 'j_pageant') && g.turn.money >= 1 && (yield* askYesNo(g, g.current, '山車: 1 金払って +1 財源にしますか？', 'する', 'しない'))) { g.turn.money -= 1; coffers(g, p, 1); }
  if (has(g, g.current, 'a_flag')) g.turn.extraDraw = (g.turn.extraDraw || 0) + 1;
  if (g.turn.cargo && p.mats.cargo && p.mats.cargo.length) g.turn.stay.push(...Array(Math.min(g.turn.cargoUsed || 0, g.turn.cargo)).fill('cargo'));
});
HOOKS.gain.push(function* (g, got) {
  const p = g.players[got.pi];
  const mine = got.pi === g.current;
  if (owns(p, 'j_academy') && is(got.id, 'action')) villagers(g, p, 1);
  if (owns(p, 'j_guildhall') && is(got.id, 'treasure')) coffers(g, p, 1);
  if (is(got.id, 'victory')) for (const [i, q] of g.players.entries()) if (i !== got.pi && owns(q, 'j_roads')) drawCards(q, 1);
  // 荷船: この手番に 1 度（荷船 1 枚につき）、獲得した札を脇に置き、次の手番に手札へ
  if (mine && g.turn.cargo > (g.turn.cargoUsed || 0) && got.to !== 'gone' && got.to !== 'trash'
    && (yield* askYesNo(g, got.pi, `獲得した${nm(got.id)}を荷船に載せて、次の手番に手札へ入れますか？`, '載せる', 'しない', [got.id]))) {
    if (yield* relocate(g, got, 'gone')) {
      g.turn.cargoUsed = (g.turn.cargoUsed || 0) + 1;
      const id = got.id;
      (p.mats.cargo = p.mats.cargo || []).push(id);
      p.nextTurn.push(function* () { const k = p.mats.cargo.indexOf(id); if (k >= 0) p.hand.push(...p.mats.cargo.splice(k, 1)); });
    }
  }
  // 新機軸: 各手番で最初に獲得したアクションを使ってよい
  if (mine && owns(p, 'j_innovation') && is(got.id, 'action') && !g.turn.innovated && got.to !== 'gone') {
    g.turn.innovated = true;
    if ((yield* askYesNo(g, got.pi, `新機軸: 獲得した${nm(got.id)}を使いますか？`, '使う', 'しない', [got.id])) && (yield* relocate(g, got, 'gone'))) {
      g.playArea.push(got.id);
      log(g, `${p.name}が${nm(got.id)}を使用。`);
      yield* resolve(g, got.id);
    }
  }
});
HOOKS.trash.push(function* (g, p, pi) {
  if (pi === g.current && g.turn.kannushi) g.turn.money += 2 * g.turn.kannushi;
  if (owns(p, 'j_sewers') && !g.turn.sewering && p.hand.length) {
    const [i] = yield* askHand(g, pi, '下水: 手札をもう 1 枚廃棄してよい', 0, 1);
    if (i == null) return;
    g.turn.sewering = true;
    yield* trashCards(g, p, takeFromHand(p, [i]));
    g.turn.sewering = false;
  }
});
HOOKS.cost.push((g) => (g.players && g.players[g.current] && owns(g.players[g.current], 'j_canal') ? 1 : 0));

defineCards({ id: 'renaissance', name: 'ルネサンス' }, [...kingdom, ...artifacts, ...projects], [
  { id: 'expertise', name: '腕のみせどころ', cards: ['yamauba', 'recruiter', 'baton', 'student', 'carver', 'clairvoyant', 'spices', 'swordsman', 'treasurer', 'koban'], landscapes: ['j_fleet', 'j_silos'] },
  { id: 'renaissancebasic', name: 'はじめてのルネサンス', cards: ['gatekeeper', 'lackeys', 'troupe', 'cargo', 'trial2', 'improve', 'flagbearer', 'mountainvillage', 'backer', 'draper'], landscapes: ['j_cathedral', 'j_barracks'] },
  { id: 'underdogs', name: 'あきらめない', cards: ['lair2', 'inventor', 'kannushi', 'research', 'badguy', 'koban', 'improve', 'swordsman', 'mountainvillage', 'recruiter'], landscapes: ['j_sewers', 'j_canal'] },
]);
