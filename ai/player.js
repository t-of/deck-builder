'use strict';
// 学習した AI の打ち手（画面・音に触らない。docs/ai-design.md §1）。
// 買う・獲得する判断（自分が獲得する supply の問い）だけ、候補ごとに net で「買ったあとの状態」を比べて選ぶ。
// それ以外の判断は、さいきょう CPU（cpu.js の expert）に任せる。
//   createAI(model, opts) → { nextMove(game), answer(game, q) }   … cpu.js の nextMove・answer と同じ形
//   expertActor(opts)     → 同じ形。さいきょう CPU のまま打つ（opts.onDecision があれば、買う・獲得する判断を知らせる）
//   playGame({ kingdom, landscapes, actors, seed }) → 終わった game（打ち切りは null）。actors[席] で席ごとに打つ
// opts.temperature: 0 なら一番見込みの高い候補、> 0 なら 見込み/温度 の softmax で選ぶ（探る）
// opts.onDecision({ source, game, me, base, cands, chosen }): 判断のたびに呼ぶ（記録用）。source は 'ai' か 'expert'
import {
  is, currentPlayer, isTreasureNow, newGame, beginTurn, playAction, playShadow, spendVillager, enterBuyPhase, playTreasureGen,
  spendCoffers, buyCard, buyEvent, enterNightPhase, playNight, endTurn, turnController,
} from '../engine.js';
import { nextMove as cpuMove, answer as cpuAnswer, wantedDirection } from '../cpu.js';
import { encode, buyCandidates, gainCandidates, startLedger, KIND } from './features.js';
import { scoreCandidates } from './net.js';

// 自分が獲得する問い（候補を比べられるもの）か。読めない問いは手書きに回す
export function isGainQuestion(game, q) {
  if (q.type !== 'supply') return false;
  if (/印を置く|借金を 2 つ置く|指定する/.test(q.purpose)) return false;
  return wantedDirection(q, game) === 'best';
}

// 買う判断の場面か（財宝を出し終わって、購入が残っている）
export function isBuyDecision(game) {
  const p = currentPlayer(game);
  const t = game.turn;
  if (t.phase !== 'buy' || t.buys <= 0) return false;
  const limited = t.handPlayLimit != null && (t.handPlays || 0) >= t.handPlayLimit;
  return limited || !p.hand.some((id) => isTreasureNow(game, id));
}

export const noBuyMove = (p) => (p.hand.some((id) => is(id, 'night')) ? { type: 'nightPhase' } : { type: 'end' });

function softmaxPick(scores, temperature, rand) {
  if (!(temperature > 0)) return scores.indexOf(Math.max(...scores));
  const mx = Math.max(...scores);
  const w = scores.map((s) => Math.exp((s - mx) / temperature));
  let r = rand() * w.reduce((a, b) => a + b, 0);
  for (let i = 0; i < w.length; i++) { r -= w[i]; if (r <= 0) return i; }
  return w.length - 1;
}

export function createAI(model, { temperature = 0, rand = Math.random, onDecision } = {}) {
  let pending = null; // 財源を使った直後に買う札
  const choose = (game, me, base, cands) => {
    if (cands.length === 1) return 0;
    const chosen = softmaxPick(scoreCandidates(model, base, cands), temperature, rand);
    if (onDecision) onDecision({ source: 'ai', game, me, base, cands, chosen });
    return chosen;
  };
  return {
    nextMove(game) {
      const p = currentPlayer(game);
      if (!isBuyDecision(game)) return cpuMove(game, 'expert');
      if (pending) { const m = pending; pending = null; return m; }
      const base = encode(game, game.current);
      const cands = buyCandidates(base);
      const c = cands[choose(game, game.current, base, cands)];
      if (c.kind === KIND.none) return noBuyMove(p);
      const move = c.kind === KIND.event ? { type: 'event', id: c.pile } : { type: 'buy', id: c.pile };
      if (c.coffers) { pending = move; return { type: 'coffers', n: c.coffers }; }
      return move;
    },
    answer(game, q) {
      if (!isGainQuestion(game, q)) return cpuAnswer(game, q, 'expert');
      const me = q.owner ?? q.player;
      const base = encode(game, me);
      const cands = gainCandidates(base, q);
      const c = cands[choose(game, me, base, cands)];
      return c.kind === KIND.none ? null : c.pile;
    },
  };
}

// さいきょう CPU。onDecision があれば、買う・獲得する判断で候補の一覧と選んだ番号を知らせる
export function expertActor({ onDecision } = {}) {
  let pend = null; // 財源を使った判断（次の買う手で決まる）
  const report = (game, me, base, cands, chosen) => { if (chosen >= 0) onDecision({ source: 'expert', game, me, base, cands, chosen }); };
  return {
    nextMove(game) {
      if (!onDecision || !isBuyDecision(game)) return cpuMove(game, 'expert');
      const me = game.current;
      const base = pend ? pend.base : encode(game, me);
      const cands = pend ? pend.cands : buyCandidates(base);
      const n = pend ? pend.n : 0;
      const m = cpuMove(game, 'expert');
      if (m.type === 'coffers') { pend = { base, cands, n: m.n }; return m; }
      pend = null;
      const at = m.type === 'buy' ? cands.findIndex((c) => c.kind === KIND.buy && c.pile === m.id && c.coffers === n)
        : m.type === 'event' ? cands.findIndex((c) => c.kind === KIND.event && c.pile === m.id && c.coffers === n)
          : cands.findIndex((c) => c.kind === KIND.none);
      report(game, me, base, cands, at);
      return m;
    },
    answer(game, q) {
      if (!onDecision || !isGainQuestion(game, q)) return cpuAnswer(game, q, 'expert');
      const me = q.owner ?? q.player;
      const base = encode(game, me);
      const cands = gainCandidates(base, q);
      const a = cpuAnswer(game, q, 'expert');
      report(game, me, base, cands, cands.findIndex((c) => (a == null ? c.kind === KIND.none : c.pile === a)));
      return a;
    },
  };
}

const STALL = new Error('問いが終わらない');

// cpu.js の simulate と同じ進め方で 1 局打つ
export function playGame({ kingdom, landscapes = [], actors, seed }) {
  const g = newGame(actors.length, kingdom, actors.map((_, i) => `P${i + 1}`), { landscapes, ...(seed != null ? { seed } : {}) });
  g.cpuPlans = {};
  startLedger(g);
  const run = (gen) => {
    let st = gen.next();
    for (let k = 0; !st.done; k++) {
      if (k > 3000) throw STALL;
      st = gen.next(actors[st.value.player].answer(g, st.value));
    }
    return st.value;
  };
  try {
    for (let turns = 0; !g.over; turns++) {
      if (turns > 300) return null;
      run(beginTurn(g));
      const a = actors[turnController(g)];
      for (let steps = 0; steps < 400; steps++) {
        const m = a.nextMove(g);
        if (m.type === 'action') run(playAction(g, m.id));
        else if (m.type === 'shadow') run(playShadow(g, m.id));
        else if (m.type === 'villager') spendVillager(g);
        else if (m.type === 'buyPhase') run(enterBuyPhase(g));
        else if (m.type === 'treasure') run(playTreasureGen(g, m.id));
        else if (m.type === 'coffers') spendCoffers(g, m.n);
        else if (m.type === 'buy') { if (!run(buyCard(g, m.id))) break; }
        else if (m.type === 'event') run(buyEvent(g, m.id));
        else if (m.type === 'nightPhase') enterNightPhase(g);
        else if (m.type === 'night') run(playNight(g, m.id));
        else break;
      }
      run(endTurn(g));
    }
  } catch (e) { if (e === STALL) return null; throw e; } // 問いが終わらない局も打ち切り扱い
  return g;
}
