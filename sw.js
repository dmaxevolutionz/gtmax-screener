const CACHE_NAME = 'screener-pwa-v1';

// Daftar file yang disimpan di cache untuk penggunaan offline
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './data.json',
  './manifest.json',
  './assets/favicon-32.png',
  './assets/favicon-64.png',
  './assets/icon-192.png',
  './assets/icon-512.png',
  './assets/splash.png'
];

// Phase Install: Menyimpan aset statis ke Cache Storage
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching app shell & assets');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Phase Activate: Membersihkan cache versi lama jika ada perubahan
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] Clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Phase Fetch: Strategi penanganan request data/aset
self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // Strategi "Network First" khusus data.json agar harga saham selalu paling update
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
          // Jika tidak ada koneksi/offline, gunakan data dari cache terakhir
          return caches.match(event.request);
        })
    );
    return;
  }

  // Strategi "Cache First" untuk aset statis (gambar, HTML, CSS, JS)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
