/* ================================================================
   sw.js — Service Worker de GATOSPIUPIU (v2)
   - Precachea el juego para que funcione sin conexión.
   - Archivos propios: RED PRIMERO (siempre ves la versión más nueva si hay
     conexión) y caché como respaldo sin conexión.
   - Fuentes de Google: caché en tiempo de ejecución.
   ► Cada vez que publiques cambios, sube el número de VERSION.
   ================================================================ */
const VERSION = 'gatospiupiu-v2';

const CORE = [
  './',
  './index.html',
  './style.css',
  './controls.js',
  './game.js',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './maskable-512.png',
  './apple-touch-icon.png',
  './favicon-32.png',
  './favicon.ico'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(VERSION)
      // cache:'reload' evita copias viejas del caché HTTP de GitHub Pages
      .then(cache => Promise.all(CORE.map(u => cache.add(new Request(u, { cache: 'reload' })).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

const cacheable = res => res && (res.ok || res.type === 'opaque');

function networkFirst(request, fallbackKey) {
  return fetch(request, { cache: 'no-cache' })
    .then(res => {
      if (cacheable(res)) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(fallbackKey || request, copy)); }
      return res;
    })
    .catch(() => caches.match(fallbackKey || request, { ignoreSearch: true }).then(hit => hit || Response.error()));
}

function staleWhileRevalidate(request) {
  return caches.open(VERSION).then(cache =>
    cache.match(request).then(hit => {
      const net = fetch(request)
        .then(res => { if (cacheable(res)) cache.put(request, res.clone()); return res; })
        .catch(() => hit);
      return hit || net;
    })
  );
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(staleWhileRevalidate(req));
    return;
  }
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req, './index.html'));
    return;
  }
  event.respondWith(networkFirst(req));
});
