import { item, type Game } from './engine';
export function icon(name: string): SVGSVGElement {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 48 48'); svg.setAttribute('class', 'game-icon'); svg.setAttribute('aria-hidden', 'true');
  const use = document.createElementNS(svg.namespaceURI, 'use'); use.setAttribute('href', `/game-icons.svg#${name}`); svg.append(use);
  return svg;
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
