'use strict';
// 拡張「同盟」のカード（単独の王国 23 種、4 種が順に重なった山 6 つ）と同盟 23 種。名前は本家と別の言い回し。
// 好意: player.tokens.favors。連携（liaison）の札で増え、同盟の効果に使う。同盟は対局に 1 つ。
// 4 種の山は game.stacks。「循環」は一番上の札と同じ名前をすべて山の下へ（rotatePile）。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  putBackInOrder, relocate, treasureEffect, later, returnCard, currentPlayer, receive, shuffle, emptyPiles,
  rotatePile, pileOf, allCards, landscapePool, supplyOptions,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const LI = ['action', 'liaison'];
const favor = (g, p, n) => { p.tokens.favors = (p.tokens.favors || 0) + n; log(g, `${p.name}が好意を ${n} 得た（${p.tokens.favors}）。`); };
const ally = (g, id) => g.landscapes.includes(id);
function* spend(g, pi, n, purpose) {
  const p = g.players[pi];
  if ((p.tokens.favors || 0) < n) return false;
  if (!(yield* askYesNo(g, pi, `${purpose}（好意 ${n} を使う・残り ${p.tokens.favors}）`, '使う', '使わない'))) return false;
  p.tokens.favors -= n;
  return true;
}
function* trashSelf(g, p, id) {
  const at = g.playArea.lastIndexOf(id);
  if (at < 0) return false;
  yield* trashCards(g, p, g.playArea.splice(at, 1));
  return true;
}
function* discardDownTo(g, ti, n) {
  const t = g.players[ti];
  const need = t.hand.length - n;
  if (need > 0) yield* discardCards(g, t, takeFromHand(t, yield* askHand(g, ti, `手札が ${n} 枚になるまで捨てる（${need} 枚選ぶ）`, need, need)));
}
function* playNow(g, pi, id) {
  g.playArea.push(id);
  log(g, `${g.players[pi].name}が${nm(id)}を使用。`);
  if (is(id, 'action')) yield* resolve(g, id); else yield* treasureEffect(g, id);
}
function* mayRotate(g, pi, pile) {
  if (g.stacks[pile] && (yield* askYesNo(g, pi, `${nm(pile)}を循環させますか？（一番上の札を山の下へ）`, '循環させる', 'しない'))) rotatePile(g, pile);
}
function* nameAndReveal(g, pi, purpose) {
  const p = g.players[pi];
  const names = [...new Set(allCards(p))];
  const [k] = yield* askCards(g, pi, purpose, names, 1, 1);
  const [top] = reveal(p, 1);
  return { named: names[k ?? 0], top };
}

const kingdom = [
  // ---- コスト 2 ----
  {
    id: 'trinket', name: '道化棒', types: ['treasure', 'liaison'], cost: 2, main: '2 つ選ぶ', desc: '+1 購入 / +1 金 / +1 好意 / この手番、獲得した札を山札の上に置いてよい から、ちがうものを 2 つ',
    *play(g, p, pi) {
      const all = [{ value: 'b', label: '+1 購入' }, { value: 'm', label: '+1 金' }, { value: 'f', label: '+1 好意' }, { value: 't', label: '獲得を山札の上に' }];
      const a = yield* askChoose(g, pi, '1 つめ', all);
      const b = yield* askChoose(g, pi, '2 つめ', all.filter((c) => c.value !== a));
      for (const v of [a, b]) { if (v === 'b') g.turn.buys += 1; else if (v === 'm') g.turn.money += 1; else if (v === 'f') favor(g, p, 1); else g.turn.topdeckGains = true; }
    },
  },
  {
    id: 'flatterer', name: 'ごますり', types: LI, cost: 2, main: '+1 アクション', desc: '手札を 3 枚捨てる。1 枚以上捨てたら +3 金。獲得したとき・廃棄したとき +2 好意',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const ids = takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚', 3, 3));
      yield* discardCards(g, p, ids);
      if (ids.length) g.turn.money += 3;
    },
    *onGain(g, got) { favor(g, g.players[got.pi], 2); },
    *onTrash(g, p) { favor(g, p, 2); },
  },
  // ---- コスト 3 ----
  { id: 'importer', name: '輸入者', types: ['action', 'duration', 'liaison'], cost: 3, main: '次の手番に\nコスト 5 以下', desc: '次の手番の始めに、コスト 5 以下を獲得する。この札を使う対局では、はじめに全員が好意を 4 持つ',
    *play(g, p, pi) { later(g, 'importer', function* () { yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を獲得', 5)); }); } },
  { id: 'tradecamp', name: '商人の野営地', cost: 3, main: '+2 アクション\n+1 金', desc: '場から捨てるとき、山札の上に置いてよい',
    *play(g) { g.turn.actions += 2; g.turn.money += 1; },
    *onCleanup(g, p, pi) {
      while (g.playArea.includes('tradecamp') && !(g.turn.campDone || 0 >= g.playArea.filter((x) => x === 'tradecamp').length)) {
        if (!(yield* askYesNo(g, pi, '「商人の野営地」を山札の上に置きますか？', '置く', 'しない', ['tradecamp']))) break;
        putOnDeck(p, g.playArea.splice(g.playArea.indexOf('tradecamp'), 1)[0]);
      }
    } },
  {
    id: 'picket', name: '歩哨', cost: 3, main: '上 5 枚を見る', desc: '山札の上 5 枚を見て、2 枚まで廃棄し、残りを好きな順に戻す',
    *play(g, p, pi) {
      const seen = reveal(p, 5);
      const idx = yield* askCards(g, pi, '廃棄する札（2 枚まで）', seen, 0, 2);
      yield* trashCards(g, p, seen.filter((_, i) => idx.includes(i)));
      yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
    },
  },
  { id: 'underling', name: '下役', types: LI, cost: 3, main: '+1 カード　+1 アクション\n+1 好意', desc: '', *play(g, p) { drawCards(p, 1); g.turn.actions += 1; favor(g, p, 1); } },
  // ---- コスト 4 ----
  {
    id: 'middleman', name: '仲買人', types: LI, cost: 4, main: '廃棄して\nコストの数だけ', desc: '手札を 1 枚廃棄し、そのコスト 1 につき +1 カード / +1 アクション / +1 金 / +1 好意 のどれか 1 つ',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const n = costOf(g, id);
      const v = yield* askChoose(g, pi, `${n} ずつ得るものを選ぶ`, [{ value: 'c', label: `+${n} カード` }, { value: 'a', label: `+${n} アクション` }, { value: 'm', label: `+${n} 金` }, { value: 'f', label: `+${n} 好意` }]);
      if (v === 'c') drawCards(p, n); else if (v === 'a') g.turn.actions += n; else if (v === 'm') g.turn.money += n; else favor(g, p, n);
    },
  },
  {
    id: 'masterbuilder', name: '大工', cost: 4, main: '獲得か格上げ', desc: '空のサプライの山がなければ +1 アクションしてコスト 4 以下を獲得。あれば手札を 1 枚廃棄し、コスト +2 以下を獲得',
    *play(g, p, pi) {
      if (!emptyPiles(g)) { g.turn.actions += 1; yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4)); return; }
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 2;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得`, max));
    },
  },
  {
    id: 'dispatch', name: '急使', cost: 4, main: '+1 金', desc: '山札の一番上を捨てる。捨て札を見て、アクションか財宝を 1 枚使ってよい',
    *play(g, p, pi) {
      g.turn.money += 1;
      const [top] = reveal(p, 1);
      if (top != null) yield* discardCards(g, p, [top], true);
      const opts = p.discard.filter((id) => is(id, 'action') || is(id, 'treasure'));
      const [i] = yield* askCards(g, pi, '使う札（なしでもよい）', opts, 0, 1);
      if (i == null) return;
      p.discard.splice(p.discard.lastIndexOf(opts[i]), 1);
      yield* playNow(g, pi, opts[i]);
    },
  },
  {
    id: 'galley', name: '王家のガレー船', types: ['action', 'duration'], cost: 4, main: '+1 カード', desc: '手札の持続でないアクションを 1 枚使ってよい。それを脇に置き、次の手番の始めにもう一度使う',
    *play(g, p, pi) {
      drawCards(p, 1);
      const [i] = yield* askHand(g, pi, '使うアクション（持続以外・なしでもよい）', 0, 1, (id) => is(id, 'action') && !is(id, 'duration'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* playNow(g, pi, id);
      const at = g.playArea.lastIndexOf(id);
      if (at < 0) return;
      (p.mats.galley = p.mats.galley || []).push(...g.playArea.splice(at, 1));
      later(g, 'galley', function* () { const k = p.mats.galley.indexOf(id); if (k >= 0) { p.mats.galley.splice(k, 1); yield* playNow(g, pi, id); } });
    },
  },
  { id: 'innkeeper', name: '宿屋の主人', cost: 4, main: '+1 アクション', desc: '+1 カード / +3 カードして 3 枚捨てる / +5 カードして 6 枚捨てる から 1 つ',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 1, label: '+1 カード' }, { value: 3, label: '+3 カード・3 枚捨てる' }, { value: 5, label: '+5 カード・6 枚捨てる' }]);
      drawCards(p, v);
      const d = v === 3 ? 3 : v === 5 ? 6 : 0;
      if (d) yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, `捨てる ${d} 枚`, d, d)));
    } },
  { id: 'posttown', name: '町', cost: 4, main: '2 つから選ぶ', desc: '「+1 カード +2 アクション」か「+1 購入 +2 金」',
    *play(g, p, pi) { if (yield* askYesNo(g, pi, 'どちらにしますか？', '+1 カード +2 アクション', '+1 購入 +2 金')) { drawCards(p, 1); g.turn.actions += 2; } else { g.turn.buys += 1; g.turn.money += 2; } } },
  // ---- コスト 5 ----
  {
    id: 'savage', name: '蛮族', types: ['action', 'attack'], cost: 5, main: '+2 金', desc: '他の人は山札の一番上を廃棄する。コスト 3 以上なら同じ種類で安い札を獲得。そうでなければ呪いを獲得',
    *play(g) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        const [id] = reveal(t, 1);
        if (id == null) return;
        yield* trashCards(g, t, [id]);
        const c = costOf(g, id);
        if (c >= 3) yield* gain(g, ti, yield* askSupply(g, ti, `コスト ${c - 1} 以下で同じ種類の札を獲得`, c - 1, (x) => CARDS[x].types.some((ty) => CARDS[id].types.includes(ty))));
        else yield* gain(g, ti, 'curse');
      });
    },
  },
  {
    id: 'metropolis', name: '首都', cost: 5, main: '+1 カード\n+2 アクション', desc: '2 枚捨てて +2 金にしてよい。2 金払って +2 カードにしてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 2;
      if (p.hand.length >= 2 && (yield* askYesNo(g, pi, '2 枚捨てて +2 金にしますか？', 'する', 'しない'))) { yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚', 2, 2))); g.turn.money += 2; }
      if (g.turn.money >= 2 && (yield* askYesNo(g, pi, '2 金払って +2 カードにしますか？', 'する', 'しない'))) { g.turn.money -= 2; drawCards(p, 2); }
    },
  },
  { id: 'deed', name: '契約書', types: ['treasure', 'duration', 'liaison'], cost: 5, value: 2, main: '+2 金\n+1 好意', desc: '手札のアクションを 1 枚脇に置いてよい。次の手番の始めにそれを使う',
    *play(g, p, pi) {
      favor(g, p, 1);
      const [i] = yield* askHand(g, pi, '次の手番に使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      (p.mats.deed = p.mats.deed || []).push(id);
      later(g, 'deed', function* () { const k = p.mats.deed.indexOf(id); if (k >= 0) { p.mats.deed.splice(k, 1); yield* playNow(g, pi, id); } });
    } },
  {
    id: 'go_between', name: '密使', types: LI, cost: 5, main: '+3 カード', desc: 'これで山札を混ぜたら、+1 アクション +2 好意',
    *play(g, p) {
      const shuffled = p.deck.length < 3 && p.discard.length > 0;
      drawCards(p, 3);
      if (shuffled) { g.turn.actions += 1; favor(g, p, 2); }
    },
  },
  { id: 'arcade2', name: 'ガレリア', cost: 5, main: '+3 金', desc: 'この手番、コスト 3 か 4 の札を獲得するたびに +1 購入', *play(g) { g.turn.money += 3; g.turn.galleria = (g.turn.galleria || 0) + 1; } },
  { id: 'guildhead', name: 'ギルドマスター', types: LI, cost: 5, main: '+3 金', desc: 'この手番、札を獲得するたびに +1 好意', *play(g) { g.turn.money += 3; g.turn.guildhead = (g.turn.guildhead || 0) + 1; } },
  {
    id: 'waylayer', name: '辻斬り', types: ['action', 'duration', 'attack'], cost: 5, main: '次の手番に\n+3 カード', desc: '次の手番の始めに、これを捨てて +3 カード。それまで、他の人が各手番で最初に出す財宝は何もしない',
    *play(g, p) {
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.waylaid = (g.players[ti].tokens.waylaid || 0) + 1; });
      later(g, 'waylayer', function* () {
        for (const ti of hit) g.players[ti].tokens.waylaid -= 1;
        const at = g.playArea.indexOf('waylayer');
        if (at >= 0) yield* discardCards(g, p, g.playArea.splice(at, 1), true);
        drawCards(p, 3);
      });
    },
  },
  {
    id: 'tracker2', name: '狩人', cost: 5, main: '+1 アクション', desc: '山札の上 3 枚をめくり、アクション・財宝・勝利点を 1 枚ずつ手札に入れ、残りを捨てる',
    *play(g, p) {
      g.turn.actions += 1;
      const shown = reveal(p, 3);
      for (const t of ['action', 'treasure', 'victory']) { const i = shown.findIndex((id) => is(id, t)); if (i >= 0) p.hand.push(...shown.splice(i, 1)); }
      yield* discardCards(g, p, shown, true);
    },
  },
  {
    id: 'modify', name: '作り変え', cost: 5, main: '廃棄して選ぶ', desc: '手札を 1 枚廃棄し、「+1 カード +1 アクション」か「そのコスト +2 以下を獲得」を選ぶ',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (yield* askYesNo(g, pi, 'どちらにしますか？', '+1 カード +1 アクション', `コスト ${costOf(g, id) + 2} 以下を獲得`)) { drawCards(p, 1); g.turn.actions += 1; }
      else yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${costOf(g, id) + 2} 以下を獲得`, costOf(g, id) + 2));
    },
  },
  { id: 'skirmisher', name: '斥候兵', types: ['action', 'attack'], cost: 5, main: '+1 カード　+1 アクション\n+1 金', desc: 'この手番、アタックを獲得するたびに、他の人は手札が 3 枚になるまで捨てる',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.money += 1; g.turn.skirmish = (g.turn.skirmish || 0) + 1; yield* attackOthers(g, function* () {}); } },
  {
    id: 'specialist', name: '職人肌', cost: 5, main: '使って\nもう一度か複製', desc: '手札のアクションか財宝を 1 枚使ってよい。そのあと、もう一度使うか、同じ札を獲得するかを選ぶ',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '使う札（なしでもよい）', 0, 1, (id) => is(id, 'action') || is(id, 'treasure'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      yield* playNow(g, pi, id);
      if (yield* askYesNo(g, pi, 'どちらにしますか？', 'もう一度使う', '同じ札を獲得')) { if (is(id, 'action')) yield* resolve(g, id); else yield* treasureEffect(g, id); }
      else yield* gain(g, pi, id in g.supply ? id : pileOf(id));
    },
  },
  {
    id: 'exchange', name: '差し替え', cost: 5, main: '+1 カード\n+1 アクション', desc: '手札のアクションを 1 枚、その山に戻してよい。そうしたら、ちがうコスト 5 以下のアクションを手札に獲得する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const [i] = yield* askHand(g, pi, '山に戻すアクション（しなくてもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      if (!returnCard(g, id)) { p.hand.push(id); return; }
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下のちがうアクションを手札に獲得', 5, (x) => is(x, 'action') && x !== id && x !== pileOf(id)), 'hand');
    },
  },
  // ---- コスト 6 ----
  { id: 'marquess', name: '侯爵', cost: 6, main: '+1 購入\n手札の数だけ引く', desc: '手札 1 枚につき +1 カード。そのあと手札が 10 枚になるまで捨てる',
    *play(g, p, pi) { g.turn.buys += 1; drawCards(p, p.hand.length); yield* discardDownTo(g, pi, 10); } },
];

// ---- 4 種が順に重なった山 ----
const ROT = {
  p_augurs: ['herbalist2', 'acolyte', 'shrinemaiden', 'oracle2'],
  p_clashes: ['battleplan', 'archer', 'warlord', 'territory'],
  p_forts: ['pavilion', 'garrison', 'hillfort', 'citadel2'],
  p_odysseys: ['oldchart', 'voyage', 'sunkentreasure', 'distantshore'],
  p_townsfolk: ['crier2', 'blacksmith2', 'miller', 'elder'],
  p_wizards: ['wizstudent', 'conjurer', 'warlock', 'lich'],
};
const rotPiles = [
  { id: 'p_augurs', name: '卜占官', cost: 3, main: '4 種の山', desc: '薬草集め・侍祭・女魔導士・女予言者が 4 枚ずつ順に重なった山' },
  { id: 'p_clashes', name: '衝突', types: ['action', 'attack'], cost: 3, main: '4 種の山', desc: '戦闘計画・射手・将軍・領土が 4 枚ずつ順に重なった山' },
  { id: 'p_forts', name: '城砦', cost: 3, main: '4 種の山', desc: '天幕・駐屯地・堡塁・要塞が 4 枚ずつ順に重なった山' },
  { id: 'p_odysseys', name: '叙事詩', cost: 3, main: '4 種の山', desc: '古地図・航海・沈没船の財宝・遠い海岸が 4 枚ずつ順に重なった山' },
  { id: 'p_townsfolk', name: '町民', cost: 2, main: '4 種の山', desc: '触れ役・蹄鉄工・粉屋・長老が 4 枚ずつ順に重なった山' },
  { id: 'p_wizards', name: '魔法使い', cost: 3, main: '4 種の山', desc: '生徒・霊術師・魔導士・リッチが 4 枚ずつ順に重なった山' },
];
const inP = (pile) => ({ pile, notSupply: true });
const rotCards = [
  // 卜占官
  { id: 'herbalist2', ...inP('p_augurs'), name: '薬草集め', types: ['action', 'augur'], cost: 3, main: '+1 購入', desc: '山札を捨て札にし、捨て札の財宝を 1 枚使ってよい。卜占官を循環させてよい',
    *play(g, p, pi) {
      g.turn.buys += 1;
      p.discard.push(...p.deck.splice(0));
      const tr = p.discard.filter((id) => is(id, 'treasure'));
      const [i] = yield* askCards(g, pi, '使う財宝（なしでもよい）', tr, 0, 1);
      if (i != null) { p.discard.splice(p.discard.lastIndexOf(tr[i]), 1); yield* playNow(g, pi, tr[i]); }
      yield* mayRotate(g, pi, 'p_augurs');
    } },
  { id: 'acolyte', ...inP('p_augurs'), name: '侍祭', types: ['action', 'augur'], cost: 4, main: '廃棄して金貨', desc: '手札のアクションか勝利点を 1 枚廃棄してよい。そうしたら金貨を獲得。これを廃棄して占い師を獲得してよい',
    *play(g, p, pi) {
      const [i] = yield* askHand(g, pi, '廃棄するアクションか勝利点（しなくてもよい）', 0, 1, (id) => is(id, 'action') || is(id, 'victory'));
      if (i != null) { yield* trashCards(g, p, takeFromHand(p, [i])); yield* gain(g, pi, 'gold'); }
      if (g.playArea.includes('acolyte') && g.supply.p_augurs > 0 && (yield* askYesNo(g, pi, '侍祭を廃棄して占い師を獲得しますか？', 'する', 'しない'))) {
        if (yield* trashSelf(g, p, 'acolyte')) yield* gain(g, pi, 'p_augurs');
      }
    } },
  { id: 'shrinemaiden', ...inP('p_augurs'), name: '女魔導士', types: ['action', 'attack', 'augur'], cost: 5, main: '+1 アクション', desc: '名前を言い、山札の一番上をめくって手札に入れる。当たりなら、他の人は呪いを獲得',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const { named, top } = yield* nameAndReveal(g, pi, '当てる札の名前');
      if (top != null) p.hand.push(top);
      yield* attackOthers(g, function* (ti) { if (top === named) yield* gain(g, ti, 'curse'); });
    } },
  { id: 'oracle2', ...inP('p_augurs'), name: '女予言者', types: ['action', 'augur'], cost: 6, main: '+4 カード\n+1 アクション', desc: '手札を 1 枚山札の上に、もう 1 枚を山札の下に置く',
    *play(g, p, pi) {
      drawCards(p, 4); g.turn.actions += 1;
      const [a] = yield* askHand(g, pi, '山札の上に置く 1 枚', 1, 1);
      if (a != null) putOnDeck(p, takeFromHand(p, [a])[0]);
      const [b] = yield* askHand(g, pi, '山札の下に置く 1 枚', 1, 1);
      if (b != null) p.deck.unshift(takeFromHand(p, [b])[0]);
    } },
  // 衝突
  { id: 'battleplan', ...inP('p_clashes'), name: '戦闘計画', types: ['action', 'clash'], cost: 3, main: '+1 カード\n+1 アクション', desc: '手札のアタックを見せてよい。見せたら +1 カード。サプライの山を 1 つ循環させてよい',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      if (p.hand.some((id) => is(id, 'attack')) && (yield* askYesNo(g, pi, 'アタックを見せて +1 カードにしますか？', '見せる', 'しない'))) drawCards(p, 1);
      const piles = Object.keys(g.stacks).filter((k) => g.stacks[k].length);
      const [i] = yield* askCards(g, pi, '循環させる山（なしでもよい）', piles, 0, 1);
      if (i != null) rotatePile(g, piles[i]);
    } },
  { id: 'archer', ...inP('p_clashes'), name: '射手', types: ['action', 'attack', 'clash'], cost: 4, main: '+2 金', desc: '手札が 5 枚以上の他の人は、1 枚を残して手札を見せ、その中の 1 枚をあなたが選んで捨てさせる',
    *play(g, p, pi) {
      g.turn.money += 2;
      yield* attackOthers(g, function* (ti) {
        const t = g.players[ti];
        if (t.hand.length < 5) return;
        const [keep] = yield* askHand(g, ti, '見せずに残す 1 枚', 1, 1);
        const shown = t.hand.map((id, i) => ({ id, i })).filter((x) => x.i !== keep);
        const [k] = yield* askCards(g, pi, `${t.name}の手札から捨てさせる 1 枚`, shown.map((x) => x.id), 1, 1);
        yield* discardCards(g, t, takeFromHand(t, [shown[k ?? 0].i]));
      });
    } },
  { id: 'warlord', ...inP('p_clashes'), name: '将軍', types: ['action', 'duration', 'attack', 'clash'], cost: 5, main: '+1 アクション', desc: '次の手番の始めに +2 カード。それまで、他の人は場に 2 枚以上あるアクションを手札から使えない',
    *play(g, p) {
      g.turn.actions += 1;
      const hit = [];
      yield* attackOthers(g, function* (ti) { hit.push(ti); g.players[ti].tokens.warlorded = (g.players[ti].tokens.warlorded || 0) + 1; });
      later(g, 'warlord', function* () { for (const ti of hit) g.players[ti].tokens.warlorded -= 1; drawCards(p, 2); });
    } },
  { id: 'territory', ...inP('p_clashes'), name: '領土', types: ['victory', 'clash'], cost: 6, main: '勝利点の種類で点', desc: '持っている勝利点カードのちがう名前 1 種につき 1 点。獲得したとき、空のサプライの山 1 つにつき金貨を獲得',
    pointsFn: (all) => new Set(all.filter((id) => is(id, 'victory'))).size,
    *onGain(g, got) { for (let k = emptyPiles(g); k > 0; k--) yield* gain(g, got.pi, 'gold'); } },
  // 城砦
  { id: 'pavilion', ...inP('p_forts'), name: '天幕', types: ['action', 'fort'], cost: 3, main: '+2 金', desc: '城砦を循環させてよい。場から捨てるとき、山札の上に置いてよい',
    *play(g, p, pi) { g.turn.money += 2; yield* mayRotate(g, pi, 'p_forts'); },
    *onCleanup(g, p, pi) { if (g.playArea.includes('pavilion') && (yield* askYesNo(g, pi, '「天幕」を山札の上に置きますか？', '置く', 'しない', ['pavilion']))) putOnDeck(p, g.playArea.splice(g.playArea.indexOf('pavilion'), 1)[0]); } },
  { id: 'garrison', ...inP('p_forts'), name: '駐屯地', types: ['action', 'duration', 'fort'], cost: 4, main: '+2 金', desc: 'この手番に獲得するたびに印を 1 つ置く。次の手番の始めに、印 1 つにつき +1 カード',
    *play(g, p) {
      g.turn.money += 2;
      const start = g.turn.gained.length;
      g.turn.garrisons = (g.turn.garrisons || []);
      const entry = { start };
      g.turn.garrisons.push(entry);
      later(g, 'garrison', function* () { drawCards(p, entry.count || 0); });
    } },
  { id: 'hillfort', ...inP('p_forts'), name: '堡塁', types: ['action', 'fort'], cost: 5, main: 'コスト 4 以下を獲得', desc: 'それを手札に入れるか、+1 カード +1 アクションかを選ぶ',
    *play(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4);
      const toHand = yield* askYesNo(g, pi, 'どちらにしますか？', '手札に入れる', '+1 カード +1 アクション');
      yield* gain(g, pi, id, toHand ? 'hand' : 'discard');
      if (!toHand) { drawCards(p, 1); g.turn.actions += 1; }
    } },
  { id: 'citadel2', ...inP('p_forts'), name: '要塞', types: ['action', 'duration', 'victory', 'fort'], cost: 6, points: 2, main: '+3 金 か\n次の手番 +3 カード', desc: '2 点',
    *play(g, p, pi) { if (yield* askYesNo(g, pi, 'どちらにしますか？', '+3 金', '次の手番に +3 カード')) g.turn.money += 3; else later(g, 'citadel2', function* () { drawCards(p, 3); }); } },
  // 叙事詩
  { id: 'oldchart', ...inP('p_odysseys'), name: '古地図', types: ['action', 'odyssey'], cost: 3, main: '+1 カード\n+1 アクション', desc: '1 枚捨てて +1 カード。叙事詩を循環させてよい',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 1; yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚', 1, 1))); drawCards(p, 1); yield* mayRotate(g, pi, 'p_odysseys'); } },
  { id: 'voyage', ...inP('p_odysseys'), name: '航海', types: ['action', 'duration', 'odyssey'], cost: 4, main: '+1 アクション\n追加の手番', desc: '前の手番が自分でなければ、この手番のあとに追加の手番を行う（その手番は手札から 3 枚までしか使えない）',
    *play(g) { g.turn.actions += 1; if (!g.extraTurn) { g.turn.voyage = true; later(g, 'voyage', function* () {}); } } },
  { id: 'sunkentreasure', ...inP('p_odysseys'), name: '沈没船の財宝', types: ['treasure', 'odyssey'], cost: 5, main: '場にないアクションを獲得', desc: '場に同じ札がないアクションを 1 枚獲得する',
    *play(g, p, pi) { yield* gain(g, pi, yield* askSupply(g, pi, '場にないアクションを獲得', 99, (id) => is(id, 'action') && !g.playArea.includes(g.stacks[id] ? g.stacks[id].at(-1) : id))); } },
  { id: 'distantshore', ...inP('p_odysseys'), name: '遠い海岸', types: ['action', 'victory', 'odyssey'], cost: 6, points: 2, main: '+2 カード　+1 アクション\n屋敷を獲得', desc: '2 点',
    *play(g, p, pi) { drawCards(p, 2); g.turn.actions += 1; yield* gain(g, pi, 'estate'); } },
  // 町民
  { id: 'crier2', ...inP('p_townsfolk'), name: '触れ役', types: ['action', 'townsfolk'], cost: 2, main: '1 つ選ぶ', desc: '+2 金 / 銀貨を獲得 / +1 カード +1 アクション から 1 つ。町民を循環させてよい',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 'm', label: '+2 金' }, { value: 's', label: '銀貨を獲得' }, { value: 'c', label: '+1 カード +1 アクション' }]);
      if (v === 'm') g.turn.money += 2; else if (v === 's') yield* gain(g, pi, 'silver'); else { drawCards(p, 1); g.turn.actions += 1; }
      yield* mayRotate(g, pi, 'p_townsfolk');
    } },
  { id: 'blacksmith2', ...inP('p_townsfolk'), name: '蹄鉄工', types: ['action', 'townsfolk'], cost: 3, main: '1 つ選ぶ', desc: '手札が 6 枚になるまで引く / +2 カード / +1 カード +1 アクション から 1 つ',
    *play(g, p, pi) {
      const v = yield* askChoose(g, pi, '1 つ選ぶ', [{ value: 6, label: '6 枚まで引く' }, { value: 2, label: '+2 カード' }, { value: 1, label: '+1 カード +1 アクション' }]);
      if (v === 6) drawCards(p, Math.max(0, 6 - p.hand.length)); else if (v === 2) drawCards(p, 2); else { drawCards(p, 1); g.turn.actions += 1; }
    } },
  { id: 'miller', ...inP('p_townsfolk'), name: '粉屋', types: ['action', 'townsfolk'], cost: 4, main: '+1 アクション', desc: '山札の上 4 枚を見て、1 枚を手札に、残りを捨てる',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const seen = reveal(p, 4);
      if (!seen.length) return;
      const [i] = yield* askCards(g, pi, '手札に入れる 1 枚', seen, 1, 1);
      p.hand.push(...seen.splice(i ?? 0, 1));
      yield* discardCards(g, p, seen, true);
    } },
  { id: 'elder', ...inP('p_townsfolk'), name: '長老', types: ['action', 'townsfolk'], cost: 5, main: '+2 金', desc: '手札のアクションを 1 枚使ってよい（ponytail: 選択肢を 1 つ多く選べる効果はまだない）',
    *play(g, p, pi) { g.turn.money += 2; const [i] = yield* askHand(g, pi, '使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action')); if (i != null) yield* playNow(g, pi, takeFromHand(p, [i])[0]); } },
  // 魔法使い
  { id: 'wizstudent', ...inP('p_wizards'), name: '生徒', types: ['action', 'wizard', 'liaison'], cost: 3, main: '+1 アクション', desc: '魔法使いを循環させてよい。手札を 1 枚廃棄する。それが財宝なら +1 好意し、これを山札の上に置く',
    *play(g, p, pi) {
      g.turn.actions += 1;
      yield* mayRotate(g, pi, 'p_wizards');
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (is(id, 'treasure')) { favor(g, p, 1); const at = g.playArea.lastIndexOf('wizstudent'); if (at >= 0) putOnDeck(p, g.playArea.splice(at, 1)[0]); }
    } },
  { id: 'conjurer', ...inP('p_wizards'), name: '霊術師', types: ['action', 'duration', 'wizard'], cost: 4, main: 'コスト 4 以下を獲得', desc: '次の手番の始めに、これを手札に戻す',
    *play(g, p, pi) {
      yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を獲得', 4));
      later(g, 'conjurer', function* () { const at = g.playArea.indexOf('conjurer'); if (at >= 0) p.hand.push(...g.playArea.splice(at, 1)); });
    } },
  { id: 'warlock', ...inP('p_wizards'), name: '魔導士', types: ['action', 'attack', 'wizard'], cost: 5, main: '+1 カード\n+1 アクション', desc: '他の人は名前を 1 つ言って山札の一番上をめくる。外れたら呪いを獲得',
    *play(g, p) {
      drawCards(p, 1); g.turn.actions += 1;
      yield* attackOthers(g, function* (ti) {
        const { named, top } = yield* nameAndReveal(g, ti, '山札の一番上を当てる（外れたら呪い）');
        if (top != null) putOnDeck(g.players[ti], top);
        if (top !== named) yield* gain(g, ti, 'curse');
      });
    } },
  { id: 'lich', ...inP('p_wizards'), name: 'リッチ', types: ['action', 'wizard'], cost: 6, main: '+6 カード\n+2 アクション', desc: '次の自分の手番を飛ばす。廃棄したとき、それを捨て札にして、廃棄置き場のそれより安い札を 1 枚獲得する',
    *play(g, p) { drawCards(p, 6); g.turn.actions += 2; p.tokens.skip = (p.tokens.skip || 0) + 1; },
    *onTrash(g, p, pi) {
      const k = g.trash.lastIndexOf('lich');
      if (k < 0) return;
      g.trash.splice(k, 1);
      p.discard.push('lich');
      const opts = [...new Set(g.trash.filter((id) => costOf(g, id) < costOf(g, 'lich')))];
      if (!opts.length) return;
      const [i] = yield* askCards(g, pi, '廃棄置き場から獲得する札', opts, 1, 1);
      const id = opts[i ?? 0];
      g.trash.splice(g.trash.lastIndexOf(id), 1);
      yield* receive(g, pi, id);
    } },
];

// ---- 同盟（好意を使う。対局に 1 つ） ----
const AL = ['ally'];
const al = (id, name, main, desc) => ({ id, name, types: AL, cost: 0, main, desc });
const allies = [
  al('x_architects', '建築家ギルド', '好意 2 で\n安い札をもう 1 枚', '札を獲得したとき、好意 2 で、それより安い勝利点以外を獲得してよい'),
  al('x_nomads', '遊牧民団', '好意 1 で\n+カード・+アクション・+購入', 'コスト 3 以上を獲得したとき、好意 1 で +1 カード / +1 アクション / +1 購入 のどれか'),
  al('x_caves', '穴居民', '好意 1 で\n1 枚入れ替え', '手番の始めに、好意 1 ごとに 1 枚捨てて 1 枚引いてよい'),
  al('x_witches', '魔女の輪', '連携のあと好意 3 で\n呪い', '連携の札を使ったあと、好意 3 で他の人に呪いを獲得させてよい'),
  al('x_citystate', '都市国家', '好意 2 で\n獲得したアクションを使う', '自分の手番にアクションを獲得したとき、好意 2 でそれを使ってよい'),
  al('x_haven', '沿岸の避難港', '好意で手札を残す', '片付けで手札を捨てるとき、好意 1 ごとに 1 枚を手札に残してよい'),
  al('x_crafters', '工芸家ギルド', '好意 2 で\n山札の上に獲得', '手番の始めに、好意 2 でコスト 4 以下を山札の上に獲得してよい'),
  al('x_desert', '砂漠の案内人', '好意 1 で\n引き直す', '手番の始めに、好意 1 ごとに手札を捨てて 5 枚引き直してよい'),
  al('x_inventors', '発明家の家族', '好意で山を安く', '購入フェイズの始めに、好意 1 を勝利点以外の山に置いてよい。その山は好意 1 つにつきコストが 1 下がる'),
  al('x_scribes', '写本士の仲間たち', '手札 4 枚以下で\n好意 1 で +1 カード', 'アクションを使ったあと手札が 4 枚以下なら、好意 1 で +1 カード'),
  al('x_forest', '森の居住者', '好意 1 で\n上 3 枚を見る', '手番の始めに、好意 1 で山札の上 3 枚を見て、好きな枚数捨て、残りを好きな順に戻す'),
  al('x_pickpockets', 'すり師団', '好意 1 を払わないと\n手札 4 枚に', '手番の始めに、好意 1 を使わなければ、手札が 4 枚になるまで捨てる'),
  al('x_island', '島民', '好意 5 で\n追加の手番', '手番の終わりに、前の手番が自分でなければ、好意 5 で追加の手番を行ってよい'),
  al('x_bankers', '銀行家連盟', '好意 4 ごとに +1 金', '購入フェイズの始めに、持っている好意 4 ごとに +1 金'),
  al('x_shopkeepers', '小売店主連盟', '連携で +金 ほか', '連携の札を使ったあと、好意 5 以上なら +1 金、10 以上ならさらに +1 アクション +1 購入'),
  al('x_markettowns', '市場の町', '好意 1 で\nアクションを使う', '購入フェイズの始めに、好意 1 ごとに手札のアクションを 1 枚使ってよい'),
  al('x_mountain', '山の民', '好意 5 で +3 カード', '手番の始めに、好意 5 で +3 カード'),
  al('x_astrologers', '占星術師団', '混ぜたら好意で\n札を一番上に', '山札を混ぜたとき、好意 1 ごとに 1 枚を一番上に置いてよい（好意 1 で、いちばん高い札を自動で上にする）'),
  al('x_masons', 'メイソン団', '混ぜたら好意で\n2 枚を捨て札に', '山札を混ぜたとき、好意 1 ごとに 2 枚を捨て札に置いてよい（要らない札があれば、好意 1 で 2 枚まで自動で）'),
  al('x_cult', '平和的教団', '好意で廃棄', '購入フェイズの始めに、好意 1 ごとに手札を 1 枚廃棄してよい'),
  al('x_shepherds', '高原の羊飼い', '好意とコスト 2 の組で\n2 点', 'ゲームの終わりに、好意 1 とコスト 2 の札 1 枚の組 1 つにつき 2 点'),
  al('x_trappers', '罠師の小屋', '好意 1 で\n獲得を山札の上に', '札を獲得したとき、好意 1 でそれを山札の上に置いてよい'),
  al('x_woodworkers', '木工ギルド', '好意 1 で\nアクションを入れ替え', '購入フェイズの始めに、好意 1 で手札のアクションを廃棄し、アクションを獲得してよい'),
];
allies.find((a) => a.id === 'x_shepherds').score = (g, p, all) => 2 * Math.min(p.tokens.favors || 0, all.filter((id) => CARDS[id].cost === 2 && !CARDS[id].potion).length);

// ---- 決まり ----
HOOKS.setup.push((g) => {
  const n = g.players.length;
  for (const [pile, ids] of Object.entries(ROT)) {
    if (!g.kingdom.includes(pile)) continue;
    g.stacks[pile] = [...ids].reverse().flatMap((id) => Array(4).fill(id)); // 末尾（一番上）が最初の札
    g.supply[pile] = 16;
  }
  // 連携の札があれば、同盟を 1 つ入れる。同盟があれば全員が好意 1 から
  const liaison = [...g.kingdom, ...Object.values(ROT).filter((ids, k) => g.kingdom.includes(Object.keys(ROT)[k])).flat()].some((id) => is(id, 'liaison'));
  if (liaison && !g.landscapes.some((id) => is(id, 'ally'))) g.landscapes.push(shuffle(allies.map((a) => a.id))[0]);
  if (g.landscapes.some((id) => is(id, 'ally'))) for (const p of g.players) p.tokens.favors = 1;
  if (g.kingdom.includes('importer')) for (const p of g.players) p.tokens.favors = (p.tokens.favors || 0) + 4;
  g.pileFavor = {};
  void n;
});
HOOKS.cost.push((g, id) => (g.pileFavor ? g.pileFavor[pileOf(id)] || g.pileFavor[id] || 0 : 0));
HOOKS.shuffle.push((p, g) => {
  if (!g || !(p.tokens.favors > 0) || p.deck.length < 2) return;
  if (ally(g, 'x_astrologers')) {
    let best = 0;
    p.deck.forEach((id, i) => { if (CARDS[id].cost > CARDS[p.deck[best]].cost) best = i; });
    p.tokens.favors -= 1;
    p.deck.push(...p.deck.splice(best, 1));
  }
  if (ally(g, 'x_masons')) {
    const junk = p.deck.map((id, i) => ({ id, i })).filter((x) => x.id === 'curse' || (is(x.id, 'victory') && !is(x.id, 'action') && !is(x.id, 'treasure'))).slice(0, 2);
    if (!junk.length) return;
    p.tokens.favors -= 1;
    for (const x of [...junk].reverse()) p.discard.push(...p.deck.splice(x.i, 1));
  }
});
HOOKS.turnStart.push(function* (g, p, pi) {
  if (ally(g, 'x_pickpockets') && p.hand.length > 4 && !(yield* spend(g, pi, 1, 'すり師団: 好意を払って手札を捨てずにすませますか？'))) yield* discardDownTo(g, pi, 4);
  if (ally(g, 'x_mountain') && (yield* spend(g, pi, 5, '山の民: +3 カードにしますか？'))) drawCards(p, 3);
  if (ally(g, 'x_crafters') && (yield* spend(g, pi, 2, '工芸家ギルド: コスト 4 以下を山札の上に獲得しますか？'))) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 4 以下を山札の上に獲得', 4), 'deck');
  if (ally(g, 'x_forest') && (yield* spend(g, pi, 1, '森の居住者: 山札の上 3 枚を見ますか？'))) {
    const seen = reveal(p, 3);
    const idx = yield* askCards(g, pi, '捨てる札（好きな枚数）', seen, 0, seen.length);
    yield* discardCards(g, p, seen.filter((_, i) => idx.includes(i)), true);
    yield* putBackInOrder(g, pi, seen.filter((_, i) => !idx.includes(i)));
  }
  while (ally(g, 'x_caves') && p.hand.length && (yield* spend(g, pi, 1, '穴居民: 1 枚捨てて 1 枚引きますか？'))) { yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚', 1, 1))); drawCards(p, 1); }
  while (ally(g, 'x_desert') && (yield* spend(g, pi, 1, '砂漠の案内人: 手札を捨てて 5 枚引き直しますか？'))) { yield* discardCards(g, p, p.hand.splice(0), true); drawCards(p, 5); }
});
HOOKS.buyPhase.push(function* (g) {
  const pi = g.current;
  const p = currentPlayer(g);
  if (ally(g, 'x_bankers')) g.turn.money += Math.floor((p.tokens.favors || 0) / 4);
  while (ally(g, 'x_markettowns') && p.hand.some((id) => is(id, 'action')) && (yield* spend(g, pi, 1, '市場の町: 手札のアクションを使いますか？'))) {
    const [i] = yield* askHand(g, pi, '使うアクション', 1, 1, (id) => is(id, 'action'));
    if (i != null) yield* playNow(g, pi, takeFromHand(p, [i])[0]);
  }
  while (ally(g, 'x_cult') && p.hand.length && (yield* spend(g, pi, 1, '平和的教団: 手札を 1 枚廃棄しますか？'))) yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1)));
  if (ally(g, 'x_woodworkers') && p.hand.some((id) => is(id, 'action')) && (yield* spend(g, pi, 1, '木工ギルド: アクションを廃棄して、アクションを獲得しますか？'))) {
    yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄するアクション', 1, 1, (id) => is(id, 'action'))));
    yield* gain(g, pi, yield* askSupply(g, pi, 'アクションを獲得', 99, (id) => is(id, 'action')));
  }
  if (ally(g, 'x_inventors') && (yield* spend(g, pi, 1, '発明家の家族: 好意を山に置いてコストを下げますか？'))) {
    const piles = Object.keys(g.supply).filter((id) => !is(g.stacks[id] ? (g.stacks[id].at(-1) || id) : id, 'victory'));
    const [i] = yield* askCards(g, pi, '好意を置く山', piles, 1, 1);
    const id = piles[i ?? 0];
    g.pileFavor[id] = (g.pileFavor[id] || 0) + 1;
  }
});
HOOKS.afterAction.push(function* (g, id) {
  const pi = g.current;
  const p = currentPlayer(g);
  if (ally(g, 'x_scribes') && p.hand.length <= 4 && (yield* spend(g, pi, 1, '写本士の仲間たち: +1 カードにしますか？'))) drawCards(p, 1);
  if (is(id, 'liaison')) {
    if (ally(g, 'x_witches') && (yield* spend(g, pi, 3, '魔女の輪: 他の人に呪いを獲得させますか？'))) yield* eachOther(g, function* (ti) { yield* gain(g, ti, 'curse'); });
    if (ally(g, 'x_shopkeepers')) {
      if ((p.tokens.favors || 0) >= 5) g.turn.money += 1;
      if ((p.tokens.favors || 0) >= 10) { g.turn.actions += 1; g.turn.buys += 1; }
    }
  }
});
HOOKS.gain.push(function* (g, got) {
  const p = g.players[got.pi];
  const mine = got.pi === g.current;
  if (mine && g.turn.guildhead) favor(g, p, g.turn.guildhead);
  if (mine && g.turn.galleria && [3, 4].includes(costOf(g, got.id))) g.turn.buys += g.turn.galleria;
  if (mine && g.turn.skirmish && is(got.id, 'attack')) for (let k = 0; k < g.turn.skirmish; k++) yield* eachOther(g, (ti) => discardDownTo(g, ti, 3));
  if (mine && g.turn.garrisons) for (const e of g.turn.garrisons) e.count = (e.count || 0) + 1;
  if (ally(g, 'x_trappers') && got.to !== 'deck' && got.to !== 'gone' && got.to !== 'trash' && (yield* spend(g, got.pi, 1, `罠師の小屋: ${nm(got.id)}を山札の上に置きますか？`))) yield* relocate(g, got, 'deck');
  if (ally(g, 'x_architects') && costOf(g, got.id) > 0 && (yield* spend(g, got.pi, 2, `建築家ギルド: ${nm(got.id)}より安い札も獲得しますか？`))) {
    const c = costOf(g, got.id) - 1;
    yield* gain(g, got.pi, yield* askSupply(g, got.pi, `コスト ${c} 以下（勝利点以外）を獲得`, c, (x) => !is(x, 'victory')));
  }
  if (ally(g, 'x_nomads') && costOf(g, got.id) >= 3 && (yield* spend(g, got.pi, 1, '遊牧民団: +1 カード・+1 アクション・+1 購入のどれかを得ますか？'))) {
    // 自分の手番でなければ、+アクション・+購入は意味がないので +1 カードだけ
    const v = !mine ? 'c' : yield* askChoose(g, got.pi, '1 つ選ぶ', [{ value: 'c', label: '+1 カード' }, { value: 'a', label: '+1 アクション' }, { value: 'b', label: '+1 購入' }]);
    if (v === 'c') drawCards(p, 1); else if (v === 'a') g.turn.actions += 1; else g.turn.buys += 1;
  }
  if (ally(g, 'x_citystate') && mine && is(got.id, 'action') && got.to !== 'gone' && (yield* spend(g, got.pi, 2, `都市国家: 獲得した${nm(got.id)}を使いますか？`))) {
    if (yield* relocate(g, got, 'gone')) yield* playNow(g, got.pi, got.id);
  }
});
HOOKS.treasure.push(function* (g, id) {
  const p = currentPlayer(g);
  // 辻斬り: 各手番で最初に出した財宝は何もしない（お金を戻す）
  if (p.tokens.waylaid > 0 && !g.turn.waylaidUsed) { g.turn.waylaidUsed = true; g.turn.money -= CARDS[id].value || 0; log(g, `${nm(id)}は辻斬りで何もしなかった。`); }
});
HOOKS.endTurn.push(function* (g) {
  const pi = g.current;
  const p = currentPlayer(g);
  if (ally(g, 'x_island') && !g.extraTurn && (yield* spend(g, pi, 5, '島民: 追加の手番を行いますか？'))) g.turn.seize = true;
  if (ally(g, 'x_haven') && p.hand.length && (p.tokens.favors || 0) > 0) {
    const idx = yield* askHand(g, pi, `沿岸の避難港: 手札に残す札（好意 1 枚ずつ・残り ${p.tokens.favors}）`, 0, Math.min(p.tokens.favors, p.hand.length));
    if (idx.length) { p.tokens.favors -= idx.length; (p.mats.keep = p.mats.keep || []).push(...takeFromHand(p, idx)); }
  }
});

defineCards({ id: 'allies', name: '同盟' }, [...kingdom, ...rotPiles, ...rotCards, ...allies], [
  { id: 'firstally', name: 'はじめての同盟', cards: ['underling', 'flatterer', 'posttown', 'innkeeper', 'metropolis', 'marquess', 'masterbuilder', 'p_townsfolk', 'p_forts', 'importer'], landscapes: ['x_mountain'] },
  { id: 'wizardsway', name: '術者の道', cards: ['p_wizards', 'p_augurs', 'trinket', 'middleman', 'guildhead', 'go_between', 'picket', 'dispatch', 'modify', 'specialist'], landscapes: ['x_bankers'] },
  { id: 'clashofarms', name: 'いくさの行方', cards: ['p_clashes', 'p_odysseys', 'savage', 'waylayer', 'skirmisher', 'tracker2', 'galley', 'deed', 'exchange', 'tradecamp'], landscapes: ['x_island'] },
]);
