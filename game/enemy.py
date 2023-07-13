from player import Player


class Enemy:
    def __init__(self, player: Player) -> None:
        self.player = player

        self.name = 'Anthon'
        self.health = 3
        self.attack = 2
        self.strength = 2
        self.agility = 2
        self.defence = 1
        self.level = self.player.level

    def show_enemy_stats(self) -> None:
        print(f'Your enemy is: {self.name} ({self.level} level)')
        print(f'Your health: {self.player.health}')
        print(f'Enemy health: {self.health}')

    def get_damage(self, attack) -> None:
        self.health -= attack

    def died(self) -> None:
        print(f'\n{self.name} was killed!')
        print('you get 100 XP')
        self.player.scores += 100

    def enemy_attack(self) -> None:
        print(f'{self.name} attacks!')
        attack = self.attack - self.player.defence
        self.player.health -= attack
        if self.player.health <= 0:
            print('your HP is 0')
            print('GAME OVER!')
            exit()
        print(f'your HP is {self.player.health}')
