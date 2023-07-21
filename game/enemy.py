import random

from player import Player
from quest import get_current_quests

HUMANS = {1: 'homeless guy', 2: 'bandit'}
DOGS = {1: 'wet dog', 2: 'Anthon'}
TYPES = [HUMANS, DOGS]


class Enemy:
    def __init__(self, player: Player) -> None:
        self.player = player

        self.type = random.choice(TYPES)
        self.name = self.type.get(1)
        self.level = self.get_random_level_of_enemy()
        self.health = 2 * self.level
        self.attack = 1 * self.level
        self.strength = 2
        self.agility = random.randint(0, 2)
        self.defence = 1 * self.level

    def get_random_level_of_enemy(self) -> int:
        """
        Generates random level close to player, but not less than 1
        :return: int level of enemy
        """
        level = self.player.level + random.randint(-2, 2)
        if level < 1:
            return 1
        return level

    def show_rivals_stats(self) -> None:
        """
        Shows status of enemy and player
        """
        print(f'Your enemy is: {self.name} ({self.level} level)')
        print(f'Your health: {self.player.health}')
        print(f'Enemy health: {self.health}')

    def get_damage(self, attack) -> None:
        """
        Reduces enemy's HP
        :param attack: int value of getting damage
        """
        self.health -= attack

    def died(self) -> None:
        """
        Kills enemy, gets XP, checks if enemy was a quest goal
        """
        print(f'\n{self.name} was killed!')
        self.player.award_for_enemy()
        quests = get_current_quests()
        if quests:
            if quests[0].order.name == self.name and quests[0].current_amount < quests[0].goal_amount:
                quests[0].increase_goal()

    def enemy_attack(self) -> None:
        """
        Enemy's part of turn, damages the player, finishes the game if player's HP is 0
        """
        print(f'{self.name} attacks!')
        attack = self.attack - self.player.defence
        if attack < 1:
            attack = 0
        self.player.health -= attack
        if self.player.health <= 0:
            print('your HP is 0')
            print('GAME OVER!')
            print('total score =', self.player.scores)
            input('click Enter to exit...')
            exit()
        print(f'your HP is {self.player.health}')


class DrunkEnemy1(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(2)
        self.health = int(self.health * 1.5)
