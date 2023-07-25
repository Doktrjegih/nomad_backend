import datetime
import random

from player import Player
from quest import get_current_quests
from console import color

HUMANS = {1: 'Homeless guy', 2: 'Bandit', 3: 'Knight', 4: 'Berserk'}
DOGS = {1: 'Wet dog', 2: 'Hyena', 3: 'Wolf', 4: 'Werewolf'}
TEST = {1: 'test', 2: 'test1', 3: 'test2', 4: 'test3'}
TEST2 = {1: 'test_', 2: 'test1_', 3: 'test2_', 4: 'test3_'}


class Enemy:
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        self.player = player
        types = [HUMANS, DOGS, TEST, TEST2]
        if exclude:
            for type_ in exclude:
                types.remove(type_)
        self.type = random.choice(types)
        self.name = self.type.get(1)
        self.level = self.get_random_level_of_enemy()
        self.health = 2 * self.level
        # self.strength = 2
        self.attack = 1 * self.level
        self.defence = 1 * self.level
        self.agility = random.randint(0, 2) * self.level

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
        if not quests:
            return
        for quest in quests:
            if quest.order.name == self.name and quest.current_amount < quest.goal_amount:
                quest.increase_goal(quests)

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
        self.player.enter_name()
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
        self.strength = self.level + 3
        self.defence = self.strength + random.randint(0, 3)
        self.attack = self.strength + random.randint(0, 3)


class DrunkEnemy2(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(3)
        self.health = int(self.health * 3)
        self.strength = self.level * 2
        self.defence = self.strength + random.randint(1, 4)
        self.attack = self.strength + random.randint(1, 4)


class Boss(Enemy):
    def __init__(self, player: Player):
        super().__init__(player)

        self.name = self.type.get(4)
        self.health = int(self.health * 5)
        self.strength = self.level * 3
        self.defence = self.strength + random.randint(2, 5)
        self.attack = self.strength + random.randint(2, 5)
