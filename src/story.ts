import { tokenizeLog, renderLogRange } from './log-format';

/** Fit the complete narrative into pages instead of hiding it in a scroll area. */
export class StoryPages {
  private lines: string[] = [];
  private pages: HTMLElement[][] = [];
  private page = -1;
  constructor(private story: HTMLElement, private pager: HTMLElement, private label: HTMLElement,
    private older: HTMLButtonElement, private newer: HTMLButtonElement) {
    older.onclick = () => { this.page--; this.paint(); };
    newer.onclick = () => { this.page++; this.paint(); };
    new ResizeObserver(() => this.layout(false)).observe(story);
  }
  set(lines: string[]) {
    this.lines = lines.filter(line => !/^You're in the (?:location|tavern|merchant shop)/.test(line));
    this.layout(true);
  }
  private layout(latest: boolean) {
    if (this.story.clientHeight < 10 || this.story.clientWidth < 10) return;
    // Reserve history controls before measuring so revealing them cannot shrink
    // the text area after pagination. The controls take a single fixed row.
    this.pager.hidden = false;
    const height = this.story.clientHeight;
    if (height < 10) return;
    const oldPage = this.page, wasLatest = this.page === this.pages.length - 1;
    const pages: HTMLElement[][] = []; let page: HTMLElement[] = [];
    this.story.replaceChildren();
    const commit = () => { if (page.length) pages.push(page); page = []; this.story.replaceChildren(); };
    const fits = () => this.story.scrollHeight <= height;
    let boundary = false;
    for (const text of this.lines) {
      if (!text.trim()) { boundary = true; continue; }
      if (boundary && page.length) {
        const hr = document.createElement('hr'); hr.className = 'divider'; this.story.append(hr);
        if (fits()) page.push(hr); else { hr.remove(); commit(); }
      }
      boundary = false;
      let words = text.split(/\s+/);
      const source = words.join(' '), tokens = tokenizeLog(source); let offset = 0;
      const fill = (p: HTMLElement, count: number) => renderLogRange(p, tokens, offset, offset + words.slice(0, count).join(' ').length);
      while (words.length) {
        const p = document.createElement('p'); fill(p, words.length); this.story.append(p);
        if (fits()) { page.push(p); break; }
        p.remove();
        // Prefer moving a complete paragraph to the next page.
        if (page.length) { commit(); continue; }
        let low = 1, high = words.length, count = 1;
        while (low <= high) {
          const mid = Math.floor((low + high) / 2); fill(p, mid); this.story.append(p);
          if (fits()) { count = mid; low = mid + 1; } else high = mid - 1;
          p.remove();
        }
        fill(p, count); this.story.append(p); page.push(p);
        offset += words.slice(0, count).join(' ').length + 1;
        words = words.slice(count); if (words.length) commit();
      }
    }
    commit(); this.pages = pages;
    this.page = latest || wasLatest || oldPage < 0 ? Math.max(0, pages.length - 1) : Math.min(oldPage, pages.length - 1);
    this.paint();
  }
  private paint() {
    this.page = Math.max(0, Math.min(this.page, this.pages.length - 1));
    this.story.replaceChildren(...(this.pages[this.page] ?? []));
    this.pager.hidden = this.pages.length < 2;
    this.label.textContent = `${this.page + 1} / ${Math.max(1, this.pages.length)}`;
    this.older.disabled = this.page === 0; this.newer.disabled = this.page >= this.pages.length - 1;
  }
}
