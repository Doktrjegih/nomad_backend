import datetime
import random

from player import Player
from quest import get_current_quests
from console import color

HUMANS = {1: 'Homeless guy', 2: 'Bandit', 3: 'Knight', 4: 'Berserk'}
DOGS = {1: 'Wet dog', 2: 'Hyena', 3: 'Wolf', 4: 'Werewolf'}
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
        level = self.player.level + random.randint(-2, 1)
        if level < 1:
            return 1
        return level

    def show_rivals_stats(self) -> None:
        """
        Shows status of enemy and player
        """
        print(f'Your enemy is: {color("red", self.name)} ({self.level} level)')
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
        print(f'\n{color("red", self.name)} was killed!')
        self.player.reward_for_enemy(self.level)
        quests = get_current_quests()
        if quests:
            if quests[0].order.name == self.name and quests[0].current_amount < quests[0].goal_amount:
                quests[0].increase_goal()

    def enemy_attack(self) -> int:
        """
        Enemy's part of turn, damages the player, finishes the game if player's HP is 0
        :return: int level of damage to player
        """
        print(f'{self.name} attacks!')
        attack = self.attack - self.player.defence
        if attack < 1:
            attack = 0
        self.player.health -= attack
        if self.player.health <= 0:
            self.game_over()
        return attack

    def game_over(self) -> None:
        """
        Finishes the game and writes Player.total_scores to file with datetime
        """
        print('Your HP is 0')
        print('GAME OVER!')
        print('Total score =', self.player.scores)
        input('Click Enter to exit...')
        with open('high_scores.txt', 'a', encoding='utf-8') as fd:
            fd.write(f'{self.player.name} - {self.player.scores} '
                     f'({datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        exit()


class DrunkEnemy1(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(2)
        self.health = int(self.health * 1.5)


class DrunkEnemy2(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(3)
        self.health = int(self.health * 3)


class Boss(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(4)
        self.health = int(self.health * 5)
