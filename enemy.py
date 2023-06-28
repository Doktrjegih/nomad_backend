from player import Player


class Enemy:
    def __init__(self, player: Player):
        self.player = player

        self.name = 'Anthon'
        self.health = 3
        self.attack = 2
        self.defence = 1
        self.level = self.player.level

    def show_enemy_stats(self):
        print(f'Your enemy is: {self.name} ({self.level} level)')
        print(f'Health: {self.health}')

    def get_damage(self, attack):
        self.health -= attack

    def died(self):
        print(f'\n{self.name} was killed!')
        print('you get 100 XP')
        self.player.scores += 100

    def enemy_attack(self):
        attack = self.attack - self.player.defence
        self.player.health -= attack
