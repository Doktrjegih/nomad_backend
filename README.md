# nomad_backend
Only CLI version of game

# gameplay
* This is turn-driven game
* Each turn player can:
- move to next area
- check current status
- change equipment
- save and stop game
* When player get into hostile area, game checks either it has enemies or not
* If player meet an enemy, he can try to run away or fight with it
* Battle mode:
- player can attack an enemy or try to run away
- player can change equipment
- if player health is 0, game is over
- if player killed the enemy, he gets an award
* Player can meet a merchant in peaceful zone and buy/sell goods/equipment

# technical details
Objects - scene, player, enemies, places, weapons

scene_obj:
- location
- player
- state
- enemies

player_obj:
- name
- health
- attack
- defence
- scores (level)
- gold

enemy_obj:
- name
- health
- attack
- defence
- level

location_obj:
- name
- type (peaceful/hostile)
- enemies (if hostile)
- chests (if hostile)

weapon_obj:
- name
- type (melee/range)
- damage
- condition
