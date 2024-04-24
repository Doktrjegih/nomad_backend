import random

HOSTILE = ["mountains", "forest", "cave"]
PEACEFUL = ["village", "river"]


class Location:
    def __init__(self, type_, player_luck: int, turns_without_tavern=0) -> None:
        self.type = type_
        self.enemies = False
        self.tavern = False
        self.chest = False
        self.npc = False

        if self.type == 'hostile':
            self.enemies = True if random.randint(1, 10) > 5 else False
            self.name = random.choice(HOSTILE)
        if self.type == 'peaceful':
            self.name = random.choice(PEACEFUL)
            if turns_without_tavern > 10:
                self.tavern = True if random.randint(1, 10) > 9 else False
            if not self.tavern:
                self.npc = True if random.randint(1, 10) > 9 else False
        elif self.type == 'hometown':
            self.name = 'hometown'
            self.type = 'peaceful'
            self.tavern = True

        if not self.tavern and not self.enemies:
            if random.randint(1, 100) + player_luck * 2 > 95:
                self.chest = True
