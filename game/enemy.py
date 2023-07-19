import random

from player import Player
from quest import get_current_quests


class Enemy:
    def __init__(self, player: Player) -> None:
        self.player = player

        self.name = 'Anthon'
        self.level = self.get_random_level_of_enemy()
        self.health = 2 * self.level
        self.attack = 1 * self.level
        self.strength = 2
        self.agility = 2
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
        print('you get 100 XP')
        self.player.scores += 100
        quests = get_current_quests()
        if quests:
            if quests[0].order.name == self.name:
                quests[0].increase_goal()

    def enemy_attack(self) -> None:
        """
        Enemy's part of turn, damages the player, finishes the game if player's HP is 0
        """
        print(f'{self.name} attacks!')
        attack = self.attack - self.player.defence
        if attack < 1:
            attack = 1
        self.player.health -= attack
        if self.player.health <= 0:
            print('your HP is 0')
            print('GAME OVER!')
            exit()
        print(f'your HP is {self.player.health}')
