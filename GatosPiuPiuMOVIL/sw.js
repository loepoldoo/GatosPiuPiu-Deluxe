/* ================================================================
   sw.js — Service Worker de GATOSPIUPIU
   - Precachea el juego para que funcione sin conexión.
   - Archivos propios: "stale-while-revalidate" (sirve rápido y se actualiza solo).
   - Navegación: red primero, caché como respaldo.
   - Fuentes de Google: caché en tiempo de ejecución.
   ► Cada vez que publiques cambios, sube el número de VERSION.
   ================================================================ */
const VERSION = 'gatospiupiu-v1';

const CORE = [
  './',
  './index.html',
  './style.css',
  './controls.js',
  './game.js',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/maskable-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(VERSION)
      .then(cache => cache.addAll(CORE))
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

// Devuelve lo que haya en caché al instante y refresca la copia en segundo plano
function staleWhileRevalidate(request) {
  return caches.open(VERSION).then(cache =>
    cache.match(request).then(hit => {
      const network = fetch(request)
        .then(res => { if (cacheable(res)) cache.put(request, res.clone()); return res; })
        .catch(() => hit);
      return hit || network;
    })
  );
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Fuentes de Google (otro origen)
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(staleWhileRevalidate(req));
    return;
  }
  if (url.origin !== self.location.origin) return;     // el resto de orígenes: red normal

  // Abrir la app: red primero (para ver actualizaciones), caché si no hay conexión
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(res => {
          if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put('./index.html', copy)); }
          return res;
        })
        .catch(() => caches.match('./index.html'))
    );
    return;
  }

  event.respondWith(staleWhileRevalidate(req));
});
