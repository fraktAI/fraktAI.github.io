// Service worker: aplikacja działa też bez internetu (pokazuje ostatnio pobrane dane).
const VER = 'kruszyn-v1';
const SHELL = ['./', 'index.html', 'wies.json', 'favicon.svg', 'icon-192.png', 'manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VER).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VER).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// Dane i strona: najpierw internet (świeże), w razie braku – ostatnia zapisana kopia.
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;   // pogoda (Open-Meteo) ma własny zapas w aplikacji
  e.respondWith(
    fetch(r).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(VER).then(c => c.put(r, copy)); }
      return res;
    }).catch(() => caches.match(r, {ignoreSearch: true}).then(hit => hit || (r.mode === 'navigate' ? caches.match('index.html') : Response.error())))
  );
});
