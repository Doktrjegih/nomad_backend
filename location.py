import random

from constants import *

HOSTILE = ["mountains", "forest", "cave"]
PEACEFUL = ["village", "river"]


class Location:
    def __init__(self, type_: str, player_luck: int, turns_without_tavern=0, name=None) -> None:
        self.type = type_
        self.enemies = False
        self.tavern = False
        self.chest = False
        self.npc = False
        self.name = name

        if self.type == 'hostile':
            self.enemies = True if random.randint(1, 100) > ENEMIES_IN_LOCATION_THRESHOLD else False
            if not self.name:
                self.name = random.choice(HOSTILE)
        elif self.type == 'peaceful':
            if not self.name:
                self.name = random.choice(PEACEFUL)
            if turns_without_tavern > TURNS_WITHOUT_TAVERN:
                self.tavern = True if random.randint(1, 100) > TAVERN_SPAWN_THRESHOLD else False
            if not self.tavern:
                self.npc = True if random.randint(1, 100) > NPC_SPAWN_THRESHOLD else False
        elif self.type == 'hometown':
            self.name = 'hometown'
            self.type = 'peaceful'
            self.tavern = True

        if not self.tavern and not self.enemies:
            if random.randint(1, 100) + player_luck * CHEST_LUCK_FACTOR > CHEST_SPAWN_THRESHOLD:
                self.chest = True
