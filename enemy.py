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
DEFAULT_PARAMS = {"stage": 1, "hp_factor": 1, "attack" : 1, "defence": 1}
STAGE_2 = {"stage": 2, "hp_factor": 2, "attack" : 2, "defence": 2}
STAGE_3 = {"stage": 3, "hp_factor": 3, "attack" : 3, "defence": 3}
STAGE_4 = {"stage": 4, "hp_factor": 4, "attack" : 4, "defence": 4}


class Enemy:
    def __init__(self, player: Player, exclude: list[dict] | None = None, params: dict = DEFAULT_PARAMS) -> None:
        self.player = player
        types = [HUMANS, DOGS, TEST]
        if exclude:
            for type_ in exclude:
                types.remove(type_)
        self.type = random.choice(types)
        self.name = self.type.get(params.get("stage"))
        self.level = self.get_random_level_of_enemy()
        self.health = 2 * params.get("hp_factor") * self.level
        # self.strength = 2
        self.attack = params.get("attack") * self.level
        self.defence = params.get("defence") * self.level
        self.agility = random.randint(0, 2) * self.level
        self.base_attack = None
        self.launch_specials = lambda: print("No specials")
        self.run_away_able = True
        self.boss = False
        self.effects_damage = None
        self.effects_vulnerability = self.get_vulnerability(self.name)

    def get_vulnerability(self, name):
        if name == "Wet dog":
            return "fire"
    
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


class Boss(Enemy):
    def __init__(self, player: Player, exclude: list[dict] | None = None) -> None:
        super().__init__(player, exclude)

        self.name = self.type.get(5)
        self.health = int(self.health * 5)
        self.strength = self.level * 3
        self.defence = self.strength + random.randint(2, 6)
        self.attack = self.strength + random.randint(2, 6)
        self.boss = True


def generate_enemy(player: Player) -> Enemy:
    """
    Generates enemy according to current player drunk state
    :param player: object of Player class
    :return: object of Enemy class
    """
    rand = random.randint(1, 100)
    if player.drunk < 26:
        return Enemy(player)
    elif player.drunk < 51:
        if rand > 90:
            return Enemy(player)
        return Enemy(player, params=STAGE_2)
    elif player.drunk < 76:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return Enemy(player, params=STAGE_2)
        return Enemy(player, params=STAGE_3)
    else:
        if rand > 90:
            return Enemy(player)
        elif rand > 80:
            return Enemy(player, params=STAGE_2)
        elif rand > 70:
            return Enemy(player, params=STAGE_3)
        return Enemy(player, params=STAGE_4)


def enemy_for_npc_quest(player: Player, exclude: list[dict] | None = None) -> Enemy:
    """
    Generates enemy for NPC quest according to current player drunk state
    :param player: object of Player class
    :param exclude: used for exclude already taken player's quests targets
    :return: object of enemy depends on its stage
    """
    if 51 > player.drunk > 24:
        return Enemy(player, params=STAGE_2, exclude=exclude)
    elif 76 > player.drunk > 50:
        return Enemy(player, params=STAGE_3, exclude=exclude)
    elif player.drunk > 75:
        return Enemy(player, params=STAGE_4, exclude=exclude)
    else:
        raise ValueError("Can't generate enemies with low drunk level")
