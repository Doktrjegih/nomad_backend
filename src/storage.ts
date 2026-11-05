import { ITEMS, view, type Game } from './engine';

export class SaveConflict extends Error {}
export interface Stored { token: string; game: Game }
const DB = 'nomad-offline';
const STORE = 'journeys';
const KEY = 'current';

/** Validate before using imported or persisted data. Unknown versions stay untouched. */
export function validateGame(value: unknown): Game {
  const fail = (): never => { throw new Error('This save is damaged or belongs to an unsupported version. Export it before starting again.'); };
  if (!value || typeof value !== 'object') return fail();
  const g = value as Game;
  const integer = (n: unknown, min = 0, max = Number.MAX_SAFE_INTEGER) => typeof n === 'number' && Number.isSafeInteger(n) && n >= min && n <= max;
  const object = (v: unknown) => v !== null && typeof v === 'object' && !Array.isArray(v);
  const validItem = (id: number) => ITEMS.some(i => i.id === id);
  const validQuest = (q: Game['quests'][number]) => object(q) && typeof q.order === 'string' && q.order.length < 100
    && integer(q.goal, 1, 100) && integer(q.current, 0, q.goal) && integer(q.reward, 0, 10000) && typeof q.plot === 'boolean' && typeof q.boss === 'boolean';
  const validPlace = (p: Game['place']) => object(p) && ['hometown', 'village', 'river', 'forest', 'mountains', 'cave'].includes(p.name)
    && ['peaceful', 'hostile'].includes(p.type) && ['enemies', 'tavern', 'chest', 'npc'].every(k => typeof p[k as keyof typeof p] === 'boolean');
  if (g.version !== 1 || typeof g.id !== 'string' || !g.id.length || g.id.length > 100 || !integer(g.revision)
    || !integer(g.rng, 0, 0xffffffff) || !object(g.player) || !object(g.menu) || !validPlace(g.place)
    || !['peace', 'battle', 'tavern', 'merchant', 'npc'].includes(g.scene)
    || !['playing', 'finished'].includes(g.status) || ![null, 'win', 'death', 'story-loss', 'exit'].includes(g.outcome)
    || !integer(g.withoutTavern) || !integer(g.biomeLeft, -1, 5)) return fail();
  const p = g.player;
  for (const key of ['health', 'max_hp', 'attack', 'defence', 'gold', 'drunk', 'endurance', 'strength', 'agility', 'luck',
    'plot_stage', 'aleg_drinks', 'moves', 'travel_moves', 'battles_won'] as const) {
    if (!integer(p[key], key === 'health' ? -10000 : 0, 1e9)) return fail();
  }
  if (p.drunk > 100 || p.max_hp < 1 || p.endurance < 1 || p.strength < 1 || p.agility < 1 || p.luck < 1 || p.plot_stage < 1 || p.plot_stage > 5
    || p.health > p.max_hp || (g.status === 'playing' && p.health <= 0)) return fail();
  if (!Array.isArray(g.inventory) || g.inventory.length > ITEMS.length || g.inventory.some(e => !object(e) || !validItem(e.id)
    || !integer(e.amount, 1, 10000) || typeof e.used !== 'boolean') || new Set(g.inventory.map(e => e.id)).size !== g.inventory.length) return fail();
  for (const type of ['weapon', 'armor']) if (g.inventory.filter(e => e.used && ITEMS.find(i => i.id === e.id)!.type === type).length > 1) return fail();
  if (!Array.isArray(g.quests) || g.quests.length > 4 || !g.quests.every(validQuest) || g.quests.filter(q => q.plot).length > 1
    || (g.npcOffer !== null && !validQuest(g.npcOffer))) return fail();
  if (g.tavern !== null && (!object(g.tavern) || ['merchant', 'aleg', 'quests'].some(k => typeof g.tavern![k as 'merchant'] !== 'boolean')
    || (g.tavern.offer !== null && !validQuest(g.tavern.offer)))) return fail();
  if (['merchant', 'tavern'].includes(g.scene) && !g.tavern) return fail();
  if (g.enemy !== null) {
    const e = g.enemy;
    if (!object(e) || typeof e.name !== 'string' || e.name.length > 100 || !integer(e.stage, 1, 4)
      || !integer(e.health, -10000, 10000) || !integer(e.max_hp, 1, 10000) || !integer(e.attack) || !integer(e.defence)
      || !integer(e.baseAttack) || !integer(e.bleeding, 0, 2) || !integer(e.heals, 0, 2) || typeof e.boss !== 'boolean' || typeof e.canRun !== 'boolean') return fail();
  }
  if (g.scene === 'battle' && !g.enemy) return fail();
  if (!Array.isArray(g.log) || g.log.length > 250 || g.log.some(l => typeof l !== 'string' || l.length > 10000)) return fail();
  const m = g.menu;
  switch (m.kind) {
    case 'main': case 'inventory': case 'exit': break;
    case 'buy': case 'sell': case 'buy-confirm': case 'sell-amount': case 'sell-confirm':
      if (g.scene !== 'merchant') return fail();
      if ('id' in m && (!validItem(m.id) || (m.kind !== 'buy-confirm' && !g.inventory.some(e => e.id === m.id)))) return fail();
      if (m.kind === 'sell-confirm' && !integer(m.amount, 1, g.inventory.find(e => e.id === m.id)!.amount)) return fail();
      break;
    case 'roads': if (!Array.isArray(m.places) || m.places.length !== 2 || !m.places.every(validPlace)) return fail(); break;
    case 'quest': if (!validQuest(m.quest) || !['plot', 'npc', 'tavern'].includes(m.source)) return fail(); break;
    case 'drink': case 'stats': if (g.scene !== 'tavern') return fail(); break;
    default: return fail();
  }
  view(g); // Every saved prompt must be renderable without advancing the game.
  return g;
}
function open(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE);
    request.onsuccess = () => { const db = request.result; db.onversionchange = () => db.close(); resolve(db); };
    request.onerror = () => reject(request.error ?? new Error('Browser storage is unavailable.'));
    request.onblocked = () => reject(new Error('Close other Nomad tabs to unlock saved games.'));
  });
}
export async function load(): Promise<Stored | null> {
  const db = await open();
  try {
    return await new Promise((resolve, reject) => {
      const request = db.transaction(STORE).objectStore(STORE).get(KEY);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        try {
          const stored = request.result as Stored | undefined;
          if (!stored) return resolve(null);
          if (typeof stored.token !== 'string') throw new Error('Invalid save record');
          resolve({ token: stored.token, game: validateGame(stored.game) });
        } catch (error) { reject(error); }
      };
    });
  } finally { db.close(); }
}
/** Read and compare in the same transaction, so two tabs cannot overwrite each other. */
export async function save(game: Game, expected: string | null, force = false): Promise<Stored> {
  validateGame(game);
  const db = await open(), token = crypto.randomUUID();
  try {
    return await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite'), store = tx.objectStore(STORE);
      let conflict = false;
      let writeError: unknown;
      const request = store.get(KEY);
      request.onsuccess = () => {
        if (!force && (request.result?.token ?? null) !== expected) { conflict = true; tx.abort(); return; }
        try { store.put({ token, game }, KEY); }
        catch (error) { writeError = error; tx.abort(); }
      };
      tx.oncomplete = () => resolve({ token, game });
      tx.onabort = () => reject(conflict ? new SaveConflict('Another tab changed this journey. The latest save has been restored.')
        : new Error(`Could not save this turn. ${writeError instanceof Error ? writeError.message : tx.error?.message ?? 'Browser storage is unavailable.'}`));
      tx.onerror = () => { /* onabort reports the transaction failure */ };
    });
  } finally { db.close(); }
}
export async function rawSave(): Promise<unknown> {
  const db = await open();
  try {
    return await new Promise((resolve, reject) => {
      const r = db.transaction(STORE).objectStore(STORE).get(KEY);
      r.onsuccess = () => resolve(r.result); r.onerror = () => reject(r.error);
    });
  } finally { db.close(); }
}
