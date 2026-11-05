import { readdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
async function files(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  return (await Promise.all(entries.map(e => e.isDirectory() ? files(`${dir}/${e.name}`) : [`${dir}/${e.name}`]))).flat();
}
const paths = (await files('dist')).sort();
const hash = createHash('sha256');
for (const path of paths) { hash.update(path); hash.update(await readFile(path)); }
const name = `nomad-shell-${hash.digest('hex').slice(0, 16)}`;
const urls = paths.map(p => '/' + p.slice(5));
await writeFile('dist/sw.js', `// Generated from the complete static build. Never cache API responses or user saves.
const CACHE = ${JSON.stringify(name)};
const FILES = ${JSON.stringify(urls)};
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)));
});
self.addEventListener('message', event => {
  if (event.data === 'ACTIVATE_UPDATE') self.skipWaiting();
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith('nomad-shell-') && name !== CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return;
  if (event.request.mode === 'navigate') {
    event.respondWith(caches.open(CACHE).then(cache => cache.match('/index.html')).then(cached => cached || fetch(event.request)));
  } else if (FILES.includes(url.pathname)) {
    event.respondWith(caches.open(CACHE).then(cache => cache.match(url.pathname)).then(cached => cached || fetch(event.request)));
  }
});
`);
console.log(`Offline shell: ${urls.length} files, ${name}`);
