import random

HOSTILE = ["mountains", "forest", "cave"]
PEACEFUL = ["village", "river"]


class Location:
    def __init__(self, type_):
        self.type = type_
        self.enemies = 0
        if self.type == 'hostile':
            self.enemies = random.randint(0, 10)

        if self.type == 'peaceful':
            self.name = random.choice(PEACEFUL)
        elif self.type == 'hostile':
            self.name = random.choice(HOSTILE)
        elif self.type == 'hometown':
            self.name = 'hometown'
            self.type = 'peaceful'
