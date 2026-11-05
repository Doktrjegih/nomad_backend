import { ENEMY_NAMES, ITEMS } from './engine';
export interface LogToken { text: string; kind?: string }
const effects: Record<string, string> = {
  fire: 'fire', cold: 'cold', poison: 'poison', bleeding: 'bleeding', rage: 'rage',
  healing: 'healing', heals: 'healing', healed: 'healing', alcohol: 'alcohol', drunk: 'alcohol',
};
const terms = new Map<string, string>([
  ...ITEMS.map(i => [i.name.toLowerCase(), `item log-${i.type}`] as [string, string]),
  ...ENEMY_NAMES.map(name => [name.toLowerCase(), 'enemy'] as [string, string]),
  ...Object.entries(effects),
]);
const escape = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
// Longest names first keep complete equipment names together (e.g. Elderfire
// greatsword), rather than highlighting an elemental substring inside a name.
const pattern = new RegExp('(?<gold>\\d+\\s+gold\\s+coins?)|' + [...terms.keys()].sort((a, b) => b.length - a.length).map(escape).join('|'), 'giu');
const word = /[\p{L}\p{N}_]/u;
export function tokenizeLog(text: string): LogToken[] {
  const tokens: LogToken[] = []; let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    const start = match.index, end = start + match[0].length;
    if ((start > 0 && word.test(text[start - 1])) || (end < text.length && word.test(text[end]))) continue;
    if (start > cursor) tokens.push({ text: text.slice(cursor, start) });
    tokens.push({ text: match[0], kind: match.groups?.gold ? 'gold' : terms.get(match[0].toLowerCase()) }); cursor = end;
  }
  if (cursor < text.length) tokens.push({ text: text.slice(cursor) });
  return tokens;
}
/** Render only text and spans; imported log text never becomes executable HTML.
 * Offsets preserve highlights when a long equipment/enemy name crosses a page.
 */
export function renderLogRange(element: HTMLElement, tokens: LogToken[], start: number, end: number) {
  const nodes: Node[] = []; let offset = 0;
  for (const token of tokens) {
    const finish = offset + token.text.length;
    const text = token.text.slice(Math.max(0, start - offset), Math.min(token.text.length, end - offset));
    if (finish > start && offset < end && text) {
      if (token.kind) { const span = document.createElement('span'); span.className = `log-${token.kind}`; span.textContent = text; nodes.push(span); }
      else nodes.push(document.createTextNode(text));
    }
    offset = finish;
    if (offset >= end) break;
  }
  element.replaceChildren(...nodes);
}
