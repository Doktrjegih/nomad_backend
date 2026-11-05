import { test, expect, type Page } from '@playwright/test';
async function ready(page: Page) {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Enter tavern', exact: true })).toBeVisible();
  await expect(page.locator('#offline-status')).toContainText('Ready for offline play');
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller));
}
async function click(page: Page, name: string) { await page.getByRole('button', { name, exact: true }).click(); }

test('installs a complete static shell and plays, saves, reloads, and restarts entirely offline', async ({ page, context }) => {
  const apiRequests: string[] = [];
  page.on('request', r => { if (r.url().includes('/api/')) apiRequests.push(r.url()); });
  await ready(page);
  const manifest = await page.request.get('/manifest.webmanifest'); expect(manifest.ok()).toBe(true);
  expect((await manifest.json()).display).toBe('standalone');
  const cached = await page.evaluate(async () => {
    const keys = await caches.keys(); const cache = await caches.open(keys.find(k => k.startsWith('nomad-shell-'))!);
    return (await cache.keys()).map(r => new URL(r.url).pathname);
  });
  expect(cached).toContain('/index.html'); expect(cached.some(k => k.endsWith('.js'))).toBe(true);
  expect(cached).toContain('/icon-512.png');
  await context.setOffline(true);
  await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  await expect(page.locator('#gold')).toHaveText('5'); await expect(page.locator('#condition')).toContainText('10%');
  await click(page, 'Merchant'); await click(page, 'Buy');
  await page.getByRole('button', { name: /Broken Spear.*3 gold/ }).click();
  await expect(page.locator('#question')).toContainText('Buy Broken Spear');
  await page.reload(); await expect(page.locator('#question')).toContainText('Buy Broken Spear');
  await click(page, 'Yes'); await expect(page.locator('#gold')).toHaveText('2');
  await click(page, 'Cancel'); await click(page, 'Inventory');
  await expect(page.getByRole('button', { name: /Broken Spear.*×2/ })).toBeVisible();
  await click(page, 'Cancel'); await click(page, 'Exit game'); await click(page, 'No');
  await click(page, 'Exit game'); await click(page, 'Yes');
  await expect(page.locator('#mode')).toHaveText('Journey ended');
  await page.reload(); await expect(page.locator('#mode')).toHaveText('Journey ended');
  await click(page, 'Begin a new journey'); await expect(page.locator('#gold')).toHaveText('10');
  expect(apiRequests).toEqual([]);
});

test('exported saves can be imported offline without changing their prompt or inventory', async ({ page, context }) => {
  await ready(page); await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  const downloaded = page.waitForEvent('download'); await click(page, 'Export save');
  const download = await downloaded; const path = await download.path(); expect(path).toBeTruthy();
  await click(page, 'New journey'); await click(page, 'Start again'); await expect(page.locator('#gold')).toHaveText('10');
  await context.setOffline(true); page.once('dialog', d => d.accept());
  await page.locator('#save-file').setInputFiles(path!);
  await expect(page.locator('#gold')).toHaveText('5'); await expect(page.locator('#condition')).toContainText('10%');
});

test('another tab cannot overwrite a newer journey', async ({ page, context }) => {
  await ready(page); const other = await context.newPage(); await ready(other);
  await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  await expect(other.locator('#gold')).toHaveText('5');
  await click(other, 'Take a beer'); await expect(other.locator('#gold')).toHaveText('0');
  await page.reload(); await expect(page.locator('#gold')).toHaveText('0');
});

test('corrupt saves remain intact and can be exported until reset is explicitly confirmed', async ({ page }) => {
  await ready(page);
  await page.evaluate(async () => {
    await new Promise<void>((resolve, reject) => {
      const r = indexedDB.open('nomad-offline', 1);
      r.onsuccess = () => { const db = r.result, tx = db.transaction('journeys', 'readwrite'); tx.objectStore('journeys').put({ token: 'broken', game: { version: 999 } }, 'current'); tx.oncomplete = () => { db.close(); resolve(); }; tx.onerror = () => reject(tx.error); };
    });
  });
  await page.reload(); await expect(page.locator('#save-error')).toContainText('has not been overwritten');
  await expect(page.locator('#actions button')).toHaveCount(0);
  const downloaded = page.waitForEvent('download'); await click(page, 'Export save'); await downloaded;
  await click(page, 'New journey'); await click(page, 'Keep playing');
  await expect(page.locator('#save-error')).toBeVisible();
  await click(page, 'New journey'); await click(page, 'Start again');
  await expect(page.locator('#gold')).toHaveText('10'); await expect(page.locator('#save-error')).toBeHidden();
});

test('storage failures do not show an unsaved turn as successful', async ({ page }) => {
  await ready(page); await click(page, 'Enter tavern');
  await expect(page.getByRole('button', { name: 'Take a beer', exact: true })).toBeVisible();
  await page.evaluate(() => {
    const original = IDBObjectStore.prototype.put;
    IDBObjectStore.prototype.put = function (...args: Parameters<typeof original>) { throw new DOMException('Quota exceeded', 'QuotaExceededError'); };
  });
  await click(page, 'Take a beer');
  await expect(page.locator('#status')).toContainText('Could not save this turn');
  await expect(page.locator('#gold')).toHaveText('10');
});

test('mobile layout keeps choices within the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await ready(page);
  const width = await page.evaluate(() => ({ document: document.documentElement.scrollWidth, viewport: innerWidth }));
  expect(width.document).toBeLessThanOrEqual(width.viewport);
});

test('a stale tab restores the newest save when broadcast messages are unavailable', async ({ page, context }) => {
  await context.addInitScript(() => { Object.defineProperty(window, 'BroadcastChannel', { value: undefined }); });
  await ready(page); const other = await context.newPage(); await ready(other);
  await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  // Other tab still has the initial prompt and token.
  await click(other, 'Enter tavern');
  await expect(other.locator('#status')).toContainText('Another tab changed this journey');
  await expect(other.locator('#gold')).toHaveText('5');
  await other.reload(); await expect(other.locator('#gold')).toHaveText('5');
});

test('a service-worker update waits for consent and preserves the saved journey', async ({ page, context }) => {
  const { readFile, writeFile } = await import('node:fs/promises');
  const original = await readFile('dist/sw.js', 'utf8');
  try {
    await ready(page); await click(page, 'Enter tavern'); await click(page, 'Take a beer');
    await writeFile('dist/sw.js', original.replace(/nomad-shell-([a-f0-9]+)/, 'nomad-shell-$1-update-test'));
    await page.evaluate(async () => { await (await navigator.serviceWorker.getRegistration())!.update(); });
    await expect(page.locator('#update')).toBeVisible();
    await expect(page.locator('#gold')).toHaveText('5');
    await click(page, 'Update ready · Reload');
    await expect(page.locator('#gold')).toHaveText('5');
    await expect(page.locator('#update')).toBeHidden();
    await context.setOffline(true); await page.reload();
    await expect(page.locator('#gold')).toHaveText('5');
  } finally { await writeFile('dist/sw.js', original); }
});
