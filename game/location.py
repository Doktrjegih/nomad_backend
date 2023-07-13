import random

HOSTILE = ["mountains", "forest", "cave"]
PEACEFUL = ["village", "river"]


class Location:
    def __init__(self, type_) -> None:
        self.type = type_
        self.enemies = False
        self.tavern = False
        if self.type == 'hostile':
            self.enemies = True if random.randint(0, 10) > 1 else False
            self.name = random.choice(HOSTILE)
        if self.type == 'peaceful':
            self.name = random.choice(PEACEFUL)
            self.tavern = True if random.randint(0, 10) > 7 else False
        elif self.type == 'hometown':
            self.name = 'hometown'
            self.type = 'peaceful'
            self.tavern = True
