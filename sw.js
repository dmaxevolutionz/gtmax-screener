const CACHE_NAME = 'screener-saham-v1';

// Daftar file dan CDN yang digunakan oleh index.html
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  'https://cdn.tailwindcss.com',
  './assets/favicon-32.png',
  './assets/favicon-64.png',
  './assets/icon-192.png',
  './assets/icon-512.png',
  './assets/splash.png'
];

// Phase Install: Menyimpan shell aplikasi ke cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching app assets');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Phase Activate: Membersihkan cache versi lama jika ada pembaruan
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Phase Fetch: Penanganan request data & aset
self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // Strategi "Network First" untuk data.json agar selalu mengambil data saham terbaru
  if (requestUrl.pathname.endsWith('data.json')) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        })
        .catch(() => {
          // Jika offline, gunakan data.json dari cache terakhir
          return caches.match(event.request);
        })
    );
    return;
  }

  // Strategi "Cache First" untuk aset lainnya (HTML, CDN Tailwind, Ikon)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
