/**
 * SUZUME SERVICE WORKER
 * Enables offline support and PWA installation
 */

const CACHE_NAME = 'suzume-v2';
const ASSETS = [
  '.',
  'index.html',
  'css/style.css',
  'js/storage.js',
  'js/memory.js',
  'js/files.js',
  'js/chat.js',
  'js/app.js',
  'manifest.json'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(ASSETS).catch(err => {
          console.warn('SW cache addAll failed:', err);
          // Still activate even if caching fails
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip API and external requests
  const url = new URL(event.request.url);
  if (!url.origin.includes(self.location.origin) || 
      url.pathname.includes('chrome-extension')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Cache the fetched resource
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });

            return response;
          })
          .catch(() => {
            // If both cache and network fail, return a simple offline page
            if (event.request.mode === 'navigate') {
              return caches.match('index.html');
            }
            return new Response('Offline', { status: 503 });
          });
      })
  );
});
