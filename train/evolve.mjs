// 買い方表を進化で作る（docs/ai-specialize.md §3-1）。王国は 1 つに固定（既定 first）。表の形は ai/table.js。
//   node train/evolve.mjs --name e1 --gens 100 [--pop 64] [--opps 8] [--games 50] [--procs 8] [--seed 1] [--preset first]
// 各個体は「過去の優良個体（hof。最初は手書きの定石）」と 1 組あたり --games 局（先後交代）打ち、勝率（引き分け 0.5）の平均が適応度。
// 上位 1/8 はそのまま残し、残りは上位半分の交叉＋突然変異。世代ごとに runs/<name>/gen_<N>.json（top ＝上位 8 個、next ＝次の集団、hof）を書く。
// 止まったら同じコマンドで続きから回る（最後の gen_N.json から）。--gens は「この世代数になるまで」。
import fs from 'node:fs';
import os from 'node:os';
import { fork } from 'node:child_process';
import { PRESETS, finalResults } from '../engine.js';
import { playGame } from '../ai/player.js';
import { tableActor, SEEDS } from '../ai/table.js';

const dir = new URL('..', import.meta.url).pathname;
const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : (process.argv[i + 1] ?? true); };
const mulberry = (s) => () => { s = (s + 0x6d2b79f5) >>> 0; let t = Math.imul(s ^ (s >>> 15), s | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

const loadCards = async () => { for (const f of fs.readdirSync(dir).filter((f) => /^cards-.*\.js$/.test(f)).sort()) await import(`../${f}`); };

if (process.argv.includes('--worker')) {
  // 子プロセス: { table, opps, games, seed, preset } を受けて、勝ち点（勝 1・分 0.5）の合計を返す
  const loaded = loadCards(); // 読み込み中に届いた仕事も取りこぼさないよう、先に受け口を作る
  process.on('message', async ({ id, table, opps, games, seed, preset }) => {
    await loaded;
    const rnd = mulberry(seed); Math.random = rnd;
    const kingdom = [...PRESETS.find((p) => p.id === preset).cards];
    let pts = 0; let n = 0;
    for (const o of opps) {
      for (let i = 0; i < games; i++) {
        const seat = i % 2;
        const g = playGame({ kingdom, actors: [0, 1].map((s) => tableActor(s === seat ? table : o)), seed: Math.floor(rnd() * 2 ** 31) });
        if (!g) continue;
        const top = finalResults(g).filter((x) => x.rank === 1);
        pts += top.length > 1 ? 0.5 : top[0].index === seat ? 1 : 0; n++;
      }
    }
    process.send({ id, pts, n });
  });
} else {
  await loadCards();
  await main();
}

async function main() {
  const name = arg('name', 'e1');
  const POP = Number(arg('pop', 64)); const GENS = Number(arg('gens', 100)); const OPPS = Number(arg('opps', 8)); const GAMES = Number(arg('games', 50));
  const procs = Number(arg('procs', process.env.SLURM_NTASKS || os.cpus().length)); const seed0 = Number(arg('seed', 1));
  const preset = arg('preset', 'first');
  const pr = PRESETS.find((p) => p.id === preset);
  if (!pr) { console.error(`知らない preset: ${preset}`); process.exit(1); }
  if (preset !== 'first') console.error('警告: 手書きの定石は first の札用。初期集団が弱くなる');
  const cards = [...pr.cards, 'silver', 'gold'];
  const out = `${dir}runs/${name}`; fs.mkdirSync(out, { recursive: true });

  // ---- 表の変異・交叉 ----
  const pick = (a, r) => a[Math.floor(r() * a.length)];
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
  const step = (x, r, lo, hi, k = 1) => clamp(x + (r() < 0.5 ? -1 : 1) * (1 + Math.floor(r() * k)), lo, hi);
  const randRule = (r) => {
    const o = { card: pick(cards, r), max: 1 + Math.floor(r() * 3) };
    if (r() < 0.4) o.minDeck = Math.floor(r() * 20);
    if (r() < 0.4) o.minMoney = 2 + Math.floor(r() * 6);
    if (r() < 0.2) o.maxProv = 1 + Math.floor(r() * 8);
    return o;
  };
  const mutate = (t, r) => {
    const c = structuredClone(t);
    const n = 1 + Math.floor(r() * 3);
    for (let k = 0; k < n; k++) {
      const x = r(); const ru = c.rules.length ? pick(c.rules, r) : null;
      if (x < 0.15) c.duchyAt = step(c.duchyAt, r, 0, 8);
      else if (x < 0.25) c.estateAt = step(c.estateAt, r, 0, 5);
      else if (x < 0.4 && ru) ru.max = ru.max >= 99 ? 99 : step(ru.max, r, 1, 8);
      else if (x < 0.5 && ru) ru.minDeck = step(ru.minDeck || 0, r, 0, 30, 3);
      else if (x < 0.6 && ru) ru.minMoney = step(ru.minMoney || 0, r, 0, 8);
      else if (x < 0.65 && ru) { if (ru.maxProv == null) ru.maxProv = 1 + Math.floor(r() * 8); else if (r() < 0.3) delete ru.maxProv; else ru.maxProv = step(ru.maxProv, r, 1, 8); }
      else if (x < 0.75 && c.rules.length > 1) { const i = Math.floor(r() * c.rules.length); const j = clamp(i + (r() < 0.5 ? -1 : 1), 0, c.rules.length - 1); [c.rules[i], c.rules[j]] = [c.rules[j], c.rules[i]]; }
      else if (x < 0.9) c.rules.splice(Math.floor(r() * (c.rules.length + 1)), 0, randRule(r));
      else if (c.rules.length > 1) c.rules.splice(Math.floor(r() * c.rules.length), 1);
    }
    return c;
  };
  const cross = (a, b, r) => {
    const head = a.rules.slice(0, Math.floor(r() * (a.rules.length + 1)));
    const seen = new Set(head.map((x) => `${x.card}${x.max}`));
    const rules = [...head, ...b.rules.filter((x) => !seen.has(`${x.card}${x.max}`) || r() < 0.2)].map((x) => ({ ...x }));
    return { duchyAt: r() < 0.5 ? a.duchyAt : b.duchyAt, estateAt: r() < 0.5 ? a.estateAt : b.estateAt, rules };
  };

  // ---- 続きから ----
  const done = fs.readdirSync(out).map((f) => /^gen_(\d+)\.json$/.exec(f)).filter(Boolean).map((m) => Number(m[1])).sort((a, b) => b - a)[0];
  let gen = 0; let pop; let hof;
  if (done != null) {
    const j = JSON.parse(fs.readFileSync(`${out}/gen_${done}.json`, 'utf8'));
    gen = done + 1; pop = j.next; hof = j.hof;
    console.log(`gen_${done}.json から再開（次は gen ${gen}）`);
  } else {
    hof = Object.values(SEEDS).map((t) => structuredClone(t));
    const r = mulberry(seed0 * 7919);
    pop = hof.map((t) => structuredClone(t));
    while (pop.length < POP) pop.push(mutate(pick(hof, r), r));
  }
  if (gen >= GENS) { console.log(`もう gen ${gen} まで済み（--gens ${GENS}）`); return; }

  // ---- 子プロセスのプール ----
  const kids = Array.from({ length: procs }, () => fork(new URL(import.meta.url), ['--worker'], { execArgv: [] }));
  const waiting = new Map(); let nextId = 0; const idle = [...kids];
  const queue = [];
  const feed = (k) => { const t = queue.shift(); if (!t) { idle.push(k); return; } k.send(t.msg); waiting.set(t.msg.id, { t, k }); };
  for (const k of kids) k.on('message', (m) => { const w = waiting.get(m.id); waiting.delete(m.id); w.t.res(m); feed(w.k); });
  const run = (msg) => new Promise((res) => { const t = { msg: { ...msg, id: nextId++ }, res }; const k = idle.pop(); if (k) { k.send(t.msg); waiting.set(t.msg.id, { t, k }); } else queue.push(t); });

  for (; gen < GENS; gen++) {
    const t0 = Date.now();
    const opps = hof.slice(-OPPS);
    const res = await Promise.all(pop.map((table, i) => run({ table, opps, games: GAMES, seed: seed0 * 1000003 + gen * 1009 + i, preset })));
    const ranked = pop.map((table, i) => ({ table, score: res[i].pts / Math.max(1, res[i].n) })).sort((a, b) => b.score - a.score);
    const top = ranked.slice(0, 8);
    hof = [...hof, top[0].table].slice(-Math.max(OPPS, 8));
    // 次の集団: 上位 1/8 は残し、あとは上位半分から親を選ぶ（交叉 6 割・突然変異のみ 4 割。どちらも変異をかける）
    const r = mulberry(seed0 * 7919 + gen + 1);
    const half = ranked.slice(0, Math.max(2, POP >> 1)).map((x) => x.table);
    const next = ranked.slice(0, Math.max(1, POP >> 3)).map((x) => structuredClone(x.table));
    while (next.length < POP) next.push(mutate(r() < 0.6 ? cross(pick(half, r), pick(half, r), r) : pick(half, r), r));
    const sec = (Date.now() - t0) / 1000;
    fs.writeFileSync(`${out}/gen_${gen}.json.tmp`, JSON.stringify({ gen, seed: seed0, preset, opps: opps.length, games: GAMES, sec, top, hof, next }));
    fs.renameSync(`${out}/gen_${gen}.json.tmp`, `${out}/gen_${gen}.json`);
    const best = top[0];
    console.log(`gen ${gen}: ${sec.toFixed(1)} 秒、最高 ${best.score.toFixed(3)}、上位 8 の平均 ${(top.reduce((a, x) => a + x.score, 0) / top.length).toFixed(3)}、最高の表: ${best.table.rules.map((x) => `${x.card}×${x.max}`).join(' ')} 公領≤${best.table.duchyAt}`);
  }
  for (const k of kids) k.kill();
}
