import { item, type Game } from './engine';
/** Tile positions in the generated 6 × 6 painted RPG atlas. */
export const ICON_TILES: Record<string, number> = {
  'item-1': 0, 'item-2': 1, 'item-3': 2, 'item-4': 3, 'item-99': 4, 'item-6': 5,
  'item-7': 6, 'item-8': 7, 'item-10': 8, 'item-11': 9, 'item-12': 10, 'item-13': 11,
  'item-5': 12, 'item-98': 13, 'item-97': 14, 'item-96': 15, 'item-95': 16,
  bag: 17, coins: 18, chest: 19, tavern: 20, road: 21, sword: 22, armor: 23,
  wanderer: 24, bandit: 25, knight: 26, berserk: 27, dog: 28, hyena: 29,
  wolf: 30, werewolf: 31, hunter: 32, aleg: 33, wisp: 34, shade: 34, specter: 35, phantom: 35,
};
export function icon(name: string): SVGSVGElement {
  const tile = ICON_TILES[name] ?? ICON_TILES.phantom;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('class', 'game-icon'); svg.setAttribute('aria-hidden', 'true');
  svg.dataset.icon = name;
  const image = document.createElementNS(svg.namespaceURI, 'image');
  image.setAttribute('href', '/art/icons.webp'); image.setAttribute('width', '600'); image.setAttribute('height', '600');
  image.setAttribute('x', String(-(tile % 6) * 100)); image.setAttribute('y', String(-Math.floor(tile / 6) * 100));
  if (name === 'shade') svg.style.filter = 'hue-rotate(65deg)';
  if (name === 'specter') svg.style.filter = 'hue-rotate(-50deg)';
  svg.append(image); return svg;
}
export const enemyIcon = (name: string) => ({
  'Homeless guy': 'wanderer', Bandit: 'bandit', Knight: 'knight', Berserk: 'berserk',
  'Wet dog': 'dog', Hyena: 'hyena', Wolf: 'wolf', Werewolf: 'werewolf',
  'Van Helsing': 'hunter', Aleg: 'aleg', test1: 'wisp', test2: 'shade', test3: 'specter', test4: 'phantom',
}[name] ?? 'phantom');
export function actionIcon(g: Game, id: string): string | null {
  if (['inventory', 'buy', 'sell'].includes(g.menu.kind) && /^\d+$/.test(id)) return `item-${item(Number(id)).id}`;
  return ({ 'enter tavern': 'tavern', 'check a chest': 'chest', attack: 'item-99', inventory: 'bag', merchant: 'coins',
    'go forward': 'road', 'take a beer': 'item-1', 'take a steak': 'item-2', 'talk with Aleg': 'aleg' } as Record<string, string>)[id] ?? null;
}
