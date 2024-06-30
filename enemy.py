import datetime
import random
import sys
import db

from console import color, print
from player import Player
from quest import get_current_quests

# todo: try to change to enums
HUMANS = {1: 'Homeless guy', 2: 'Bandit', 3: 'Knight', 4: 'Berserk', 5: 'Madman'}
DOGS = {1: 'Wet dog', 2: 'Hyena', 3: 'Wolf', 4: 'Werewolf', 5: 'Van Helsing'}
TEST = {1: 'test1', 2: 'test2', 3: 'test3', 4: 'test4', 5: 'test5'}


class Enemy:
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        self.player = player
        types = [HUMANS, DOGS, TEST]
        if exclude:
            for type_ in exclude:
                types.remove(type_)
        # self.type = globals()[random.choice(types)]  # todo: maybe go away from entire dicts using this method
        self.type = random.choice(types)
        self.name = self.type.get(1)
        self.level = self.get_random_level_of_enemy()
        self.health = 2 * self.level
        # self.strength = 2
        self.attack = 1 * self.level
        self.defence = 1 * self.level
        self.agility = random.randint(0, 2) * self.level
        self.base_attack = None
        self.launch_specials = lambda: print("No specials")
        self.run_away_able = True
        self.boss = False

    # todo: later need to move all such methods to another class or module
    def hyena(self):
        if self.base_attack:
            self.attack = self.base_attack
        if self.health < 5:
            if random.randint(1, 100) > 25:  # todo: change value
                if not self.base_attack:
                    self.base_attack = self.attack
                self.attack *= 2
                print(f"Special skill has been activated! Enemy attack is {self.attack}")

    # todo: later need to move all such methods to another class or module
    def wolf(self):
        if not hasattr(self, "player_bleeding") or self.player_bleeding == 0:
            if random.randint(1, 100) > 25:  # todo: change value
                self.player_bleeding = 2
                print(f"Special skill has been activated! Player bleeding is {self.player_bleeding}")
        else:
            self.player.health -= 2
            self.player_bleeding -= 1
            print(f"You less 2 HP due to {color('red', 'bleeding')}")

    # todo: later need to move all such methods to another class or module
    def werewolf(self):
        if self.health < 5:
            if not hasattr(self, "healing_activatings"):
                self.healing_activatings = 2
            if self.healing_activatings <= 0:
                return
            self.health += 5
            self.healing_activatings -= 1
            print(f"Special skill has been activated! Enemy health is {self.health}")        

    # todo: later need to move all such methods to another class or module
    def van_helsing(self):
        self.hyena()
        self.wolf()
        self.werewolf()
    
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

    def reward_for_enemy(self) -> None:
        """
        Gives reward for killed enemy
        :param enemy: object of Enemy class
        """
        if self.player.drunk > 0:
            reward = round((total := 50 * self.level) + total * random.uniform(0.03, 0.1))
            print(f'You get {reward} XP')
            self.player.gain_scores(reward)
        if self.boss:
            db.add_item_to_inventory((unique_item := db.get_item_by_name(self.name)).item_id)
            print(f"You get {color('yellow', unique_item.name)}!")
    
    def died(self) -> None:
        """
        Kills enemy, gets XP, checks if enemy was a quest goal
        """
        print(f'\n{color("red", self.name)} was killed!')
        self.reward_for_enemy()
        quests = get_current_quests()
        if not quests:
            return
        for quest in quests:
            if quest.order.name == self.name and quest.current_amount < quest.goal_amount:
                xp = 100 * self.level if self.player.drunk > 0 else 0
                quest.update_quest(quests, xp)

    @staticmethod
    def check_specials(func):
        def wrapper(self, *args, **kwargs):
            self.get_specials()
            self.launch_specials()
            func(self, *args, **kwargs)
        return wrapper

    @check_specials
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

    def get_specials(self):
        # todo: doc
        if self.type == DOGS:
            if self.name == 'Hyena':
                self.launch_specials = self.hyena
            if self.name == 'Wolf':
                self.launch_specials = self.wolf
            if self.name == 'Werewolf':
                self.launch_specials = self.werewolf
            if self.name == 'Van Helsing':
                self.launch_specials = self.van_helsing
    
    def game_over(self) -> None:
        """
        Finishes the game and writes Player.total_scores to file with datetime
        """
        print('Your HP is 0')
        print('GAME OVER!')
        print('Total scores =', self.player.scores)
        self.player.enter_name()
        input('Click Enter to exit...')
        with open('high_scores.txt', 'a', encoding='utf-8') as fd:
            fd.write(f'{self.player.name} - {self.player.scores} '
                     f'({datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        sys.exit(0)


class DrunkEnemy1(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(2)
        self.health = int(self.health * 2)
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


class DrunkEnemy3(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(4)
        self.health = int(self.health * 4)
        self.strength = self.level * 2 + 5
        self.defence = self.strength + random.randint(1, 5)
        self.attack = self.strength + random.randint(1, 5)


class Boss(Enemy):
    def __init__(self, player: Player, exclude: list[dict] = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(5)
        self.health = int(self.health * 5)
        self.strength = self.level * 3
        self.defence = self.strength + random.randint(2, 6)
        self.attack = self.strength + random.randint(2, 6)
        self.boss = True


def generate_enemy(player: Player) -> Enemy | DrunkEnemy1 | DrunkEnemy2 | Boss:
    """
    Generates enemy according to current player drunk state
    :param player: object of Player class
    :return: object of Enemy class
    """
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
    elif drunk_level < 100:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return DrunkEnemy1(player)
        elif rand > 70:
            return DrunkEnemy2(player)
        return DrunkEnemy3(player)
    else:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return DrunkEnemy1(player)
        elif rand > 70:
            return DrunkEnemy2(player)
        elif rand > 5:
            return DrunkEnemy3(player)
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
