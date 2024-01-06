import datetime
import random

from console import color, print
from player import Player
from quest import get_current_quests

HUMANS = {1: 'Homeless guy', 2: 'Bandit', 3: 'Knight', 4: 'Berserk'}
DOGS = {1: 'Wet dog', 2: 'Hyena', 3: 'Wolf', 4: 'Werewolf'}
TEST = {1: 'test1', 2: 'test2', 3: 'test3', 4: 'test4'}


class ExitException(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class Enemy:
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        self.player = player
        types = [HUMANS, DOGS, TEST]
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
        self.player.reward_for_enemy(self)
        quests = get_current_quests()
        if not quests:
            return
        for quest in quests:
            if quest.order.name == self.name and quest.current_amount < quest.goal_amount:
                xp = 100 * self.level if self.player.drunk > 0 else 0
                quest.update_quest(quests, xp)

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
        self.player.recount_params()
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
        raise ExitException()


class DrunkEnemy1(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(2)
        self.health = int(self.health * 1.5)
        self.strength = self.level + 3
        self.defence = self.strength + random.randint(0, 3)
        self.attack = self.strength + random.randint(0, 3)


class DrunkEnemy2(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(3)
        self.health = int(self.health * 3)
        self.strength = self.level * 2
        self.defence = self.strength + random.randint(1, 4)
        self.attack = self.strength + random.randint(1, 4)


class Boss(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(4)
        self.health = int(self.health * 5)
        self.strength = self.level * 3
        self.defence = self.strength + random.randint(2, 5)
        self.attack = self.strength + random.randint(2, 5)


# todo: shitcode
def generate_enemy(player: Player) -> Enemy | DrunkEnemy1 | DrunkEnemy2 | Boss:
    """
    Generates enemy according to current player drunk state
    :param player: object of Player class
    :return: object of Enemy class
    """
    # detect an enemy (first version)
    # if player.drunk < 26:
    #     enemy = Enemy(player)
    # elif 51 > player.drunk > 25:
    #     if random.randint(1, 100) > 80:
    #         enemy = DrunkEnemy1(player)
    #     else:
    #         enemy = Enemy(player)
    # elif 76 > player.drunk > 50:
    #     if random.randint(1, 100) > 90:
    #         enemy = DrunkEnemy2(player)
    #     elif 91 > random.randint(1, 100) > 60:
    #         enemy = DrunkEnemy1(player)
    #     else:
    #         enemy = Enemy(player)
    # else:
    #     if random.randint(1, 100) > 95:
    #         print('Prepare your anus, puppy')
    #         enemy = Boss(player)
    #     elif 96 > random.randint(1, 100) > 80:
    #         enemy = DrunkEnemy2(player)
    #     elif 81 > random.randint(1, 100) > 55:
    #         enemy = DrunkEnemy1(player)
    #     else:
    #         enemy = Enemy(player)

    # detect an enemy (second version)
    drunk_level = player.drunk
    rand = random.randint(1, 100)

    if drunk_level < 26:
        return Enemy(player)
    elif drunk_level < 51:
        if rand > 90:
            return Enemy(player)
        return DrunkEnemy1(player)
    elif drunk_level < 76:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return DrunkEnemy1(player)
        return DrunkEnemy2(player)
    else:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return DrunkEnemy1(player)
        elif rand > 70:
            return DrunkEnemy2(player)
        return Boss(player)


def enemy_for_npc_quest(player: Player, exclude: list[dict] = None) -> DrunkEnemy1 | DrunkEnemy2 | Boss:
    """
    Generates enemy for NPC quest according to current player drunk state
    :param player: object of Player class
    :param exclude: used for exclude already taken player's quests targets
    :return: object of enemy depends on its stage
    """
    if 51 > player.drunk > 24:
        enemy = DrunkEnemy1(player, exclude=exclude)
    elif 76 > player.drunk > 50:
        enemy = DrunkEnemy2(player, exclude=exclude)
    elif player.drunk > 75:
        enemy = Boss(player, exclude=exclude)
    return enemy
