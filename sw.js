/* Increment the cache version whenever the app shell changes. */
const PREFIX = `smartcoach-shell:${new URL(self.registration.scope).pathname}:`;
const CACHE = `${PREFIX}v0.5.3`;
const CONTENT = ['./content/genesungsweg.md', './content/berichte.md', './content/videos.md', './content/dialoge.md', './content/ansprache-dialoge.md'];
const SHELL = ['./', './index.html', './styles.css', './demo-data.js', './dashboard-data.js', './idle-image.js', './app.js', './content.js', './local-videos.js', './local-prompt-audio.js', './xray-media.js',
  './manifest.webmanifest', './assets/icon.svg', './assets/icon-192.png', './assets/icon-512.png',
  './assets/header-landscape.svg', './assets/profile-ernst.svg', './assets/profile-anna.svg'];
const scopeURL = new URL(self.registration.scope);
self.addEventListener('install', event => {
  // Activate only after the shell and matching Markdown are cached together.
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll([...SHELL, ...CONTENT])).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    const upgrading = names.some(name => name.startsWith(PREFIX) && name !== CACHE);
    await Promise.all(names.filter(name => name.startsWith(PREFIX) && name !== CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
    if (upgrading) {
      const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
      clients.filter(client => {
        const url = new URL(client.url);
        return url.origin === scopeURL.origin && url.pathname.startsWith(scopeURL.pathname);
      }).forEach(client => { void client.navigate(client.url).catch(() => null); });
    }
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== scopeURL.origin || !url.pathname.startsWith(scopeURL.pathname)) return;
  if (CONTENT.some(path => new URL(path, scopeURL).href === url.href)) {
    // Never mix Markdown from a new deployment with app code from an old one.
    event.respondWith(caches.open(CACHE).then(cache => cache.match(event.request).then(response => response || fetch(event.request))));
    return;
  }
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
