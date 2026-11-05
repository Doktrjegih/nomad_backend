import { test } from 'node:test';
import assert from 'node:assert/strict';
import { act, addItem, createGame, equipment, item, level, makeEnemy, recount, round, view, type Game } from '../src/engine';
import { validateGame } from '../src/storage';
const fresh = (seed = 42) => createGame(seed, `test-${seed}`);
function click(g: Game, label: string): Game {
  const option = view(g).options.find(o => o.label.includes(label));
  assert.ok(option, `${label} missing in ${g.menu.kind}`);
  return act(g, option.id);
}
function battle(g: Game, name = 'Wet dog', stage = 1): Game {
  g.scene = 'battle'; g.enemy = makeEnemy(g, name, stage, ['Aleg', 'Van Helsing'].includes(name)); return g;
}
function restore(g: Game) { return validateGame(JSON.parse(JSON.stringify(g))); }

test('tavern, purchases, menu restoration, inventory and exit work without a server', () => {
  let g = click(fresh(), 'enter tavern');
  g = click(g, 'take a beer');
  assert.equal(g.player.gold, 5); assert.equal(g.player.drunk, 10); assert.equal(g.player.moves, 1);
  g = click(g, 'inventory'); assert.equal(view(restore(g)).question, view(g).question);
  g = click(g, 'Broken Spear'); assert.equal(equipment(g, 'weapon'), undefined);
  g = click(click(g, 'inventory'), 'Broken Spear'); assert.equal(equipment(g, 'weapon')?.id, 3);
  g = click(click(g, 'exit game'), 'No'); assert.equal(g.status, 'playing');
  g = click(click(g, 'exit game'), 'Yes'); assert.equal(g.status, 'finished'); assert.equal(g.outcome, 'exit');
  assert.deepEqual(view(g).options, []);
});

test('shop confirms cost, rejects unaffordable items, sells equipped gear, and handles stacks', () => {
  let g = click(click(fresh(), 'enter tavern'), 'merchant');
  g = click(click(click(g, 'buy'), 'Broken Spear'), 'Yes');
  assert.equal(g.player.gold, 7); assert.equal(g.inventory.find(e => e.id === 3)?.amount, 2);
  g = click(g, 'Hot iron axe'); assert.equal(g.menu.kind, 'buy'); assert.equal(g.player.gold, 7);
  g = click(g, 'Cancel');
  g = click(click(g, 'sell'), 'Broken Spear');
  assert.equal(g.menu.kind, 'sell-amount');
  g = act(g, '2'); g = click(restore(g), 'Yes');
  assert.equal(g.player.gold, 11); assert.equal(equipment(g, 'weapon'), undefined); assert.equal(g.player.attack, 10);
});

test('food caps at maximum health, alcohol caps at 100, and inventory items are consumed', () => {
  let g = fresh(); addItem(g, 1); addItem(g, 2); g.player.drunk = 98; recount(g);
  g = click(click(g, 'inventory'), 'Beer bottle'); assert.equal(g.player.drunk, 100);
  assert.ok(!g.inventory.some(e => e.id === 1));
  g = click(click(g, 'inventory'), 'Steak');
  assert.equal(g.player.health, 100); assert.equal(g.player.drunk, 98); assert.equal(g.player.moves, 2);
});

test('stale and forged actions do not mutate the source snapshot', () => {
  const g = fresh(), snapshot = JSON.stringify(g);
  assert.throws(() => act(g, 'hesoyam'));
  assert.throws(() => act(g, 'go forward', -1));
  assert.equal(JSON.stringify(g), snapshot);
  const next = act(g, 'go forward'); assert.notEqual(next, g); assert.equal(JSON.stringify(g), snapshot);
});

test('random cursor, pending roads, battle damage, and enemy special counters survive round trips', () => {
  let g = click(fresh(), 'go forward');
  assert.deepEqual(act(restore(g), '0'), act(g, '0'));
  g = battle(fresh(), 'Van Helsing', 3); g.enemy!.health = 10; g.player.health = 1000; g.player.endurance = 100; recount(g);
  g = act(g, 'attack');
  assert.deepEqual(act(restore(g), 'attack'), act(g, 'attack'));
});

test('combat kills prevent retaliation, advance quests, pay gold, and award predictable gear', () => {
  let g = fresh(); g.quests.push({ order: 'Wet dog', goal: 2, current: 0, reward: 10, plot: false, boss: false });
  for (let n = 0; n < 4; n++) {
    battle(g); g.enemy!.health = 1; g.player.luck = 100; recount(g);
    const hp = g.player.health;
    // Find a deterministic hitting seed (there is still a bounded 5% miss chance).
    let next = act(g, 'attack');
    while (next.enemy) next = act(next, 'attack');
    g = next; assert.ok(g.player.health <= hp);
  }
  assert.equal(g.player.battles_won, 4); assert.ok(g.player.gold >= 42);
  assert.ok(g.inventory.some(e => e.id === 99)); assert.ok(g.inventory.some(e => e.id === 95));
  assert.equal(g.quests[0].current, 2);
  g.scene = 'tavern'; g.tavern = { merchant: true, aleg: true, quests: false, offer: null };
  const gold = g.player.gold; g = click(g, 'check quests');
  assert.equal(g.player.gold, gold + 10); assert.equal(g.quests.length, 0); assert.ok(g.inventory.some(e => e.id === 1));
});

test('safe tavern appears by eight travels, independently of hostile routes', () => {
  let g = fresh();
  g.withoutTavern = 8; g.biomeLeft = 3;
  g.place = { name: 'forest', type: 'hostile', enemies: false, tavern: false, chest: false, npc: false };
  g = click(g, 'go forward');
  assert.equal(g.place.tavern, true); assert.equal(g.place.enemies, false); assert.equal(g.scene, 'peace');
  assert.equal(g.player.travel_moves, 1);
});

test('endurance and agility improve separate stats, while enemy tiers depend on story', () => {
  const g = fresh(); g.player.endurance = 4; g.player.agility = 2; recount(g);
  assert.equal(g.player.max_hp, 160); assert.equal(g.player.defence, 14); assert.equal(g.player.attack, 11);
  const a = makeEnemy(fresh(), 'Wet dog', 1), other = fresh(); other.player.endurance = 100;
  assert.deepEqual(makeEnemy(other, 'Wet dog', 1), a);
});

test('equipment effects and Python-style rounding remain intact', () => {
  const g = fresh(); g.player.drunk = 25;
  assert.deepEqual(level(g, item(4))?.effects, [{ name: 'poison', damage: 1 }]);
  assert.equal(round(2.5), 2); assert.equal(round(3.5), 4); assert.equal(round(1.5), 2);
  const e = makeEnemy(g, 'Van Helsing', 3, true);
  assert.ok(e.health > 50); assert.ok(e.boss);
});

test('story turn-ins heal, offer a stat drink, then advance to the next story quest', () => {
  let g = click(fresh(), 'enter tavern');
  g = click(click(g, 'talk with Aleg'), 'Yes'); assert.equal(g.quests[0].order, 'Wet dog');
  g.quests[0].current = 3; g.player.health = 12;
  g = click(g, 'talk with Aleg'); assert.equal(g.player.health, 100); assert.equal(g.player.plot_stage, 2);
  g = click(click(g, 'Yes'), 'Vodka'); assert.equal(g.player.strength, 2); assert.equal(g.player.aleg_drinks, 1);
  g = click(g, 'Yes'); assert.equal(g.quests[0].order, 'Hyena');
});

test('story boss victories and ordinary deaths have real terminal states', () => {
  let g = battle(fresh(), 'Aleg', 4); g.enemy!.health = 1;
  for (let i = 0; i < 5 && g.status === 'playing'; i++) g = act(g, 'attack');
  assert.equal(g.outcome, 'win'); assert.ok(g.log.some(l => l.includes('You win!')));
  g = battle(fresh()); g.player.health = 1; g.enemy!.health = 1000;
  g = act(g, 'attack'); assert.equal(g.outcome, 'death'); assert.equal(g.status, 'finished');
  assert.doesNotThrow(() => restore(g));
});

test('unknown versions and malformed saves cannot silently reset a journey', () => {
  for (const patch of [{ version: 2 }, { rng: NaN }, { player: null }, { menu: { kind: 'roads' } },
    { quests: [null] }, { inventory: [{ id: 123456, amount: 1, used: true }] }, { log: [42] }]) {
    assert.throws(() => validateGame({ ...fresh(), ...patch }));
  }
  assert.throws(() => validateGame(null)); assert.doesNotThrow(() => restore(fresh()));
});

// A complete policy run exercises the actual transitions, rather than granting story progress.
function play(seed: number): Game {
  let g = fresh(seed), equippedThisStop = false;
  for (let steps = 0; steps < 4000 && g.status === 'playing' && g.player.moves < 500; steps++) {
    validateGame(g);
    const m = g.menu; let action: string;
    if (m.kind === 'roads') {
      action = String(Math.max(0, m.places.findIndex(p => p.type === 'hostile')));
      equippedThisStop = false;
    } else if (m.kind === 'quest' || m.kind === 'drink') action = 'yes';
    else if (m.kind === 'stats') action = 'strength';
    else if (m.kind === 'inventory') {
      const upgrades = g.inventory.filter(e => ['weapon', 'armor'].includes(item(e.id).type) && !e.used)
        .filter(e => {
          const value = item(e.id), old = equipment(g, value.type as 'weapon' | 'armor');
          const score = (v: typeof value) => (level(g, v)?.attack ?? level(g, v)?.defence ?? 0);
          return !old || score(value) > score(old);
        });
      action = upgrades.length ? String(upgrades[0].id) : 'cancel';
    } else if (m.kind !== 'main') action = view(g).options.some(o => o.id === 'cancel') ? 'cancel' : 'no';
    else if (g.scene === 'battle') action = 'attack';
    else if (g.scene === 'tavern') {
      if (g.player.health < g.player.max_hp - 10 && g.player.gold >= 5) action = 'take a steak';
      else if (!equippedThisStop) { equippedThisStop = true; action = 'inventory'; }
      else if (g.tavern?.aleg && (!g.quests.some(q => q.plot) || g.quests.some(q => q.plot && q.current >= q.goal))) action = 'talk with Aleg';
      else action = 'go out';
    } else if (g.place.tavern) {
      const needs = g.player.health < g.player.max_hp - 10 && g.player.gold >= 5;
      const plot = !g.quests.some(q => q.plot) || g.quests.some(q => q.plot && q.current >= q.goal);
      if (needs || !equippedThisStop || (plot && (!g.tavern || g.tavern.aleg))) action = 'enter tavern';
      else action = 'go forward';
    } else if (g.place.chest) action = 'check a chest';
    else action = 'go forward';
    g = act(g, action);
  }
  return g;
}
test('seeded complete journeys reach story bosses and a winning ending without cheats', () => {
  const outcomes = Array.from({ length: 20 }, (_, seed) => play(seed));
  const wins = outcomes.filter(g => g.outcome === 'win');
  assert.ok(wins.length > 0, 'policy must reach and defeat Aleg');
  assert.ok(outcomes.every(g => g.status === 'finished'), 'no unexplained stalled journeys');
  assert.ok(wins.every(g => g.player.plot_stage === 4 && g.player.battles_won >= 7));
  console.log(`Seeded policy: ${wins.length}/20 wins; first win seed ${outcomes.findIndex(g => g.outcome === 'win')}, ${wins[0].player.moves} moves.`);
});

test('quiet travel reports an uneventful move, but encounters and cancelled travel do not', () => {
  const empty = { name: 'village', type: 'peaceful' as const, enemies: false, tavern: false, chest: false, npc: false };
  for (const event of [null, 'enemies', 'tavern', 'chest', 'npc'] as const) {
    const g = fresh();
    const place = { ...empty };
    if (event) place[event] = true;
    g.menu = { kind: 'roads', places: [place, { ...empty, name: 'river' }] };
    const moved = act(g, '0');
    assert.equal(moved.player.travel_moves, 1);
    assert.equal(moved.log.includes('Nothing interesting so far.'), event === null);
    assert.ok(!act(g, 'cancel').log.includes('Nothing interesting so far.'));
  }
});
