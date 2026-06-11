const CACHE_NAME = 'ipremium-dashboard-v1';
const ASSETS_TO_CACHE = [
    '/dashboard/',
    '/static/manifest.json',
];

// Install Event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
        .then(cache => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
        .catch(err => console.log('Cache error', err))
    );
});

// Fetch Event
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
