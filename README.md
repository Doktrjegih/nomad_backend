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
