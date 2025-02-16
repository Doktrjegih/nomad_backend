import random
import sys
from json import loads
from paths import ENEMIES

import db
from console import color, print, get_effect_color
from player import Player
from quest import get_current_quests

# todo: try to change to enums
HUMANS = {1: 'Homeless guy', 2: 'Bandit', 3: 'Knight', 4: 'Berserk', 5: 'Madman'}
DOGS = {1: 'Wet dog', 2: 'Hyena', 3: 'Wolf', 4: 'Werewolf', 5: 'Van Helsing'}
TEST = {1: 'test1', 2: 'test2', 3: 'test3', 4: 'test4', 5: 'test5'}

DEFAULT_PARAMS = {"stage": 1, "hp_factor": 1, "attack": 1, "defence": 1}
STAGE_2 = {"stage": 2, "hp_factor": 2, "attack": 2, "defence": 2}
STAGE_3 = {"stage": 3, "hp_factor": 3, "attack": 3, "defence": 3}
STAGE_4 = {"stage": 4, "hp_factor": 4, "attack": 4, "defence": 4}


class Enemy:
    # todo: remove stupid dict types at all
    def __init__(self, player: Player,
                 random_enemy: bool = True,
                 name: str = "",
                 exclude: list[str] | None = None,
                 params: dict = DEFAULT_PARAMS) -> None:
        self.player = player
        if random_enemy:
            while True:
                type_ = random.choice([HUMANS, DOGS, TEST])
                self.name = type_.get(params.get("stage"))
                if exclude and self.name in exclude:
                    continue
                else:
                    break
        else:
            self.name = name
        self.health = 2 * params.get("hp_factor")  # todo: use smth instead of lvl
        self.attack = params.get("attack")  # todo: use smth instead of lvl
        self.defence = params.get("defence")  # todo: use smth instead of lvl
        self.agility = random.randint(0, 2)  # todo: use smth instead of lvl
        self.base_attack = None
        self.launch_specials = lambda: print("No specials")
        self.run_away_able = True
        self.boss = False
        self.effects_damage = self.get_effects_param(self.name, "effects_damage")
        self.effects_vulnerabilities = self.get_effects_param(self.name, "vulnerabilities")
        self.effects_resist = self.get_effects_param(self.name, "resist")

    @staticmethod
    def get_effects_param(name: str, param: str) -> list:
        """
        Retrieves specified effect-related data for a given enemy name
        :param name: name of the enemy to look up.
        :param param: parameter (e.g., effects_damage, vulnerabilities) to fetch
        :return: list of the specified parameter values for the enemy
        """
        with open(ENEMIES, "r", encoding="utf-8") as fd:
            enemies = loads(fd.read())
        for enemy in enemies:
            if enemy.get("name") == name:
                return enemy.get(param)

    # todo: later need to move all such methods to another class or module
    # ========== enemies' special methods start here ==========
    def hyena(self) -> None:
        """
        Doubles the attack power when the health is below specific value
        """
        if self.base_attack:
            self.attack = self.base_attack
        if self.health < 5:
            if random.randint(1, 100) > 25:  # todo: change value
                if not self.base_attack:
                    self.base_attack = self.attack
                self.attack *= 2
                print(f"Special skill has been activated! Enemy attack is {self.attack}")

    def wolf(self) -> None:
        """
        Causes bleeding effect to the player
        """
        if not hasattr(self, "player_bleeding") or self.player_bleeding == 0:
            if random.randint(1, 100) > 25:  # todo: change value
                self.player_bleeding = 2
                print(f"Special skill has been activated! Player bleeding is {self.player_bleeding}")
        else:
            self.player.health -= 2
            self.player_bleeding -= 1
            print(f"You less 2 HP due to {color('red', 'bleeding')}")

    def werewolf(self) -> None:
        """
        Heals the enemy's health by when it drops below specific value
        """
        if self.health < 5:
            if not hasattr(self, "healing_activatings"):
                self.healing_activatings = 2
            if self.healing_activatings <= 0:
                return
            self.health += 5
            self.healing_activatings -= 1
            print(f"Special skill has been activated! Enemy health is {self.health}")

    def van_helsing(self) -> None:
        """
        Activates a combination of 'Hyena', 'Wolf', and 'Werewolf' abilities
        """
        self.hyena()
        self.wolf()
        self.werewolf()
    # ========== enemies' special methods end here ==========

    def show_rivals_stats(self) -> None:
        """
        Shows status of enemy and player
        """
        print(f'Your enemy is: {color("red", self.name)}')
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
        def drop_rate():
            rand = random.randint(1, 100)
            if rand > 90:
                return 3
            elif rand > 70:
                return 2
            else:
                return 1

        if self.name not in list(DOGS.values()):  # todo: make expendable
            reward = random.randint(3, 10)
            print(f'You get {reward} gold coins')
        if (items := db.get_enemy_loot(self.name)) and random.randint(1, 10) > 3:
            db.add_item_to_inventory((item := random.choice(items)).item_id, amount=(pieces := drop_rate()))
            print(f"You get {color('yellow', item.name)} ({pieces})")
        if self.boss:
            db.add_item_to_inventory((unique_item := db.get_item_by_name(self.name)).item_id)
            print(f"You get {color('yellow', unique_item.name)}!")

    def died(self) -> None:
        """
        Kills enemy, checks if enemy was a quest goal
        """
        if self.boss and self.name == "Aleg":
            self.good_ending()
        print(f'\n{color("red", self.name)} was killed!')
        self.reward_for_enemy()
        quests = get_current_quests()
        if not quests:
            return
        for quest in quests:
            if quest.order.name == self.name and quest.current_amount < quest.goal_amount:
                quest.update_quest(quests)

    @staticmethod
    def check_specials(func: callable) -> callable:
        """
        A decorator for applying specials before enemy's attack
        :param: the function to be decorated
        :return: The wrapped function after applying pre-execution of specials
        """
        def wrapper(self, *args: tuple, **kwargs: dict) -> None:
            self.get_specials()
            self.launch_specials()
            func(self, *args, **kwargs)
        return wrapper

    @check_specials
    def enemy_attack(self) -> int:
        """
        Enemy's part of turn, damages the player, finishes the game if player's HP is 0
        :return: int damage to player
        """
        print(f'{self.name} attacks!')
        attack = self.attack - self.player.defence
        attack += self.count_effect_damage()
        if attack < 1:
            attack = 0
        self.player.health -= attack
        self.player.recount_params()
        if self.player.health <= 0:
            if self.boss and self.name == "Aleg":
                if self.player.aleg_drinks > 3:
                    self.bad_ending_false()
                else:
                    self.bad_ending_true()
            self.game_over()
        return attack

    def count_effect_damage(self) -> int:
        if not self.effects_damage:
            return 0
        total_value = 0
        for effect_damage in self.effects_damage:
            value = effect_damage.get('value')
            effect_name = effect_damage.get('name')

            if not self.player.armor or self.player.armor.effects == "null":
                pass
            else:
                for armor_effect in loads(self.player.armor.effects):
                    if armor_effect.get('name') == effect_name:
                        if not (resist := armor_effect.get('resist')):
                            continue
                        diff = value if resist > value else resist
                        value -= resist
                        print(f"{self.player.armor.name} absorb {diff} damage from {get_effect_color(effect_name)}")

            if value <= 0:
                continue
            total_value += value
            print(f"You get {value} damage from {get_effect_color(effect_name)}")
        return total_value

    def get_specials(self) -> None:
        """
        Assigns special abilities to enemies based on their name
        """
        if self.name == 'Hyena':
            self.launch_specials = self.hyena
        if self.name == 'Wolf':
            self.launch_specials = self.wolf
        if self.name == 'Werewolf':
            self.launch_specials = self.werewolf
        if self.name == 'Van Helsing':
            self.launch_specials = self.van_helsing

    def good_ending(self) -> None:
        """
        Finishes the game if player has drunk with Aleg less or equal to 3 times and won
        """
        print(f"You defeated {color('red', self.name)}!")
        print("(add text) Everyone is happy! You win! :)")
        sys.exit(0)

    def bad_ending_true(self) -> None:
        """
        Finishes the game if player has drunk with Aleg less or equal to 3 times,
        but lost the last fight
        """
        print(f"You've been defeated by {color('red', self.name)}...")
        print("(add text) Everyone is sad! You lose! :(")
        sys.exit(0)

    def bad_ending_false(self) -> None:
        """
        Finishes the game if player has drunk with Aleg MORE than 3 times
        """
        print(f"You've been defeated by {color('red', self.name)}...")
        print("(add text) Your soul has been absorbed by Aleg")
        sys.exit(0)

    def game_over(self) -> None:
        """
        Finishes the game
        """
        print('Your HP is 0\nGAME OVER!')
        sys.exit(0)


class Boss(Enemy):
    def __init__(self, player: Player, name: str) -> None:
        super().__init__(player=player, random_enemy=False)

        self.name = name
        self.health = int(self.health * 5)
        self.defence = random.randint(2, 6) * 3
        self.attack = random.randint(2, 6) * 3
        self.boss = True


def generate_enemy(player: Player) -> Enemy:
    """
    Generates enemy according to current player drunk state
    :param player: object of Player class
    :return: object of Enemy class
    """
    rand = random.randint(1, 100)
    for quest in get_current_quests():
        if quest.order.boss and rand > 75:
            if quest.order.name == "Some shit":
                return Boss(player, name="Aleg")
            else:
                return Boss(player, name=quest.order.name)
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


def enemy_for_npc_quest(player: Player, exclude: list[str] | None = None) -> Enemy:
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
