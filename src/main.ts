import { act, createGame, equipment, view, type Game } from './engine';
import { load, rawSave, save, SaveConflict, validateGame, type Stored } from './storage';

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
let current: Stored | null = null;
let busy = true;
let storageBroken = false;
const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('nomad-journey') : null;
const errorText = (e: unknown) => e instanceof Error ? e.message : 'Something went wrong.';
function message(text: string, error = false) { $('status').textContent = text; $('status').classList.toggle('error', error); }
function storageError(text: string) { $('save-error').hidden = !text; $('save-error').textContent = text; }
function setBusy(value: boolean) {
  busy = value;
  document.querySelectorAll<HTMLButtonElement>('#actions button,#new-game,#import,#update').forEach(b => b.disabled = value);
}
function render(g: Game) {
  const v = view(g), p = g.player;
  $('location').textContent = v.location[0].toUpperCase() + v.location.slice(1);
  $('mode').textContent = g.status === 'playing' ? (g.scene === 'battle' ? 'Battle' : 'Your turn') : 'Journey ended';
  $('question').textContent = v.question;
  const story = $('story'); story.replaceChildren();
  for (const line of g.log) { const row = document.createElement('p'); row.textContent = line; story.append(row); }
  story.scrollTop = story.scrollHeight;
  for (const key of ['attack', 'defence', 'gold', 'moves'] as const) $(key).textContent = String(p[key]);
  $('weapon').textContent = equipment(g, 'weapon')?.name ?? 'Unarmed';
  $('armor').textContent = equipment(g, 'armor')?.name ?? 'No armor';
  $('hp').textContent = `${Math.max(0, p.health)} / ${p.max_hp}`;
  const hp = $('hp-bar');
  hp.setAttribute('aria-valuemin', '0'); hp.setAttribute('aria-valuemax', String(p.max_hp)); hp.setAttribute('aria-valuenow', String(Math.max(0, p.health)));
  (hp.firstElementChild as HTMLElement).style.width = `${Math.max(0, Math.min(100, 100 * p.health / p.max_hp))}%`;
  $('condition').textContent = p.drunk ? `Alcohol level · ${p.drunk}%` : 'Sober & steady';
  $('progress').textContent = `Chapter ${p.plot_stage} · Move ${p.moves}`;
  const actions = $('actions'); actions.replaceChildren();
  for (const option of v.options) {
    const b = document.createElement('button'); b.className = 'action';
    b.textContent = option.label[0].toUpperCase() + option.label.slice(1);
    b.onclick = () => void takeTurn(option.id, g.revision); actions.append(b);
  }
  if (g.status !== 'playing') {
    const b = document.createElement('button'); b.className = 'action'; b.textContent = 'Begin a new journey';
    b.onclick = () => void newJourney(); actions.append(b);
  }
}
async function commit(game: Game, force = false) {
  // Display a turn only after its complete snapshot has been durably written.
  current = await save(game, current?.token ?? null, force);
  storageBroken = false; storageError('');
  render(current.game); message(''); $('save-status').textContent = 'Saved on this device.';
  channel?.postMessage('saved');
}
async function takeTurn(action: string, revision: number) {
  if (busy || !current) return;
  setBusy(true);
  try { await commit(act(current.game, action, revision)); }
  catch (e) {
    if (e instanceof SaveConflict) {
      try { current = await load(); if (current) render(current.game); }
      catch (loadError) { storageError(errorText(loadError)); }
    }
    message(errorText(e), true);
  } finally { setBusy(false); }
}
async function newJourney(force = false) {
  if (busy) return;
  setBusy(true);
  try { await commit(createGame(crypto.getRandomValues(new Uint32Array(1))[0], crypto.randomUUID()), force); }
  catch (e) { storageError(`Could not save a new journey. ${errorText(e)}`); }
  finally { setBusy(false); }
}
const restart = $('restart-dialog') as HTMLDialogElement;
$('new-game').onclick = () => {
  if (current?.game.status === 'playing' || storageBroken) restart.showModal(); else void newJourney();
};
$('cancel-restart').onclick = () => restart.close();
$('confirm-restart').onclick = () => { restart.close(); void newJourney(storageBroken); };
function download(value: unknown) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = 'nomad-save.json'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('export').onclick = async () => {
  try { const stored = await rawSave(); if (stored) download((stored as Stored).game ?? stored); else message('No saved journey yet.'); }
  catch (e) { if (current) download(current.game); else storageError(errorText(e)); }
};
$('import').onclick = () => ($('save-file') as HTMLInputElement).click();
$('save-file').onchange = async () => {
  const input = $('save-file') as HTMLInputElement, file = input.files?.[0]; input.value = '';
  if (!file || busy) return;
  try {
    if (file.size > 1_000_000) throw new Error('Save file is too large.');
    const game = validateGame(JSON.parse(await file.text()));
    if (!confirm('Replace the journey saved on this device with this imported save?')) return;
    setBusy(true); await commit(game, storageBroken);
  } catch (e) { message(`Import failed. ${errorText(e)}`, true); }
  finally { setBusy(false); }
};
channel && (channel.onmessage = async () => {
  if (busy) return; setBusy(true);
  try { const latest = await load(); if (latest && latest.token !== current?.token) { current = latest; render(latest.game); message('Journey updated from another tab.'); } }
  catch (e) { storageError(errorText(e)); }
  finally { setBusy(false); }
});

interface InstallPrompt extends Event { prompt(): Promise<void>; userChoice: Promise<{ outcome: string }> }
let installPrompt: InstallPrompt | null = null;
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event as InstallPrompt; $('install').hidden = false; });
$('install').onclick = async () => { if (installPrompt) { await installPrompt.prompt(); await installPrompt.userChoice; installPrompt = null; $('install').hidden = true; } };
window.addEventListener('appinstalled', () => { $('install').hidden = true; });
let offlineReady = false;
function connectionStatus() {
  $('offline-status').textContent = offlineReady ? `${navigator.onLine ? 'Ready for offline play' : 'Playing offline'} · Everything stays on this device.`
    : 'Offline files are not cached yet. Connect once to finish downloading the game.';
}
window.addEventListener('online', connectionStatus); window.addEventListener('offline', connectionStatus);
async function setupOffline() {
  if (!('serviceWorker' in navigator) || !import.meta.env.PROD) { $('offline-status').textContent = 'Local development · Offline caching is enabled in the production build.'; return; }
  try {
    const registration = await navigator.serviceWorker.register('/sw.js');
    await navigator.serviceWorker.ready; offlineReady = true; connectionStatus();
    function offerUpdate() {
      if (!registration.waiting || !navigator.serviceWorker.controller) return;
      $('update').hidden = false;
      $('update').onclick = () => {
        if (busy) return;
        registration.waiting?.postMessage('ACTIVATE_UPDATE');
        navigator.serviceWorker.addEventListener('controllerchange', () => location.reload(), { once: true });
      };
    }
    offerUpdate();
    registration.addEventListener('updatefound', () => registration.installing?.addEventListener('statechange', offerUpdate));
  } catch { connectionStatus(); }
}
async function boot() {
  try {
    current = await load();
    if (current) render(current.game);
    else {
      await commit(createGame(crypto.getRandomValues(new Uint32Array(1))[0], crypto.randomUUID()));
      try {
        if (localStorage.getItem('nomad-save')) message('A new offline journey has begun. Saves from the earlier online game cannot be imported.');
      } catch { /* Legacy storage is optional; the current save uses IndexedDB. */ }
    }
    void navigator.storage?.persist?.().catch(() => false);
  } catch (e) {
    storageBroken = true;
    $('question').textContent = 'Your saved journey could not be opened.';
    storageError(`${errorText(e)} Your existing save has not been overwritten. Export it, or use New journey to reset.`);
  } finally { setBusy(false); }
  void setupOffline();
}
void boot();
