import { test, expect, type Page } from '@playwright/test';
async function resize(page: Page, size: { width: number; height: number }) {
  await page.setViewportSize(size);
  // CSS updates immediately; wait for the resize handler to recalculate action
  // pages before testing whether the previous/next buttons are enabled.
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
}
async function ready(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Enter tavern', exact: true })).toBeVisible();
  await page.evaluate(() => navigator.serviceWorker.ready.then(() => undefined));
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller));
  await page.evaluate(() => document.fonts.ready.then(() => undefined));
}
async function click(page: Page, name: string) {
  await expect(page.locator('#open-menu')).toBeEnabled();
  const target = page.getByRole('button', { name, exact: true });
  if (await target.isVisible()) { await target.click(); return; }
  if (['New journey', 'Export save', 'Import save'].includes(name)) await page.getByRole('button', { name: 'Main menu', exact: true }).click();
  else if (await page.locator('#main-menu').isVisible()) await page.getByRole('button', { name: 'Continue', exact: true }).click();
  const previous = page.getByRole('button', { name: 'Previous choices', exact: true });
  while (await previous.isVisible() && await previous.isEnabled()) await previous.click();
  const next = page.getByRole('button', { name: 'More choices', exact: true });
  for (let n = 0; n < 50 && !(await target.isVisible()) && await next.isVisible() && await next.isEnabled(); n++) await next.click();
  await target.click();
}

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
  expect(cached).toContain('/art/icons.webp');
  expect(cached).toContain('/art/controls.webp');
  expect(cached).toContain('/art/locations.webp');
  expect(cached.some(path => path.endsWith('.woff2'))).toBe(true);
  await context.setOffline(true);
  await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  await expect(page.locator('#story .divider')).toHaveCount(1);
  await expect(page.locator('#offline-status')).toBeHidden();
  await expect(page.locator('#gold')).toHaveText('5'); await expect(page.locator('#condition')).toContainText('10%');
  await click(page, 'Merchant'); await click(page, 'Buy');
  await page.getByRole('button', { name: /Broken Spear.*3 gold/ }).click();
  await expect(page.locator('#question')).toContainText('Buy Broken Spear');
  await page.reload(); await click(page, 'Continue'); await expect(page.locator('#question')).toContainText('Buy Broken Spear');
  await expect(page.locator('#story .divider')).toHaveCount(1);
  await click(page, 'Yes'); await expect(page.locator('#gold')).toHaveText('2');
  await click(page, 'Cancel'); await click(page, 'Inventory');
  await expect(page.getByRole('button', { name: /Broken Spear.*×2/ })).toBeVisible();
  await click(page, 'Cancel'); await click(page, 'Exit game'); await click(page, 'No');
  await click(page, 'Exit game'); await click(page, 'Yes');
  await expect(page.locator('#question')).toHaveText('Your journey has ended.');
  await page.reload(); await click(page, 'Continue'); await expect(page.locator('#question')).toHaveText('Your journey has ended.');
  await click(page, 'Begin a new journey'); await expect(page.locator('#gold')).toHaveText('10');
  expect(apiRequests).toEqual([]);
});

test('exported saves can be imported offline without changing their prompt or inventory', async ({ page, context }) => {
  await ready(page); await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  const downloaded = page.waitForEvent('download'); await click(page, 'Export save');
  const download = await downloaded; const path = await download.path(); expect(path).toBeTruthy();
  await click(page, 'New journey'); await click(page, 'Start again'); await expect(page.locator('#game-screen')).toBeVisible(); await expect(page.locator('#gold')).toHaveText('10');
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
  await resize(page, { width: 390, height: 844 }); await ready(page);
  const width = await page.evaluate(() => ({ document: document.documentElement.scrollWidth, viewport: innerWidth }));
  expect(width.document).toBeLessThanOrEqual(width.viewport);
});

test('a stale tab restores the newest save when broadcast messages are unavailable', async ({ page, context }) => {
  await context.addInitScript(() => { Object.defineProperty(window, 'BroadcastChannel', { value: undefined }); });
  await ready(page); const other = await context.newPage(); await ready(other);
  await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  await expect(page.locator('#gold')).toHaveText('5');
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

async function importJourney(page: Page, game: unknown) {
  await click(page, 'Main menu');
  page.once('dialog', d => d.accept());
  await page.locator('#save-file').setInputFiles({ name: 'journey.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(game)) });
  await expect(page.locator('#game-screen')).toBeVisible();
}
async function fitsScreen(page: Page) {
  await expect.poll(() => page.evaluate(() => {
    const visible = (e: Element) => (e as HTMLElement).offsetParent !== null;
    const elements = [...document.querySelectorAll('#actions button,#common-actions button,#common-actions,#action-pager,#enemy-card,#story,#game-screen,.sheet,.app-header')].filter(visible);
    return elements.every(e => { const b = e.getBoundingClientRect(); return b.top >= 0 && b.left >= 0 && b.right <= innerWidth + 1 && b.bottom <= innerHeight + 1; })
      && document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight
      && document.querySelector('#story')!.scrollHeight <= document.querySelector('#story')!.clientHeight + 1;
  })).toBe(true);
}

test('main menu resumes the same journey and alcohol uses an accessible progress bar', async ({ page }) => {
  await page.goto('/'); await expect(page.locator('#main-menu')).toBeVisible();
  await expect(page.locator('.location-strip')).toBeHidden();
  await expect(page.locator('#progress,#mode')).toHaveCount(0);
  await click(page, 'Continue'); await click(page, 'Enter tavern'); await click(page, 'Take a beer');
  await expect(page.getByRole('progressbar', { name: 'Alcohol', exact: true })).toHaveAttribute('aria-valuenow', '10');
  await expect(page.locator('#alcohol-bar i')).toHaveCSS('width', /px$/);
  await click(page, 'Main menu'); await expect(page.locator('#game-screen')).toBeHidden();
  await click(page, 'Continue'); await expect(page.locator('#gold')).toHaveText('5');
  await expect(page.locator('#story')).not.toContainText("You're in the");
});

test('equipment and every enemy have cached icons; tavern and chest choices are highlighted', async ({ page, context }) => {
  const { createGame } = await import('../src/engine');
  await ready(page);
  await expect(page.getByRole('button', { name: 'Enter tavern', exact: true })).toHaveClass(/highlight/);
  await expect(page.locator('#weapon-icon svg')).toHaveAttribute('data-icon', 'item-3');
  await expect(page.locator('#weapon-icon image')).toHaveAttribute('href', '/art/icons.webp');
  const { ICON_TILES } = await import('../src/icons');
  for (const id of [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 95, 96, 97, 98, 99]) expect(ICON_TILES[`item-${id}`]).toBeGreaterThanOrEqual(0);
  for (const id of ['wanderer', 'bandit', 'knight', 'berserk', 'dog', 'hyena', 'wolf', 'werewolf', 'hunter', 'aleg', 'wisp', 'shade', 'specter', 'phantom']) expect(ICON_TILES[id]).toBeLessThan(36);
  const game = createGame(42, 'chest-test'); game.place.chest = true;
  await context.setOffline(true); await importJourney(page, game);
  await expect(page.getByRole('button', { name: 'Check a chest', exact: true })).toHaveClass(/highlight/);
  await click(page, 'Check a chest'); await expect(page.locator('#story')).toContainText("You've found");
});

test('battle, long history, inventory and merchant pages fit phone, desktop and landscape screens', async ({ page }) => {
  const { createGame, makeEnemy, ITEMS, addItem } = await import('../src/engine');
  await ready(page);
  const game = createGame(42, 'layout-test');
  game.log = Array.from({ length: 80 }, (_, i) => i % 4 === 0 ? '' : `Story ${i}: You cross the forest and discover an unfamiliar path through the mountains.`);
  for (const item of ITEMS) addItem(game, item.id, 3);
  game.scene = 'battle'; game.enemy = makeEnemy(game, 'Van Helsing', 3, true);
  await importJourney(page, game); await expect(page.locator('#enemy-name')).toHaveText('Van Helsing');
  await expect(page.locator('#enemy-icon svg')).toHaveAttribute('data-icon', 'hunter');
  for (const size of [{ width: 1366, height: 768 }, { width: 390, height: 844 }, { width: 320, height: 568 }, { width: 844, height: 390 }]) {
    await resize(page, size); await fitsScreen(page);
    await expect(page.locator('#story-pager')).toBeVisible();
    await click(page, 'Earlier story'); await fitsScreen(page);
    await click(page, 'Inventory'); await expect(page.locator('#question')).toContainText('Which item'); await fitsScreen(page);
    while (await page.locator('#next-actions').isEnabled()) { await click(page, 'More choices'); await fitsScreen(page); }
    await click(page, 'Cancel'); await fitsScreen(page);
  }
  await resize(page, { width: 390, height: 844 }); await fitsScreen(page);
  await page.screenshot({ path: '/tmp/nomad-battle.png' });
  await resize(page, { width: 1366, height: 768 });
  await fitsScreen(page); await page.screenshot({ path: '/tmp/nomad-rpg-desktop.png' });
  const shop = createGame(42, 'shop-layout'); shop.scene = 'merchant'; shop.tavern = { merchant: true, aleg: true, quests: true, offer: null };
  await importJourney(page, shop); await click(page, 'Buy'); await expect(page.locator('#question')).toContainText('What do you want to buy');
  for (const size of [{ width: 320, height: 568 }, { width: 844, height: 390 }, { width: 1366, height: 768 }]) {
    await resize(page, size); await fitsScreen(page);
    while (await page.locator('#next-actions').isEnabled()) { await click(page, 'More choices'); await fitsScreen(page); }
    await click(page, 'Previous choices');
  }
});

test('desktop separates unchanged status, log-only center and right-hand actions', async ({ page }) => {
  await resize(page, { width: 1366, height: 768 }); await ready(page);
  const status = (await page.locator('.sheet').boundingBox())!;
  const log = (await page.locator('.journey').boundingBox())!;
  const actions = (await page.locator('.action-panel').boundingBox())!;
  expect(status.x + status.width).toBeLessThan(log.x);
  expect(log.x + log.width).toBeLessThan(actions.x);
  expect(status.width).toBe(230);
  await expect(page.locator('.journey #actions,.journey #enemy-card,.journey #location')).toHaveCount(0);
  await expect(page.locator('.action-panel #actions')).toBeVisible();
  await expect(page.locator('.location-strip #location')).toHaveText('Hometown');
  await expect(page.locator('.brand')).toHaveCSS('font-family', /Cinzel/);
  await expect(page.locator('#story')).toHaveCSS('font-family', /Alegreya/);
  await expect(page.getByRole('button', { name: 'Enter tavern', exact: true })).toHaveCSS('background-image', /linear-gradient/);
  const context = (await page.locator('.context-panel').boundingBox())!;
  const common = (await page.locator('.common-panel').boundingBox())!;
  expect(context.y + context.height).toBeLessThan(common.y);
  await expect(page.locator('#common-actions button')).toHaveCount(3);
  await expect(page.locator('#actions button[aria-label="Get status"]')).toHaveCount(0);
  expect(await page.evaluate(() => [...document.querySelectorAll('button')].every(b => b.querySelector('.game-icon image')))).toBe(true);
  expect(await page.locator('.sheet').evaluate(e => getComputedStyle(e).backgroundColor)).toBe(await page.locator('.context-panel').evaluate(e => getComputedStyle(e).backgroundColor));
  await expect(page.locator('#actions .action').first()).toHaveCSS('font-size', '14px');
  await click(page, 'Inventory'); await expect(page.locator('#question')).toContainText('Which item');
  for (const button of await page.locator('#common-actions button').all()) await expect(button).toBeDisabled();
  await click(page, 'Cancel'); await click(page, 'Get status');
  await expect(page.locator('#story')).toContainText('Health:');
});

test('static blurred backgrounds follow all locations and indoor scenes without network access', async ({ page, context }) => {
  const { createGame } = await import('../src/engine');
  await ready(page); await context.setOffline(true);
  for (const [location, position] of [['hometown', '50% 100%'], ['village', '50% 100%'], ['forest', '50% 0%'], ['mountains', '100% 0%'], ['cave', '0% 100%'], ['river', '100% 100%']]) {
    const game = createGame(42, `background-${location}`); game.place.name = location;
    await importJourney(page, game);
    await expect(page.locator('body')).toHaveAttribute('data-location', location);
    expect((await page.evaluate(() => getComputedStyle(document.body, '::before').backgroundPosition)).replace(/0px/g, '0%')).toBe(position);
    expect(await page.evaluate(() => getComputedStyle(document.body, '::before').filter)).toContain('blur(3px)');
    expect(await page.evaluate(() => getComputedStyle(document.body, '::before').animationName)).toBe('none');
  }
  const indoor = createGame(42, 'indoor');
  await importJourney(page, indoor); await click(page, 'Enter tavern');
  await expect(page.locator('body')).toHaveAttribute('data-location', 'tavern');
  await click(page, 'Merchant'); await expect(page.locator('body')).toHaveAttribute('data-location', 'tavern');
  await expect(page.locator('#location')).toHaveText('Merchant');
});

test('log colors survive reload safely, battle frames clear on restart, and menu hides location', async ({ page }) => {
  const { createGame, makeEnemy } = await import('../src/engine');
  await resize(page, { width: 1366, height: 768 }); await ready(page);
  const game = createGame(42, 'colored-log');
  game.scene = 'battle'; game.enemy = makeEnemy(game, 'Wet dog', 1);
  game.log = ['Equipped Broken Spear and Leather armor. Wet dog attacks!', 'fire cold poison bleeding Rage healing Alcohol', '<img src=x onerror="alert(1)">'];
  await importJourney(page, game);
  for (const kind of ['weapon', 'armor', 'enemy', 'fire', 'cold', 'poison', 'bleeding', 'rage', 'healing', 'alcohol']) {
    await expect(page.locator(`#story .log-${kind}`).first()).toBeVisible();
  }
  const colors = await page.locator('#story span').evaluateAll(nodes => nodes.map(e => getComputedStyle(e).color));
  expect(new Set(colors).size).toBeGreaterThan(7);
  await expect(page.locator('#story img')).toHaveCount(0);
  await expect(page.locator('#story')).toContainText('<img src=x onerror="alert(1)">');
  const redBorder = await page.locator('.journey').evaluate(e => getComputedStyle(e).borderColor);
  await expect(page.locator('body')).toHaveAttribute('data-battle', 'true');
  await click(page, 'Main menu'); await expect(page.locator('.location-strip')).toBeHidden();
  await click(page, 'Continue'); await expect(page.locator('.location-strip')).toBeVisible();
  await page.reload(); await click(page, 'Continue');
  await expect(page.locator('#story .log-enemy')).toHaveText('Wet dog');
  await click(page, 'Main menu'); await click(page, 'New journey'); await click(page, 'Start again');
  await expect(page.locator('#main-menu')).toBeHidden(); await expect(page.locator('#game-screen')).toBeVisible();
  await expect(page.locator('#location')).toHaveText('Hometown'); await expect(page.locator('body')).toHaveAttribute('data-battle', 'false');
  expect(await page.locator('.journey').evaluate(e => getComputedStyle(e).borderColor)).not.toBe(redBorder);
  await expect(page.locator('#progress,#mode')).toHaveCount(0);
});
