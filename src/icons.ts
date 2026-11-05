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
export const CONTROL_TILES: Record<string, number> = {
  status: 0, exit: 1, left: 2, right: 3, confirm: 4, cancel: 5,
  menu: 6, new: 7, export: 8, import: 9, install: 10, reload: 11,
};
export function icon(name: string): SVGSVGElement {
  const control = Object.hasOwn(CONTROL_TILES, name);
  const tile = control ? CONTROL_TILES[name] : ICON_TILES[name] ?? ICON_TILES.phantom;
  const cols = control ? 4 : 6, rows = control ? 3 : 6;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('class', 'game-icon'); svg.setAttribute('aria-hidden', 'true');
  svg.dataset.icon = name;
  const image = document.createElementNS(svg.namespaceURI, 'image');
  image.setAttribute('href', control ? '/art/controls.webp' : '/art/icons.webp');
  image.setAttribute('width', String(cols * 100)); image.setAttribute('height', String(rows * 100));
  image.setAttribute('preserveAspectRatio', 'none');
  image.setAttribute('x', String(-(tile % cols) * 100)); image.setAttribute('y', String(-Math.floor(tile / cols) * 100));
  if (name === 'shade') svg.style.filter = 'hue-rotate(65deg)';
  if (name === 'specter') svg.style.filter = 'hue-rotate(-50deg)';
  svg.append(image); return svg;
}
export function decorateButton(button: HTMLButtonElement, name: string, text = button.textContent?.trim() ?? '') {
  const accessibleName = button.getAttribute('aria-label') ?? text;
  button.replaceChildren(); button.setAttribute('aria-label', accessibleName);
  const image = document.createElement('span'); image.className = 'action-icon'; image.append(icon(name));
  const label = document.createElement('span'); label.className = 'action-label'; label.textContent = text;
  button.append(image, label);
}
export const enemyIcon = (name: string) => ({
  'Homeless guy': 'wanderer', Bandit: 'bandit', Knight: 'knight', Berserk: 'berserk',
  'Wet dog': 'dog', Hyena: 'hyena', Wolf: 'wolf', Werewolf: 'werewolf',
  'Van Helsing': 'hunter', Aleg: 'aleg', test1: 'wisp', test2: 'shade', test3: 'specter', test4: 'phantom',
}[name] ?? 'phantom');
export function actionIcon(g: Game, id: string): string {
  if (['inventory', 'buy', 'sell'].includes(g.menu.kind) && /^\d+$/.test(id)) return `item-${item(Number(id)).id}`;
  return ({
    'enter tavern': 'tavern', 'check a chest': 'chest', attack: 'item-99', inventory: 'bag', merchant: 'coins',
    'go forward': 'road', 'take a beer': 'item-1', 'take a steak': 'item-2', 'talk with Aleg': 'aleg',
    'get status': 'status', 'exit game': 'exit', 'go out': 'left', 'back to tavern': 'tavern',
    buy: 'coins', sell: 'coins', 'check quests': 'status', 'talk with Carl': 'wanderer', 'run away': 'road',
    yes: 'confirm', no: 'cancel', cancel: 'cancel', endurance: 'item-1', strength: 'item-7', agility: 'road', luck: 'coins',
  } as Record<string, string>)[id] ?? (g.menu.kind === 'sell-amount' ? 'coins' : 'road');
}
