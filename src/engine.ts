/** Browser-only rules. Every transition works on a snapshot; nothing uses I/O or replay. */
import itemData from '../jsons/items.json' with { type: 'json' };
import enemyData from '../jsons/enemies.json' with { type: 'json' };
import plots from '../jsons/plot_quests.json' with { type: 'json' };

export interface Effect { name: string; damage?: number; resist?: number }
export interface Item {
  id: number; name: string; type: string; cost: number; boss?: string; enemies?: string[];
  levels?: Record<string, { attack?: number; defence?: number; effects?: Effect[] }>;
}
export const ITEMS = itemData as Item[];
const byId = new Map(ITEMS.map(item => [item.id, item]));
export function item(id: number): Item {
  const result = byId.get(id);
  if (!result) throw new Error('Unknown item');
  return result;
}
export interface Player {
  health: number; max_hp: number; attack: number; defence: number; gold: number; drunk: number;
  endurance: number; strength: number; agility: number; luck: number; plot_stage: number;
  aleg_drinks: number; moves: number; travel_moves: number; battles_won: number;
}
export interface Entry { id: number; amount: number; used: boolean }
export interface Quest { order: string; goal: number; current: number; reward: number; plot: boolean; boss: boolean }
export interface Place { name: string; type: 'peaceful' | 'hostile'; enemies: boolean; tavern: boolean; chest: boolean; npc: boolean }
export interface Enemy {
  name: string; stage: number; health: number; max_hp: number; attack: number; defence: number;
  boss: boolean; canRun: boolean; baseAttack: number; bleeding: number; heals: number;
}
interface Tavern { merchant: boolean; aleg: boolean; quests: boolean; offer: Quest | null }
type Scene = 'peace' | 'battle' | 'tavern' | 'merchant' | 'npc';
type Menu = { kind: 'main' | 'inventory' | 'buy' | 'sell' | 'exit' | 'drink' | 'stats' }
  | { kind: 'roads'; places: Place[] }
  | { kind: 'buy-confirm'; id: number }
  | { kind: 'sell-amount'; id: number }
  | { kind: 'sell-confirm'; id: number; amount: number }
  | { kind: 'quest'; quest: Quest; source: 'tavern' | 'npc' | 'plot' };
export interface Game {
  version: 1; id: string; revision: number; rng: number; player: Player; inventory: Entry[];
  quests: Quest[]; place: Place; scene: Scene; enemy: Enemy | null; tavern: Tavern | null;
  withoutTavern: number; biomeLeft: number; npcOffer: Quest | null; menu: Menu;
  status: 'playing' | 'finished'; outcome: 'win' | 'death' | 'story-loss' | 'exit' | null;
  log: string[];
}
export interface Option { id: string; label: string }
export interface View { question: string; options: Option[]; location: string }
const names = [
  ['Homeless guy', 'Bandit', 'Knight', 'Berserk'],
  ['Wet dog', 'Hyena', 'Wolf', 'Werewolf'],
  ['test1', 'test2', 'test3', 'test4'],
];
export const ENEMY_NAMES = [...names.flat(), 'Van Helsing', 'Aleg'];
const clamp = (n: number, low: number, high: number) => Math.max(low, Math.min(high, n));
// Python's round uses ties-to-even; keep combat/economy rounding consistent.
export function round(n: number): number {
  const floor = Math.floor(n);
  return n - floor === 0.5 ? (floor % 2 === 0 ? floor : floor + 1) : Math.round(n);
}
function random(g: Game): number {
  // Mulberry32: the current cursor is saved, so restoration never replays turns.
  g.rng = (g.rng + 0x6D2B79F5) >>> 0;
  let t = g.rng;
  t = Math.imul(t ^ t >>> 15, t | 1);
  t ^= t + Math.imul(t ^ t >>> 7, t | 61);
  return ((t ^ t >>> 14) >>> 0) / 4294967296;
}
const int = (g: Game, low: number, high: number) => low + Math.floor(random(g) * (high - low + 1));
const pick = <T>(g: Game, values: readonly T[]): T => values[int(g, 0, values.length - 1)];
function say(g: Game, ...lines: string[]) { g.log.push(...lines); g.log = g.log.slice(-250); }
export function equipment(g: Game, type: 'weapon' | 'armor'): Item | undefined {
  const entry = g.inventory.find(e => e.used && item(e.id).type === type);
  return entry ? item(entry.id) : undefined;
}
export function level(g: Game, value: Item) { return value.levels?.[String(Math.min(3, Math.floor(g.player.drunk / 25)))]; }
export function describe(g: Game, value: Item): string {
  const stats = level(g, value);
  if (!stats) return value.name;
  return `${value.name} (${value.type === 'weapon' ? `attack ${stats.attack}` : `defence ${stats.defence}`})`
    + (stats.effects ?? []).map(e => ` [+${e.damage ?? e.resist} ${e.name} ${e.damage ? 'damage' : 'resist'}]`).join('');
}
export function recount(g: Game) {
  const p = g.player;
  p.max_hp = 80 + p.endurance * 20;
  p.health = Math.min(p.health, p.max_hp);
  const weapon = equipment(g, 'weapon'), armor = equipment(g, 'armor');
  p.attack = 10 + (p.strength - 1) * 2 + Math.floor(p.drunk / 25) + (weapon ? level(g, weapon)?.attack ?? 0 : 0);
  p.defence = 10 + (p.agility - 1) * 2 + (armor ? level(g, armor)?.defence ?? 0 : 0);
}
function drink(g: Game, amount: number) { g.player.drunk = clamp(g.player.drunk + amount, 0, 100); recount(g); }
export function addItem(g: Game, id: number, amount = 1) {
  const entry = g.inventory.find(e => e.id === id);
  if (entry) entry.amount += amount;
  else g.inventory.push({ id, amount, used: false });
  g.inventory.sort((a, b) => a.id - b.id);
}
function removeItem(g: Game, id: number, amount = 1) {
  const entry = g.inventory.find(e => e.id === id);
  if (!entry || entry.amount < amount) throw new Error('Item is no longer available');
  entry.amount -= amount;
  if (entry.amount === 0) g.inventory = g.inventory.filter(e => e !== entry);
}
export function createGame(seed: number, id: string): Game {
  const g: Game = {
    version: 1, id, revision: 0, rng: seed >>> 0,
    player: { health: 100, max_hp: 100, attack: 10, defence: 10, gold: 10, drunk: 0,
      endurance: 1, strength: 1, agility: 1, luck: 1, plot_stage: 1, aleg_drinks: 0,
      moves: 0, travel_moves: 0, battles_won: 0 },
    inventory: [{ id: 3, amount: 1, used: true }, { id: 5, amount: 1, used: true }],
    quests: [], place: { name: 'hometown', type: 'peaceful', enemies: false, tavern: true, chest: false, npc: false },
    scene: 'peace', enemy: null, tavern: null, withoutTavern: 0, biomeLeft: 1, npcOffer: null,
    menu: { kind: 'main' }, status: 'playing', outcome: null, log: ['Hello, a big new world!'],
  };
  recount(g);
  return g;
}
const option = (id: string, label = id): Option => ({ id, label });
const yesNo = [option('yes', 'Yes'), option('no', 'No')];
const cancel = option('cancel', 'Cancel');
function mainOptions(g: Game): Option[] {
  let actions: string[];
  switch (g.scene) {
    case 'battle': actions = ['attack', ...(g.enemy?.canRun ? ['run away'] : [])]; break;
    case 'tavern': actions = ['go out', 'take a beer', 'take a steak', ...(g.tavern?.aleg ? ['talk with Aleg'] : []),
      ...(g.tavern?.merchant ? ['merchant'] : []), 'check quests']; break;
    case 'merchant': actions = ['back to tavern', 'buy', 'sell']; break;
    default: actions = ['go forward', ...(g.place.tavern ? ['enter tavern'] : []),
      ...(g.place.chest ? ['check a chest'] : []), ...(g.scene === 'npc' && g.npcOffer ? ['talk with Carl'] : [])];
  }
  return [...actions, 'inventory', 'get status', 'exit game'].map(a => option(a));
}
function inventoryOptions(g: Game, sell = false): Option[] {
  return g.inventory.filter(e => !sell || !['food', 'alcohol'].includes(item(e.id).type)).map(e =>
    option(String(e.id), `${describe(g, item(e.id))} ×${e.amount}${e.used ? ' · equipped' : ''}`));
}
export function view(g: Game): View {
  const location = g.scene === 'tavern' ? 'The tavern' : g.scene === 'merchant' ? 'Merchant' : g.place.name;
  const result = (question: string, options: Option[]): View => ({ question, options, location });
  if (g.status === 'finished') return result('Your journey has ended.', []);
  const m = g.menu;
  switch (m.kind) {
    case 'main': return result(g.scene === 'battle'
      ? `${g.enemy!.name} · ${g.enemy!.health} / ${g.enemy!.max_hp} HP` : 'What do you want to do?', mainOptions(g));
    case 'inventory': return result('Which item do you want to use?', [...inventoryOptions(g), cancel]);
    case 'roads': return result('Where do you want to go?', [...m.places.map((p, i) => option(String(i), p.name)), cancel]);
    case 'exit': return result('Do you want to exit?', yesNo);
    case 'buy': return result(`What do you want to buy? You have ${g.player.gold} gold coins.`,
      [...ITEMS.filter(i => ['weapon', 'armor'].includes(i.type) && !i.boss).map(i => option(String(i.id), `${describe(g, i)} · ${i.cost} gold`)), cancel]);
    case 'buy-confirm': return result(`Buy ${item(m.id).name} for ${item(m.id).cost} gold coins?`, yesNo);
    case 'sell': return result('Which item do you want to sell?', [...inventoryOptions(g, true), cancel]);
    case 'sell-amount': {
      const amount = g.inventory.find(e => e.id === m.id)!.amount;
      return result(`How many ${item(m.id).name} do you want to sell?`,
        [...Array.from({ length: amount }, (_, i) => option(String(i + 1))), cancel]);
    }
    case 'sell-confirm': return result(`Sell ${m.amount} ${item(m.id).name} for ${round(item(m.id).cost / 2) * m.amount} gold coins?`, yesNo);
    case 'quest': return result(`Accept: defeat ${m.quest.goal} ${m.quest.order}${m.quest.plot ? ' (story quest)' : ` · ${m.quest.reward} gold`}?`, yesNo);
    case 'drink': return result('Wanna drink with me?', yesNo);
    case 'stats': return result('What do you want to drink?', [option('endurance', 'Beer (endurance)'), option('strength', 'Vodka (strength)'),
      option('agility', 'Whiskey (agility)'), option('luck', 'Rum (luck)'), cancel]);
  }
}
function makePlace(g: Game, type?: Place['type'], name?: string): Place {
  type ??= pick(g, ['peaceful', 'hostile'] as const);
  const p: Place = { name: name ?? pick(g, type === 'hostile' ? ['mountains', 'forest', 'cave'] : ['village', 'river']),
    type, enemies: false, tavern: false, chest: false, npc: false };
  if (type === 'hostile') p.enemies = int(g, 1, 100) > 50;
  else {
    if (g.withoutTavern > 8) p.tavern = int(g, 1, 100) > 90;
    if (!p.tavern) p.npc = int(g, 1, 100) > 90;
  }
  if (!p.tavern && !p.enemies) p.chest = int(g, 1, 100) + g.player.luck * 2 > 95;
  return p;
}
export function makeEnemy(g: Game, name: string, stage: number, boss = false): Enemy {
  const hp = round((32 + 8 * (stage - 1)) * (0.9 + random(g) * 0.2));
  const attack = [7, 9, 12, 15][stage - 1] + int(g, -1, 1);
  const defence = [4, 6, 9, 12][stage - 1] + int(g, -1, 1);
  const e = { name, stage, health: boss ? round(hp * 1.5) : hp, max_hp: 0,
    attack: boss ? round(attack * 1.25) : attack, defence: boss ? round(defence * 1.25) : defence,
    boss, canRun: true, baseAttack: 0, bleeding: 0, heals: 2 };
  e.max_hp = e.health; e.baseAttack = e.attack;
  return e;
}
function generateEnemy(g: Game): Enemy {
  const quest = g.quests.find(q => q.plot && q.current < q.goal);
  const stage = Math.min(4, g.player.plot_stage);
  const allowed = g.place.name === 'forest' ? names[1] : g.place.name === 'mountains' ? [...names[0], ...names[2]] : [...names[0], ...names[1]];
  // Match the Python encounter selection: reroll biome-incompatible regular
  // enemies, while an active story target can appear in any hostile biome.
  for (;;) {
    const enemy = quest && random(g) < 0.5 ? makeEnemy(g, quest.order, stage, quest.boss)
      : makeEnemy(g, pick(g, names)[stage - 1], stage);
    if (allowed.includes(enemy.name) || enemy.boss || enemy.name === quest?.order) return enemy;
  }
}
function enterPlace(g: Game, place: Place) {
  g.place = place;
  g.player.moves++; g.player.travel_moves++;
  if (g.withoutTavern >= 8) {
    g.place = { name: 'village', type: 'peaceful', enemies: false, tavern: true, chest: false, npc: false };
    say(g, 'A safe tavern appears beside the road.');
  }
  if (g.place.tavern) { g.tavern = null; g.withoutTavern = 1; }
  else g.withoutTavern++;
  g.npcOffer = null; g.enemy = null; g.scene = 'peace';
  say(g, `You're in the location "${g.place.name}" (${g.place.type})`);
  if (g.place.enemies) {
    g.enemy = generateEnemy(g); g.scene = 'battle';
    say(g, `Your enemy is: ${g.enemy.name}`);
  } else if (g.place.npc) {
    g.scene = 'npc'; say(g, "You've met Carl.");
    if (g.quests.filter(q => !q.plot).length < 3) {
      if (g.player.drunk > 24 && int(g, 1, 100) > 20) {
        const stage = g.player.drunk <= 50 ? 2 : g.player.drunk <= 75 ? 3 : 4;
        g.npcOffer = sideQuest(g, stage);
        if (g.npcOffer) g.menu = { kind: 'quest', quest: g.npcOffer, source: 'npc' };
      } else if (g.player.drunk < 25 && int(g, 1, 100) > 60) {
        addItem(g, 1); say(g, 'I see you need a drink, take it.', "You've gotten Beer bottle"); g.scene = 'peace';
      }
    }
  } else if (!g.place.chest && !g.place.tavern) {
    say(g, 'Nothing interesting so far.');
  }
}
function sideQuest(g: Game, stage = 1): Quest | null {
  const candidates = names.map(group => group[stage - 1]).filter(name => !g.quests.some(q => !q.plot && q.order === name));
  if (!candidates.length) return null;
  const order = pick(g, candidates), goal = int(g, 2, 5);
  return { order, goal, current: 0, reward: goal * 5 + int(g, 2, 10), plot: false, boss: false };
}
function offerPlot(g: Game) {
  const plot = plots.find(p => p.id === g.player.plot_stage);
  if (!plot) { say(g, 'All plot quests are complete!'); return; }
  if (g.player.drunk < plot.needed_drunk) { say(g, "Sorry, not sure if you're ready for this now."); return; }
  const q: Quest = { order: plot.target === 'Some shit' ? 'Aleg' : plot.target, goal: plot.amount, current: 0, reward: 0, plot: true, boss: !!plot.boss };
  say(g, plot.description, `You need to defeat ${q.order} ${q.goal} time${q.goal === 1 ? '' : 's'}.`);
  g.menu = { kind: 'quest', quest: q, source: 'plot' };
}
function talkAleg(g: Game) {
  const q = g.quests.find(q => q.plot);
  say(g, "You're sitting across from Aleg.");
  if (q) {
    if (q.current < q.goal) { say(g, "Come back when you've finished."); return; }
    g.quests = g.quests.filter(other => other !== q);
    g.player.plot_stage++; g.player.health = g.player.max_hp;
    say(g, "Oh, nice work! I see you've done well. Your health is restored.");
    g.menu = { kind: 'drink' };
  } else offerPlot(g);
}
function finish(g: Game, outcome: Game['outcome'], ...lines: string[]) {
  say(g, ...lines); g.status = 'finished'; g.outcome = outcome; g.menu = { kind: 'main' };
}
function finishBattle(g: Game, ran = false) {
  g.enemy = null; g.scene = 'peace';
  if (!ran) {
    g.player.battles_won++;
    if (g.player.battles_won === 2) { addItem(g, 99); say(g, 'You earned an Iron sword!'); }
    if (g.player.battles_won === 4) { addItem(g, 95); say(g, 'You earned Leather armor!'); }
  }
  drink(g, ran ? -1 : -3);
}
function victory(g: Game) {
  const e = g.enemy!;
  if (e.boss && e.name === 'Aleg') { finish(g, 'win', 'You defeated Aleg!', 'Everyone is happy! You win! :)'); return; }
  say(g, `${e.name} was killed!`);
  const gold = int(g, 8, 12); g.player.gold += gold; say(g, `You get ${gold} gold coins`);
  if (e.stage > 2 && int(g, 1, 100) > 70) {
    const gear = pick(g, ITEMS.filter(i => ['weapon', 'armor'].includes(i.type) && !i.boss));
    addItem(g, gear.id); say(g, `You get ${gear.name}`);
  }
  const loot = ITEMS.filter(i => i.enemies?.includes(e.name));
  if (loot.length && int(g, 1, 100) > 30) {
    const drop = pick(g, loot), roll = int(g, 1, 100), amount = roll > 90 ? 3 : roll > 70 ? 2 : 1;
    addItem(g, drop.id, amount); say(g, `You get ${drop.name} (${amount})`);
  }
  if (e.boss) {
    const reward = ITEMS.find(i => i.boss === e.name);
    if (reward) { addItem(g, reward.id); say(g, `You get ${reward.name}!`); }
  }
  for (const q of g.quests) if (q.order === e.name && q.current < q.goal) {
    q.current++;
    if (q.current === q.goal) say(g, "You've finished the quest conditions!", 'You can get a reward in any tavern.');
  }
  finishBattle(g);
}
function enemyTurn(g: Game) {
  const e = g.enemy!, p = g.player;
  if (['Hyena', 'Van Helsing'].includes(e.name)) {
    e.attack = e.baseAttack;
    if (e.health < e.max_hp * 0.25) { e.attack = round(e.baseAttack * 1.5); say(g, `Rage! Enemy attack is ${e.attack}.`); }
  }
  if (['Wolf', 'Van Helsing'].includes(e.name)) {
    if (!e.bleeding) { if (int(g, 1, 100) > 70) { e.bleeding = 2; say(g, 'You are bleeding!'); } }
    else { p.health -= 2; e.bleeding--; say(g, 'You lost 2 HP due to bleeding.'); }
  }
  if (['Werewolf', 'Van Helsing'].includes(e.name) && e.health < e.max_hp * 0.25 && e.heals > 0) {
    e.health += 5; e.heals--; say(g, `Enemy heals! Health is ${e.health}.`);
  }
  const data = enemyData.find(d => d.name === e.name);
  const armor = equipment(g, 'armor');
  const effects = armor ? level(g, armor)?.effects ?? [] : [];
  let damage = round(e.attack * 10 / (10 + p.defence));
  for (const effect of data?.effects_damage ?? []) {
    const resist = effects.filter(a => a.name === effect.name).reduce((n, a) => n + (a.resist ?? 0), 0);
    const extra = Math.max(0, effect.value - resist);
    damage += extra;
    if (extra) say(g, `You get ${extra} damage from ${effect.name}.`);
  }
  damage = Math.max(1, damage); p.health -= damage; recount(g);
  say(g, `${e.name} attacks! You lose ${damage} HP.`);
  if (p.health <= 0) {
    if (e.boss && e.name === 'Aleg') finish(g, 'story-loss', 'You have been defeated by Aleg.',
      p.aleg_drinks >= 4 ? 'Your soul has been absorbed by Aleg.' : 'Everyone is sad! You lose! :(');
    else finish(g, 'death', 'Your HP is 0. GAME OVER!');
  }
}
function attack(g: Game) {
  const p = g.player, e = g.enemy!;
  p.moves++;
  if (int(g, 1, 100) > clamp(88 + 2 * p.luck - 0.1 * p.drunk, 75, 95)) {
    say(g, "You've missed!"); enemyTurn(g); return;
  }
  let damage = Math.max(1, round(p.attack * 10 / (10 + e.defence)));
  if (int(g, 1, 100) < p.luck * p.drunk / 100) { damage *= 2; say(g, 'CRITICAL HIT!'); }
  const weapon = equipment(g, 'weapon');
  const data = enemyData.find(d => d.name === e.name);
  for (const effect of (weapon ? level(g, weapon)?.effects : []) ?? []) {
    let extra = effect.damage ?? 0;
    if (data?.vulnerabilities?.includes(effect.name)) extra *= 2;
    if (data?.resist?.includes(effect.name)) extra = round(extra * 0.5);
    damage += extra;
    if (extra) say(g, `Your weapon deals ${extra} ${effect.name} damage.`);
  }
  e.health -= damage; say(g, `You deal ${damage} damage to ${e.name}.`);
  if (e.health <= 0) victory(g); else enemyTurn(g);
}
function chest(g: Game) {
  const candidates = ITEMS.filter(i => !i.boss && i.type !== 'loot');
  const weights = candidates.map(i => ((g.inventory.some(e => e.id === i.id) ? 0.1 : 1) / Math.sqrt(Math.max(1, i.cost))) ** (1 / g.player.luck));
  let roll = random(g) * weights.reduce((a, b) => a + b, 0), chosen = candidates[candidates.length - 1];
  for (let i = 0; i < candidates.length; i++) { roll -= weights[i]; if (roll <= 0) { chosen = candidates[i]; break; } }
  addItem(g, chosen.id); const gold = int(g, 1, 5); g.player.gold += gold;
  say(g, `You've found ${chosen.name}`, `You've found ${gold} gold coins`); g.place.chest = false;
}
function useItem(g: Game, id: number) {
  const entry = g.inventory.find(e => e.id === id)!, value = item(id), p = g.player;
  switch (value.type) {
    case 'food': p.moves++; p.health += 20; drink(g, -2); removeItem(g, id); say(g, `Your HP is ${p.health} now`); break;
    case 'alcohol': p.moves++; drink(g, 10); removeItem(g, id); say(g, `You've drunk ${value.name}`); break;
    case 'weapon': case 'armor': {
      const equip = !entry.used;
      for (const other of g.inventory) if (item(other.id).type === value.type) other.used = false;
      entry.used = equip; say(g, `${equip ? 'Equipped' : 'Removed'} ${value.name}`); break;
    }
    default: say(g, `You can't use ${value.name}, but you can sell it at a merchant.`);
  }
  recount(g);
}
function mainAction(g: Game, action: string) {
  switch (action) {
    case 'go forward':
      g.biomeLeft--;
      if (g.biomeLeft > 0) enterPlace(g, makePlace(g, g.place.type, g.place.name));
      else {
        const first = makePlace(g);
        let second = makePlace(g);
        while (second.name === first.name) second = makePlace(g);
        g.menu = { kind: 'roads', places: [first, second] };
      }
      break;
    case 'enter tavern':
      g.scene = 'tavern';
      g.tavern ??= { merchant: g.place.name === 'hometown' || random(g) < 0.5,
        quests: g.place.name === 'hometown' || random(g) < 0.5,
        aleg: g.place.name === 'hometown' || g.quests.some(q => q.plot && q.current >= q.goal) || int(g, 1, 100) > 66, offer: null };
      say(g, "You're in the tavern"); break;
    case 'go out': g.scene = 'peace'; say(g, `You're in the location "${g.place.name}" (${g.place.type})`); break;
    case 'merchant': g.scene = 'merchant'; say(g, "You're in the merchant shop"); break;
    case 'back to tavern': g.scene = 'tavern'; break;
    case 'take a beer': case 'take a steak':
      if (g.player.gold < 5) { say(g, "Not enough money, it's 5 gold coins."); break; }
      g.player.gold -= 5; g.player.moves++;
      if (action === 'take a steak') { g.player.health += 20; drink(g, -2); say(g, `Your HP is ${g.player.health} now`); }
      else { drink(g, 10); say(g, 'You drink a beer.'); }
      break;
    case 'inventory': g.menu = { kind: 'inventory' }; break;
    case 'get status': {
      const p = g.player;
      say(g, `Health: ${p.health}/${p.max_hp} · Gold coins: ${p.gold} · Alcohol: ${p.drunk}%`,
        `Endurance: ${p.endurance} · Strength: ${p.strength} · Agility: ${p.agility} · Luck: ${p.luck}`,
        'Active quests:', ...(g.quests.length ? g.quests.map(q => `${q.order}: ${q.current}/${q.goal}${q.plot ? ' [Plot quest]' : ''}`) : ['[Empty list]']));
      break;
    }
    case 'exit game': g.menu = { kind: 'exit' }; break;
    case 'check a chest': chest(g); break;
    case 'attack': attack(g); break;
    case 'run away':
      g.player.moves++;
      if (int(g, 1, 100) < 40 + g.player.luck * 10 - g.player.drunk * 0.5) { say(g, 'You have run away.'); finishBattle(g, true); }
      else { say(g, "You couldn't run away."); g.enemy!.canRun = false; enemyTurn(g); }
      break;
    case 'buy': g.menu = { kind: 'buy' }; break;
    case 'sell': g.menu = { kind: 'sell' }; break;
    case 'talk with Aleg': talkAleg(g); break;
    case 'talk with Carl': if (g.npcOffer) g.menu = { kind: 'quest', quest: g.npcOffer, source: 'npc' }; break;
    case 'check quests': {
      for (const q of [...g.quests]) if (!q.plot && q.current >= q.goal) {
        g.player.gold += q.reward; addItem(g, 1); g.quests = g.quests.filter(other => other !== q);
        say(g, `Thanks! Your reward is: ${q.reward} gold coins and a beer bottle.`);
      }
      if (g.quests.filter(q => !q.plot).length >= 3 || !g.tavern!.quests) { say(g, "Sorry, I don't have quests for you now."); break; }
      g.tavern!.offer ??= sideQuest(g);
      if (g.tavern!.offer) g.menu = { kind: 'quest', quest: g.tavern!.offer, source: 'tavern' };
      break;
    }
  }
}
/** Reject stale/unknown input and leave the original snapshot untouched. */
export function act(previous: Game, action: string, revision = previous.revision): Game {
  if (revision !== previous.revision || !view(previous).options.some(o => o.id === action)) throw new Error('Invalid or stale action');
  const g = structuredClone(previous), m = g.menu;
  g.revision++;
  g.log.push(''); // Persist turn boundaries alongside narrative, including across reloads.
  g.menu = { kind: 'main' };
  switch (m.kind) {
    case 'main': mainAction(g, action); break;
    case 'inventory': if (action !== 'cancel') useItem(g, Number(action)); break;
    case 'roads':
      if (action !== 'cancel') {
        drink(g, -1); g.biomeLeft = int(g, 2, 5); enterPlace(g, m.places[Number(action)]);
      } else g.biomeLeft = 1;
      break;
    case 'exit': if (action === 'yes') finish(g, 'exit', 'Your journey has ended.'); break;
    case 'buy':
      if (action !== 'cancel') {
        const id = Number(action);
        if (item(id).cost > g.player.gold) { say(g, "You don't have enough gold coins for that."); g.menu = m; }
        else g.menu = { kind: 'buy-confirm', id };
      }
      break;
    case 'buy-confirm':
      if (action === 'yes') {
        const value = item(m.id);
        if (value.cost > g.player.gold) throw new Error('Not enough gold');
        addItem(g, m.id); g.player.gold -= value.cost; say(g, `Bought ${value.name}`); g.menu = { kind: 'buy' };
      }
      break;
    case 'sell':
      if (action !== 'cancel') {
        const id = Number(action), amount = g.inventory.find(e => e.id === id)!.amount;
        g.menu = amount > 1 ? { kind: 'sell-amount', id } : { kind: 'sell-confirm', id, amount: 1 };
      }
      break;
    case 'sell-amount': if (action !== 'cancel') g.menu = { kind: 'sell-confirm', id: m.id, amount: Number(action) }; break;
    case 'sell-confirm':
      if (action === 'yes') {
        removeItem(g, m.id, m.amount);
        const profit = round(item(m.id).cost / 2) * m.amount; g.player.gold += profit;
        say(g, `Sold ${m.amount} ${item(m.id).name} for ${profit} gold coins`); recount(g);
      }
      break;
    case 'quest':
      if (action === 'yes') {
        g.quests.push(m.quest); say(g, 'Quest has been taken');
        if (m.source === 'tavern') g.tavern!.quests = false;
        if (m.source === 'npc') { g.npcOffer = null; g.scene = 'peace'; }
      }
      break;
    case 'drink': if (action === 'yes') g.menu = { kind: 'stats' }; else offerPlot(g); break;
    case 'stats':
      if (action !== 'cancel') {
        g.player[action as 'endurance' | 'strength' | 'agility' | 'luck']++;
        g.player.aleg_drinks++; recount(g);
        say(g, `${action[0].toUpperCase() + action.slice(1)} has been increased!`);
      }
      offerPlot(g); break;
  }
  if (g.log[g.log.length - 1] === '') g.log.pop();
  return g;
}
