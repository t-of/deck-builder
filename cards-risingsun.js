'use strict';
// 拡張「旭日」のカード（王国 25 種）、予言 13 種、イベント 10 種。名前は本家と別の言い回し。
// 影（shadow）: 山札にあれば手札と同じように使える（engine の playShadow）。混ぜると山札の一番下へ。
// 前兆（omen）: +1 太陽 = 予言の上の太陽トークンを 1 つ取る。最後の 1 つを取ると、予言が効き始める。
// ponytail: 予言の「神風」（王国カードを入れ替える）と「悟り」（財宝をアクションとして使う）はまだ入れていない。
import {
  CARDS, HOOKS, defineCards, is, drawCards, takeTop, putOnDeck, takeFromHand, trashCards, discardCards,
  gain, costOf, askHand, askSupply, askCards, askChoose, askYesNo, attackOthers, eachOther, resolve, reveal,
  treasureEffect, later, returnCard, returnToPile, currentPlayer, receive, shuffle, pileOf, kingdomPool,
  takeFromSupply, relocate,
} from './engine.js';

const log = (g, text) => g.log.push(text);
const nm = (id) => `「${CARDS[id].name}」`;
const debt = (g, p, n) => { p.tokens.debt = (p.tokens.debt || 0) + n; log(g, `${p.name}が借金を ${n} 受け取った。`); };
const SH = ['action', 'shadow'];
const OM = ['action', 'omen'];
const prophecy = (g) => g.landscapes.find((id) => is(id, 'prophecy'));
const active = (g, id) => g.landscapes.includes(id) && g.sun === 0;
function* sun(g, pi) {
  if (!prophecy(g) || !(g.sun > 0)) return;
  g.sun -= 1;
  if (g.sun > 0) return;
  log(g, `予言「${CARDS[prophecy(g)].name}」が効き始めた。`);
  if (prophecy(g) === 'r_emperor') yield* emperorGift(g, pi);
}
function* emperorGift(g, pi) { yield* gain(g, pi, yield* askSupply(g, pi, '慈悲の帝: アクションを手札に獲得', 99, (id) => is(id, 'action')), 'hand'); }
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

const kingdom = [
  // ---- コスト 2〜3 ----
  { id: 'fishseller', name: '棒手振り', types: SH, cost: 2, main: '+1 購入\n+1 金', desc: '山札にあれば、手札と同じように使える（混ぜると山札の一番下へ）', *play(g) { g.turn.buys += 1; g.turn.money += 1; } },
  {
    id: 'snakecharmer', name: '蛇遣い', types: ['action', 'attack'], cost: 2, main: '+1 カード\n+1 アクション', desc: '手札に同じ札がなければ、手札を見せてこれを山に戻してよい。そうしたら他の人は災いを獲得する',
    *play(g, p, pi) {
      drawCards(p, 1); g.turn.actions += 1;
      const ok = new Set(p.hand).size === p.hand.length && g.playArea.includes('snakecharmer')
        && (yield* askYesNo(g, pi, '蛇遣いを山に戻して、他の人に災いを配りますか？', '戻す', 'しない'));
      if (ok) returnToPile(g, 'snakecharmer');
      yield* attackOthers(g, function* (ti) { if (ok) yield* gain(g, ti, 'curse'); });
    },
  },
  {
    id: 'courtnoble', name: '殿上人', cost: 3, main: '場の数で決まる', desc: '場の殿上人が 1・5 枚なら +3 アクション、2・6 枚なら +3 カード、3・7 枚なら +3 金、4・8 枚なら +3 購入',
    *play(g, p) {
      const n = ((g.playArea.filter((id) => id === 'courtnoble').length - 1) % 4) + 1;
      if (n === 1) g.turn.actions += 3; else if (n === 2) drawCards(p, 3); else if (n === 3) g.turn.money += 3; else g.turn.buys += 3;
    },
  },
  { id: 'meister', name: '名人', cost: 3, main: '+2 借金\nコスト 5 以下を獲得', desc: '', *play(g, p, pi) { debt(g, p, 2); yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下を獲得', 5)); } },
  {
    id: 'ferryboat', name: '屋形船', types: ['action', 'duration'], cost: 3, main: '次の手番に\n脇の札を使う', desc: '次の手番の始めに、対局の始めに脇に置いたコスト 5 のアクションとして使う（札は脇に残る）',
    *play(g, p, pi) { later(g, 'ferryboat', function* () { if (g.ferryCard) { log(g, `屋形船が${nm(g.ferryCard)}として働く。`); yield* resolve(g, g.ferryCard); } }); },
  },
  { id: 'cellar2', name: '土蔵', cost: 3, main: '+3 カード　+1 アクション\n+3 借金', desc: '', *play(g, p) { drawCards(p, 3); g.turn.actions += 1; debt(g, p, 3); } },
  // ---- コスト 4 ----
  { id: 'backalley', name: '横丁', types: SH, cost: 4, main: '+1 カード\n+1 アクション', desc: '1 枚捨てる。山札にあれば、手札と同じように使える',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 1; yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 1 枚', 1, 1))); } },
  {
    id: 'switchover', name: '入れ替え', cost: 4, main: '借金があれば +3 金', desc: '借金があれば +3 金。なければ手札を 1 枚廃棄し、それより高い札を獲得して、コストの差だけ借金を受け取る',
    *play(g, p, pi) {
      if (p.tokens.debt > 0) { g.turn.money += 3; return; }
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const c = costOf(g, id);
      const got = yield* askSupply(g, pi, `コスト ${c + 1} 以上の札を獲得（差の分だけ借金）`, 99, (x) => costOf(g, x) > c);
      if (yield* gain(g, pi, got)) debt(g, p, costOf(g, got) - c);
    },
  },
  { id: 'kunoichi', name: 'くノ一', types: ['action', 'attack', 'shadow'], cost: 4, main: '+1 カード', desc: '他の人は手札が 3 枚になるまで捨てる。山札にあれば、手札と同じように使える',
    *play(g, p) { drawCards(p, 1); yield* attackOthers(g, (ti) => discardDownTo(g, ti, 3)); } },
  { id: 'poet', name: '詠み人', types: OM, cost: 4, main: '+1 太陽\n+1 カード +1 アクション', desc: '山札の一番上をめくり、コスト 3 以下なら手札に入れる',
    *play(g, p, pi) {
      yield* sun(g, pi); drawCards(p, 1); g.turn.actions += 1;
      const [id] = reveal(p, 1);
      if (id == null) return;
      if (costOf(g, id) <= 3) p.hand.push(id); else putOnDeck(p, id);
    } },
  { id: 'rivershrine', name: '川の祠', types: OM, cost: 4, main: '+1 太陽\n2 枚まで廃棄', desc: '片付けの始めに、この手番の購入フェイズに何も獲得していなければ、コスト 4 以下を獲得する',
    *play(g, p, pi) { yield* sun(g, pi); yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, '廃棄する札（2 枚まで）', 0, 2))); g.turn.rivershrine = (g.turn.rivershrine || 0) + 1; } },
  { id: 'hillvillage', name: '山あいの村', types: OM, cost: 4, main: '+1 太陽\n+1 カード +2 アクション', desc: '2 枚捨てて +1 カードにしてよい',
    *play(g, p, pi) {
      yield* sun(g, pi); drawCards(p, 1); g.turn.actions += 2;
      if (p.hand.length >= 2 && (yield* askYesNo(g, pi, '2 枚捨てて +1 カードにしますか？', 'する', 'しない'))) { yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 2 枚', 2, 2))); drawCards(p, 1); }
    } },
  // ---- コスト 5 ----
  { id: 'goldmine', name: '金の鉱山', cost: 5, main: '+1 カード　+1 アクション\n+1 購入', desc: '金を獲得してよい。そうしたら +4 借金',
    *play(g, p, pi) { drawCards(p, 1); g.turn.actions += 1; g.turn.buys += 1; if ((yield* askYesNo(g, pi, '金を獲得して +4 借金にしますか？', 'する', 'しない')) && (yield* gain(g, pi, 'gold'))) debt(g, p, 4); } },
  { id: 'imperialenvoy', name: '宮の使い', cost: 5, main: '+5 カード　+1 購入\n+2 借金', desc: '', *play(g, p) { drawCards(p, 5); g.turn.buys += 1; debt(g, p, 2); } },
  {
    id: 'kitsune', name: '化け狐', types: ['action', 'attack', 'omen'], cost: 5, main: '+1 太陽\n2 つ選ぶ', desc: '+2 アクション / +2 金 / 他の人は災いを獲得 / 銀を獲得 から、ちがうものを 2 つ',
    *play(g, p, pi) {
      yield* sun(g, pi);
      const all = [{ value: 'a', label: '+2 アクション' }, { value: 'm', label: '+2 金' }, { value: 'c', label: '他の人に災い' }, { value: 's', label: '銀を獲得' }];
      const a = yield* askChoose(g, pi, '1 つめ', all);
      const b = yield* askChoose(g, pi, '2 つめ', all.filter((c) => c.value !== a));
      const picks = [a, b];
      if (picks.includes('a')) g.turn.actions += 2;
      if (picks.includes('m')) g.turn.money += 2;
      if (picks.includes('s')) yield* gain(g, pi, 'silver');
      yield* attackOthers(g, function* (ti) { if (picks.includes('c')) yield* gain(g, ti, 'curse'); });
    },
  },
  { id: 'palanquin', name: 'かご', cost: 5, main: '+2 カード　+2 アクション\n+1 借金', desc: '', *play(g, p) { drawCards(p, 2); g.turn.actions += 2; debt(g, p, 1); } },
  { id: 'ricedealer', name: '米問屋', cost: 5, main: '+1 アクション', desc: '手札を 1 枚廃棄する。財宝なら +2 カード、アクションなら +5 カード',
    *play(g, p, pi) {
      g.turn.actions += 1;
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (is(id, 'treasure')) drawCards(p, 2);
      if (is(id, 'action')) drawCards(p, 5);
    } },
  { id: 'ronin', name: '素浪人', types: SH, cost: 5, main: '7 枚まで引く', desc: '山札にあれば、手札と同じように使える', *play(g, p) { drawCards(p, Math.max(0, 7 - p.hand.length)); } },
  { id: 'tanuki', name: '化け狸', types: SH, cost: 5, main: '廃棄して格上げ', desc: '手札を 1 枚廃棄し、そのコスト +2 以下を獲得する。山札にあれば、手札と同じように使える',
    *play(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      const max = costOf(g, id) + 2;
      yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${max} 以下を獲得`, max));
    } },
  { id: 'teahouse', name: '茶店', types: OM, cost: 5, main: '+1 太陽　+1 カード\n+1 アクション　+2 金', desc: '', *play(g, p, pi) { yield* sun(g, pi); drawCards(p, 1); g.turn.actions += 1; g.turn.money += 2; } },
  { id: 'peakshrine', name: '峰の祠', types: OM, cost: 0, debt: 5, main: '+1 太陽\n+2 金', desc: '手札を 1 枚廃棄してよい。そのあと廃棄置き場にアクションがあれば +2 カード',
    *play(g, p, pi) {
      yield* sun(g, pi); g.turn.money += 2;
      const [i] = yield* askHand(g, pi, '廃棄する 1 枚（しなくてもよい）', 0, 1);
      if (i != null) yield* trashCards(g, p, takeFromHand(p, [i]));
      if (g.trash.some((id) => is(id, 'action'))) drawCards(p, 2);
    } },
  // ---- コスト 6〜 ----
  { id: 'bushi', name: '武士', types: ['action', 'duration', 'attack'], cost: 6, main: '手札を 3 枚に\nずっと毎手番 +1 金', desc: '他の人は手札が 3 枚になるまで捨てる（1 度だけ）。このあとの毎手番の始めに +1 金（場に残り続ける）',
    *play(g) {
      yield* attackOthers(g, (ti) => discardDownTo(g, ti, 3));
      const job = function* () { g.turn.money += 1; later(g, 'bushi', job); };
      later(g, 'bushi', job);
    } },
  { id: 'tonosama', name: '殿様', types: ['action', 'command'], cost: 0, debt: 6, main: '+1 カード\n+1 アクション', desc: 'この手番、次に使った命令でないアクションを、もう一度使う',
    *play(g, p) { drawCards(p, 1); g.turn.actions += 1; g.turn.daimyo = (g.turn.daimyo || 0) + 1; } },
  { id: 'painter', name: '絵描き', cost: 0, debt: 8, main: '+1 アクション', desc: '場にちょうど 1 枚だけの札 1 種につき +1 カード',
    *play(g, p) { g.turn.actions += 1; drawCards(p, [...new Set(g.playArea)].filter((id) => g.playArea.filter((x) => x === id).length === 1).length); } },
  { id: 'ricebale', name: '米俵', types: ['treasure'], cost: 7, autoPlay: true, main: '+1 購入\n場の種類の数 +金', desc: '場の札の種類（アクション・財宝など）1 つにつき +1 金',
    *play(g) { g.turn.buys += 1; g.turn.money += new Set(g.playArea.flatMap((id) => CARDS[id].types)).size; } },
];

// ---- 予言（前兆の太陽トークンがなくなると効き始める） ----
const PR = ['prophecy'];
const pr = (id, name, main, desc) => ({ id, name, types: PR, cost: 0, main, desc });
const prophecies = [
  pr('r_army', '迫る軍勢', 'アタックのあと +1 金', 'アタックを使ったあと +1 金'),
  pr('r_biding', '待ちの時', '手札を持ち越す', '片付けの始めに手札を脇に置き、次の手番の始めに手札に戻す'),
  pr('r_bureau', 'お役所仕事', '獲得で銅', 'コスト 0 でない札を獲得したとき、銅を獲得する'),
  pr('r_trade', '商いの花', 'コスト -1', 'カードのコストが 1 下がる'),
  pr('r_harvest', '豊年', '財宝の初出しで\n+1 購入 +1 金', '各手番で、ちがう名前の財宝をはじめて使うとき、先に +1 購入 +1 金'),
  pr('r_leader', '名君', 'アクションで\n+1 アクション', 'アクションを使うたび +1 アクション'),
  pr('r_growth', '伸び盛り', '財宝で安い札も', '財宝を獲得したとき、それより安い札を獲得する'),
  pr('r_winter', '冬の厳しさ', '山に借金', '自分の手番に獲得したとき、その山に借金があれば受け取り、なければ借金 2 を置く'),
  pr('r_emperor', '慈悲の帝', '手番の始めに\nアクションを手札に', '手番の始め（と効き始めたとき）に、アクションを手札に獲得する'),
  pr('r_panic', '大慌て', '財宝で +2 購入', '財宝を使うと +2 購入。場から財宝を捨てるとき、山に戻す'),
  pr('r_progress', '前進', '獲得は山札の上', '獲得した札は山札の上に置く'),
  pr('r_rapid', '急な広がり', '獲得したら\n次の手番に使う', 'アクションか財宝を獲得したとき、脇に置いて次の手番の始めに使う'),
  pr('r_sickness', '病み', '災いか 3 枚捨て', '手番の始めに、災いを山札の上に獲得するか、3 枚捨てるかを選ぶ'),
];

// ---- イベント ----
const E = ['event'];
const events = [
  { id: 're_amass', name: '寄せ集め', types: E, cost: 2, main: 'アクションを獲得', desc: '場にアクションがなければ、コスト 5 以下のアクションを獲得する',
    *buy(g, p, pi) { if (!g.playArea.some((id) => is(id, 'action'))) yield* gain(g, pi, yield* askSupply(g, pi, 'コスト 5 以下のアクションを獲得', 5, (id) => is(id, 'action'))); } },
  { id: 're_ascetic', name: '修行', types: E, cost: 2, main: '払った分だけ廃棄', desc: 'お金を好きなだけ払い、同じ枚数の手札を廃棄する',
    *buy(g, p, pi) {
      const max = Math.min(g.turn.money, p.hand.length);
      const n = yield* askChoose(g, pi, '何金払いますか？', Array.from({ length: max + 1 }, (_, k) => ({ value: k, label: `${k} 金` })));
      g.turn.money -= n;
      yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, `廃棄する ${n} 枚`, n, n)));
    } },
  { id: 're_credit', name: 'つけ払い', types: E, cost: 2, main: '借金で獲得', desc: 'コスト 8 以下のアクションか財宝を獲得し、そのコストと同じ借金を受け取る',
    *buy(g, p, pi) { const id = yield* askSupply(g, pi, 'コスト 8 以下のアクションか財宝を獲得', 8, (x) => is(x, 'action') || is(x, 'treasure')); if (yield* gain(g, pi, id)) debt(g, p, costOf(g, id)); } },
  { id: 're_foresight', name: '先読み', types: E, cost: 2, main: 'アクションを手札に', desc: 'アクションが出るまで山札をめくり、それを脇に置いて手番の終わりに手札へ。ほかは捨てる',
    *buy(g, p) {
      const other = [];
      for (let id = takeTop(p); id != null; id = takeTop(p)) { if (is(id, 'action')) { (p.mats.laterhand = p.mats.laterhand || []).push(id); break; } other.push(id); }
      yield* discardCards(g, p, other, true);
    } },
  { id: 're_kintsugi', name: '継ぎ直し', types: E, cost: 3, main: '廃棄して格上げ', desc: '手札を 1 枚廃棄する。この対局で金を獲得していれば、そのコスト +2 以下を獲得する',
    *buy(g, p, pi) {
      const [id] = takeFromHand(p, yield* askHand(g, pi, '廃棄する 1 枚', 1, 1));
      if (!id) return;
      yield* trashCards(g, p, [id]);
      if (p.tokens.gainedGold) yield* gain(g, pi, yield* askSupply(g, pi, `コスト ${costOf(g, id) + 2} 以下を獲得`, costOf(g, id) + 2));
    } },
  { id: 're_practice', name: 'おさらい', types: E, cost: 3, main: 'アクションを 2 回', desc: '手札のアクションを 1 枚、2 回使ってよい',
    *buy(g, p, pi) {
      const [i] = yield* askHand(g, pi, '2 回使うアクション（なしでもよい）', 0, 1, (id) => is(id, 'action'));
      if (i == null) return;
      const [id] = takeFromHand(p, [i]);
      g.playArea.push(id);
      yield* resolve(g, id); yield* resolve(g, id);
    } },
  { id: 're_seatrade', name: '海の商い', types: E, cost: 4, main: '場のアクションの数\nだけ引いて廃棄', desc: '場のアクション 1 枚につき +1 カード。そのあと、その枚数まで手札を廃棄する',
    *buy(g, p, pi) { const n = g.playArea.filter((id) => is(id, 'action')).length; drawCards(p, n); yield* trashCards(g, p, takeFromHand(p, yield* askHand(g, pi, `廃棄する札（${n} 枚まで）`, 0, n))); } },
  { id: 're_tribute', name: '献上', types: E, cost: 5, main: 'アクションを 3 種', desc: 'この手番に 3 枚以上獲得していれば、場にないちがう名前のアクションを 3 枚まで獲得する',
    *buy(g, p, pi) {
      if (g.turn.gained.length < 3) return;
      const opts = Object.keys(g.supply).filter((id) => g.supply[id] > 0 && is(id, 'action') && !g.playArea.includes(id));
      const idx = yield* askCards(g, pi, '獲得するアクション（3 枚まで）', opts, 0, 3);
      for (const i of idx) yield* gain(g, pi, opts[i]);
    } },
  { id: 're_gather', name: '取りそろえ', types: E, cost: 7, main: 'コスト 3・4・5 を\n1 枚ずつ', desc: '',
    *buy(g, p, pi) { for (const c of [3, 4, 5]) yield* gain(g, pi, yield* askSupply(g, pi, `ちょうどコスト ${c} を獲得`, c, (x) => costOf(g, x) === c)); } },
  { id: 're_continue', name: '続行', types: E, cost: 0, debt: 8, once: true, main: 'アクションを獲得して\nすぐ使う', desc: '1 手番に 1 度: コスト 4 以下のアタックでないアクションを獲得し、アクションフェイズに戻ってそれを使う。+1 アクション +1 購入',
    *buy(g, p, pi) {
      const id = yield* askSupply(g, pi, 'コスト 4 以下のアクション（アタック以外）', 4, (x) => is(x, 'action') && !is(x, 'attack'));
      if (!(yield* gain(g, pi, id))) return;
      g.turn.phase = 'action';
      const real = p.discard.at(-1);
      if (real && pileOf(real) === pileOf(id)) { p.discard.pop(); yield* playNow(g, pi, real); }
      g.turn.actions += 1; g.turn.buys += 1;
    } },
];

// ---- 決まり ----
HOOKS.setup.push((g) => {
  const n = g.players.length;
  const omen = g.kingdom.some((id) => is(id, 'omen'));
  if (omen && !prophecy(g)) g.landscapes.push(shuffle(prophecies.map((x) => x.id))[0]);
  if (prophecy(g)) g.sun = n === 2 ? 5 : n === 3 ? 8 : 10;
  if (g.kingdom.includes('ferryboat')) {
    const pool = kingdomPool().filter((id) => !(id in g.supply) && CARDS[id].cost === 5 && is(id, 'action') && !is(id, 'duration') && CARDS[id].play && !CARDS[id].pile);
    g.ferryCard = pool.length ? shuffle(pool)[0] : null;
  }
});
HOOKS.cost.push((g) => (g.landscapes && active(g, 'r_trade') ? 1 : 0));
HOOKS.play.push(function* (g, id) {
  if (active(g, 'r_leader')) g.turn.actions += 1;
  if (g.turn.daimyo > 0 && !is(id, 'command')) { g.turn.daimyo -= 1; g.turn.daimyoAgain = id; }
});
HOOKS.afterAction.push(function* (g, id) {
  if (g.turn.daimyoAgain === id) { g.turn.daimyoAgain = null; log(g, `殿様で${nm(id)}をもう一度使う。`); yield* resolve(g, id); }
  if (active(g, 'r_army') && is(id, 'attack')) g.turn.money += 1;
});
HOOKS.treasure.push(function* (g, id) {
  if (active(g, 'r_harvest')) { g.turn.harvested = g.turn.harvested || []; if (!g.turn.harvested.includes(id)) { g.turn.harvested.push(id); g.turn.buys += 1; g.turn.money += 1; } }
  if (active(g, 'r_panic')) g.turn.buys += 2;
});
HOOKS.gain.push(function* (g, got) {
  const pi = got.pi;
  const p = g.players[pi];
  if (got.id === 'gold') p.tokens.gainedGold = true;
  if (!g.landscapes || !prophecy(g) || g.sun !== 0) return;
  if (active(g, 'r_bureau') && costOf(g, got.id) !== 0 && got.id !== 'copper') yield* gain(g, pi, 'copper');
  if (active(g, 'r_growth') && is(got.id, 'treasure') && costOf(g, got.id) > 0) yield* gain(g, pi, yield* askSupply(g, pi, `伸び盛り: コスト ${costOf(g, got.id) - 1} 以下を獲得`, costOf(g, got.id) - 1));
  if (active(g, 'r_winter') && pi === g.current) {
    const pile = pileOf(got.id) in g.supply ? pileOf(got.id) : got.id;
    if (g.pileDebt[pile] > 0) { debt(g, p, g.pileDebt[pile]); g.pileDebt[pile] = 0; } else g.pileDebt[pile] = 2;
  }
  if (active(g, 'r_progress') && got.to !== 'deck' && got.to !== 'gone' && got.to !== 'trash') yield* relocate(g, got, 'deck');
  if (active(g, 'r_rapid') && (is(got.id, 'action') || is(got.id, 'treasure')) && got.to !== 'gone' && (yield* relocate(g, got, 'gone'))) {
    const id = got.id;
    (p.mats.rapid = p.mats.rapid || []).push(id);
    p.nextTurn.push(function* (gg, pp, ppi) { const k = pp.mats.rapid.indexOf(id); if (k >= 0) { pp.mats.rapid.splice(k, 1); yield* playNow(gg, ppi, id); } });
  }
});
HOOKS.turnStart.push(function* (g, p, pi) {
  if (active(g, 'r_emperor')) yield* emperorGift(g, pi);
  if (active(g, 'r_sickness')) {
    if (yield* askYesNo(g, pi, '病み: どちらにしますか？', '災いを山札の上に獲得', '3 枚捨てる')) yield* gain(g, pi, 'curse', 'deck');
    else yield* discardCards(g, p, takeFromHand(p, yield* askHand(g, pi, '捨てる 3 枚', 3, 3)));
  }
});
HOOKS.endTurn.push(function* (g) {
  const p = currentPlayer(g);
  const pi = g.current;
  // 川の祠: 購入フェイズに何も獲得していなければ、コスト 4 以下を獲得
  for (let k = g.turn.rivershrine || 0; k > 0; k--) if (!g.turn.bought.length) yield* gain(g, pi, yield* askSupply(g, pi, '川の祠: コスト 4 以下を獲得', 4));
  if (active(g, 'r_panic')) for (const id of [...g.playArea]) if (is(id, 'treasure') && !g.turn.stay.includes(id)) { g.playArea.splice(g.playArea.indexOf(id), 1); if (!returnCard(g, id)) p.discard.push(id); }
  if (active(g, 'r_biding') && p.hand.length) (p.mats.biding = p.mats.biding || []).push(...p.hand.splice(0));
});
HOOKS.turnStart.push(function* (g, p) { if (p.mats.biding && p.mats.biding.length) p.hand.push(...p.mats.biding.splice(0)); });

defineCards({ id: 'risingsun', name: '旭日' }, [...kingdom, ...prophecies, ...events], [
  { id: 'dawn', name: '夜明け', cards: ['fishseller', 'courtnoble', 'meister', 'cellar2', 'backalley', 'poet', 'hillvillage', 'goldmine', 'teahouse', 'ronin'], landscapes: ['r_harvest', 're_amass'] },
  { id: 'shadowplay', name: '影の舞台', cards: ['kunoichi', 'tanuki', 'fishseller', 'backalley', 'ronin', 'kitsune', 'snakecharmer', 'switchover', 'ricedealer', 'bushi'], landscapes: ['r_leader', 're_practice'] },
  { id: 'debtandhonor', name: '借りと誉れ', cards: ['tonosama', 'painter', 'peakshrine', 'imperialenvoy', 'palanquin', 'rivershrine', 'ferryboat', 'ricebale', 'meister', 'cellar2'], landscapes: ['r_winter', 're_credit'] },
]);
