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
