'use strict';
// CPU の「狙いの札」を決める自己対局を、画面と別のスレッド（Web Worker）で回す。
// 画面（main.js）は { id, kingdom, landscapes, players, colony, level } を送り、{ id, plan, duchyAt } を受け取る。
// 同じ王国カード・ランドスケープで新しく対局を作って考えるので、今の対局の隠れた情報は使わない。
import './cards-base.js';
import './cards-intrigue.js';
import './cards-seaside.js';
import './cards-prosperity.js';
import './cards-hinterlands.js';
import './cards-guilds.js';
import './cards-alchemy.js';
import './cards-darkages.js';
import './cards-adventures.js';
import './cards-empires.js';
import './cards-nocturne.js';
import './cards-renaissance.js';
import './cards-menagerie.js';
import './cards-promo.js';
import './cards-allies.js';
import './cards-plunder.js';
import './cards-risingsun.js';
import { newGame } from './engine.js';
import { planFor } from './cpu.js';

self.onmessage = (e) => {
  const { id, kingdom, landscapes, players, colony, level } = e.data;
  let plan = [];
  try {
    const g = newGame(Math.max(2, players || 2), kingdom, null, { landscapes, colony });
    plan = planFor(g, 0, level);
  } catch { plan = []; }
  self.postMessage({ id, plan: [...plan], duchyAt: plan.duchyAt });
};
