# Nomad · Offline PWA

The `chatgpt/ts_pwa` branch runs the game entirely in your browser. TypeScript
handles combat, travel, equipment, merchants, quests, and endings. There are no
API calls, Python runtime, signing keys, accounts, or remote database in this app.
The Python implementation remains in the repository as a CLI/reference version.

## Run and verify

Use Node.js 22+ (tested with Node 24):

```sh
npm ci
npm run dev
```

For the installable offline version:

```sh
npm test
npm run build
npm run preview
npm run test:e2e
```

`npm run build` runs strict TypeScript checks and generates `dist/`, including a
service worker that precaches every app asset. Development mode deliberately
leaves service-worker caching off. Playwright uses `/usr/bin/chromium` by default;
set `CHROMIUM_PATH` to your browser executable on another machine. For example,
install Chromium with `npx playwright install chromium` and use its executable
path. HTTP integration tests require local socket access.

## Offline play and saves

Open the app once on HTTPS (or localhost) and let the offline assets finish downloading.
You can then disconnect, reload, close/reopen the app, and start new journeys
without Internet. Use **Install game** when your browser offers installation; on
iOS use Safari's Share → Add to Home Screen. Installation is optional.

Each successful action saves a complete versioned snapshot in IndexedDB, including
inventory, quests, current dialog, enemy specials, story log, and the random-number
cursor. Turns never replay previous choices. Reloading restores the exact prompt.
Two tabs compare save tokens in an atomic transaction to prevent lost updates.
A failed save does not advance the displayed game. Updates wait until you choose
**Update ready · Reload**, and keep the saved journey.

Saves have no expiry. They belong to this browser/profile and origin; clearing
site data, private browsing cleanup, or browser storage eviction can remove them.
Use **Export save** for a backup and **Import save** to move a journey to another
browser/device. The app requests persistent storage where supported, but browsers
may decline it. Corrupt or unsupported saves are preserved for export until you
explicitly reset them. Previous signed saves from the Python/Vercel replay version
are not imported. Local saves are editable; this is a single-player game.

## Static deployment

Vercel: select `chatgpt/ts_pwa`, repository root, and the committed `vercel.json`.
It installs with `npm ci`, builds with `npm run build`, and serves **dist**.
The old `api/` functions are removed and Python files are excluded from deployment.
No environment variables or `NOMAD_SAVE_SECRET` are required. Remove any manually
configured dashboard build/output overrides that conflict with these settings.
You can also serve `dist/` with any static HTTPS host. The app assumes the origin
root (`/`); deployment under a subdirectory would need base-path changes.

## Rules and validation

`src/engine.ts` is a pure snapshot transition engine and imports the original
item, enemy-effect, and story JSON data. It retains story-driven encounter tiers,
smooth damage mitigation, alcohol equipment stages, elemental damage/resistance,
Hyena/Wolf/Werewolf/Van Helsing specials, predictable second/fourth-victory gear,
tavern recovery and quests, Carl encounters, Aleg stat drinks, and story endings.
Python's ties-to-even rounding is preserved. The browser uses a saved Mulberry32
random cursor; matching Python seed numbers do not produce identical journeys.
Declining route selection consumes no travel move.

Rules tests cover purchases, sales, consumables, restoration, combat, quests,
progression, death/win endings, invalid actions and save formats, and 20 complete
seeded games through the actual choices. Browser tests exercise the production
build with networking disabled, including caching, reloads, export/import,
multiple tabs, storage failures, and mobile layout.

## Legacy Python game

The following describes the retained Python version, which is not used by the PWA.
Install `requirements.txt` in a virtual environment and run `python main.py`.
The older process-based browser UI is still available through `python web_server.py`.

# gameplay
This is turn-driven game. During the game you can:
- travel across different locations
- meet and fight enemies
- explore the lore by plot quests
- pass side missions for reward
- drink alcohol to get special effects
- loot and change equipment
- buy and sell goods

Find your own style of playing and have fun!

# technical solutions
- endless loop for the processing the game
- DB for storing items (temporary)
- pickle for storing quests (temporary)
- overriden print for logging last game session to the file
- common handler for user's inputs and validation of them
- random generating of many objects:
    - locations
    - enemies (based on player's stats)
    - treasure chests
    - quests in taverns and from the strangers
- inheritance of classes (Boss from Enemy)
- relative paths are used
- tempopary files are created
- JSONs keep some data (plot quests, enemies, items)
- autotests for some scenarios
    - use pieces of code to generate needed environment
    - perform actions
    - check results by comparing game log
- autoplayer for adjusting the balance can:
    - go forward
    - enter taverns for buying goods, taking and completing quests
    - fight enemies
    - loot chests
    - take quests from the strangers
    - consume goods and change gear

# balance and reproducible runs

Combat uses smooth defence mitigation, bounded accuracy, and fixed enemy HP per
story tier. Alcohol improves equipment without jumping enemy tiers; strength
improves attack, agility defence, endurance HP, and luck accuracy/loot. Every
victory pays gold. The second and fourth wins grant an Iron sword and Leather
armor; a safe tavern appears after at most eight travels without one. Story
turn-ins restore HP, and story targets can appear outside their usual biome.

`Player.moves` counts travel, attack, retreat, and food/alcohol actions. Browsing
menus and equipping items do not advance this counter. Games target 100–500 such
moves; this is a pacing goal, not a forced timeout or a guarantee for every policy.

Run tests with `.venv/bin/python -m pytest -q`. Run seeded simulations with:

```sh
.venv/bin/python tools/balance_simulation.py --runs 100 --seed 100
```

The simulator resets local game state; do not run it alongside an interactive
game. It writes per-game transcripts and `results.csv` under ignored
`temp_files/balance/`, distinguishing wins, story losses, deaths, and runs censored
at 500 moves. A fresh 100-seed evaluation (100–199) produced 47 wins, 9 story
losses, and 44 deaths; 97 runs finished within 100–500 moves, with median 156 and
range 79–274. This evaluates the supplied automated policy, not human players.
