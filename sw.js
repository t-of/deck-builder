// オフライン用のサービスワーカー。
//
// 自分のファイルは network-first（つながっていれば常に最新、圏外なら保存しておいた版）。
// Google Fonts は変わらないので cache-first。
//
// 注意: キャッシュ（CacheStorage）は t-of.github.io のすべてのアプリで共有されている。
// 古いキャッシュを消すときは、必ず自分の PREFIX で始まるものだけを消す。
// keys.filter(k => k !== CACHE) のように書くと、ほかのアプリのキャッシュまで消してしまう。
// ブラウザの HTTP キャッシュを通さない（install は reload、fetch は no-cache）。古い main.js と新しい index.html が混ざって動かなくなるのを防ぐ。

const PREFIX = 'deck-builder-';
const VERSION = 'v19';
const CACHE = `${PREFIX}${VERSION}`;
const FONT_CACHE = `${PREFIX}fonts`;

const SHELL = [
  './',
  './index.html',
  './style.css',
  './main.js',
  './engine.js',
  './cpu.js',
  './planner.js',
  './cards-base.js',
  './cards-intrigue.js',
  './cards-seaside.js',
  './cards-prosperity.js',
  './cards-hinterlands.js',
  './cards-guilds.js',
  './cards-alchemy.js',
  './cards-darkages.js',
  './cards-adventures.js',
  './cards-empires.js',
  './cards-nocturne.js',
  './cards-renaissance.js',
  './cards-menagerie.js',
  './cards-promo.js',
  './cards-allies.js',
  './cards-plunder.js',
  './cards-risingsun.js',
  './pixel-cards.js',
  './manifest.webmanifest',
  './webapp-kit/webapp-kit.css',
  './webapp-kit/webapp-kit.js',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png',
  './art/copper.png',
  './art/silver.png',
  './art/gold.png',
  './art/estate.png',
  './art/duchy.png',
  './art/province.png',
  './art/warehouse.png',
  './art/moat.png',
  './art/moneylender.png',
  './art/village.png',
  './art/workshop.png',
  './art/mercenary.png',
  './art/remodel.png',
  './art/smithy.png',
  './art/market.png',
  './art/mine.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys
      .filter((k) => k.startsWith(PREFIX) && k !== CACHE && k !== FONT_CACHE)
      .map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    e.respondWith(networkFirst(req));
  } else if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(cacheFirst(req, FONT_CACHE));
  }
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(req, { cache: 'no-cache' });
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch {
    return (await cache.match(req, { ignoreSearch: true })) || (await cache.match('./index.html')) || Response.error();
  }
}

async function cacheFirst(req, name) {
  const cache = await caches.open(name);
  const hit = await cache.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok || res.type === 'opaque') cache.put(req, res.clone());
  return res;
}
