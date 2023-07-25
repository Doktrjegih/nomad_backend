import random
from player import Player

HOSTILE = ["mountains", "forest", "cave"]
PEACEFUL = ["village", "river"]


class Location:
    def __init__(self, type_, player: Player) -> None:
        self.type = type_
        self.enemies = False
        self.tavern = False
        self.chest = False
        self.player = player

        if self.type == 'hostile':
            self.enemies = True if random.randint(0, 10) > 4 else False
            self.name = random.choice(HOSTILE)
        if self.type == 'peaceful':
            self.name = random.choice(PEACEFUL)
            self.tavern = True if random.randint(0, 10) > 9 else False
        elif self.type == 'hometown':
            self.name = 'hometown'
            self.type = 'peaceful'
            self.tavern = True

        if self.type != 'hometown' and not self.tavern and not self.enemies:
            if random.randint(1, 100) + self.player.luck * 2 > 95:
                self.chest = True
