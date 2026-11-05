# nomad_backend
Only CLI version of game (4th iteration)

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

# browser version

Run the browser interface with the same installed dependencies:

```sh
.venv/bin/python web_server.py
```

Open your local browser at `http://127.0.0.1:8000`. Actions, inventory items,
merchant purchases, quest decisions, and confirmations use labeled buttons.
Health, equipment, gold, and moves update after each choice. Reloading reconnects
to the current prompt; New journey starts over after confirmation.

The CLI remains available through `python main.py`. The web server runs each
browser session in a separate process with its own temporary SQLite database,
quests, and log. Web games do not reset CLI saves. Sessions are temporary: server
shutdown removes them, and inactive sessions can be reclaimed after 30 minutes.
The local development server supports up to 16 sessions; it is not a production
hosting service. Use `--host` and `--port` to change the listening address.

Run `.venv/bin/python -m pytest -q` to include HTTP integration checks for button
flows, purchases, refresh, separate browser sessions, and stale/invalid actions.

# Vercel deployment

Import this GitHub repository in Vercel and select branch `chatgpt/web`. Keep the
repository root as Root Directory and use the committed `vercel.json` (static
output `web`, Python functions in `api/`). No frontend build command is needed.

Before deploying, add `NOMAD_SAVE_SECRET` in Vercel Environment Variables for
Production and Preview. Use a securely generated random value of at least 32
characters; never commit it. Keep it stable across deployments if saves should
continue to work. Changing the key invalidates existing saves.

Vercel uses a stateless adapter rather than the local persistent-process server.
Each API request authenticates a JSON save, replays the recorded button choices
with their original random seed in an isolated temporary directory, and returns
the next prompt. Temporary SQLite and quest files are removed after each request.
A signed save lives in browser local storage, expires after seven days, and can
be restored on a different function instance. No database service is required.
Clearing browser storage loses that browser's save; prior signed saves can be
replayed, so this is a casual single-player game, not an anti-cheat leaderboard.

The API fails closed when the signing key is missing or the save was modified.
Replay is capped at 3,000 button choices and 20 seconds per replay. A 232-choice
winning game was reproduced locally within the replay timeout; deployed function
performance still needs verification. Saves are versioned: bump `SAVE_VERSION`
in `vercel_game.py` when incompatible game-rule changes are deployed.

After deployment, verify: start a journey, enter the tavern, buy beer, reload
(the gold/alcohol values should persist), open inventory, and finish an exit
confirmation. `python web_server.py` still runs the process-based local version;
Vercel does not start that server.
