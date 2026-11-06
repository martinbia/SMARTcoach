/* Increment the cache version whenever the app shell changes. */
const PREFIX = `smartcoach-shell:${new URL(self.registration.scope).pathname}:`;
const CACHE = `${PREFIX}v0.1.2`;
const SHELL = ['./', './index.html', './styles.css', './demo-data.js', './idle-image.js', './app.js',
  './manifest.webmanifest', './assets/icon.svg', './assets/icon-192.png', './assets/icon-512.png'];
const scopeURL = new URL(self.registration.scope);
self.addEventListener('install', event => {
  // Keep an existing app active until its tabs close; avoid mixing app versions.
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith(PREFIX) && name !== CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== scopeURL.origin || !url.pathname.startsWith(scopeURL.pathname)) return;
  if (event.request.mode === 'navigate') {
    // Only serve the PWA entry points; never mask missing documents or other pages.
    if (![scopeURL.pathname, `${scopeURL.pathname}index.html`].includes(url.pathname)) return;
    event.respondWith(caches.open(CACHE).then(cache => cache.match(new URL('./', scopeURL).href)));
    return;
  }
  // Cache only the explicit app shell, not local media, private content or arbitrary URLs.
  if (!SHELL.some(path => new URL(path, scopeURL).href === url.href)) return;
  event.respondWith(caches.open(CACHE).then(async cache => (await cache.match(event.request)) || fetch(event.request)));
});
