import os
import pickle
import random
from pathlib import Path
import db
from console import color, print

STATS = "\n1 - endurance\n2 - strength\n3 - agility\n4 - luck\n0 - cancel"

main_folder = Path(__file__).parent


class Player:
    def __init__(self) -> None:
        self.name = None
        self.health = 10
        self.max_hp = 10
        self.attack = 1
        self.defence = 1
        self.endurance = 1  # influences HP
        self.strength = 1  # influences attack
        self.agility = 1  # influences attack + side-roll
        self.luck = 1  # increases rewards and chances to get good loot
        self.level = 1
        self.scores = 0
        self.total_scores = 0
        self.gold = 0
        self.drunk = 0
        self.available_stats_point = 0
        self.next_level = 1000
        self.inventory = []
        self.weapon = None
        self.armor = None

    def enter_name(self) -> None:
        """
        USER ACTION
        Add name to player in the end of game (for high score file)
        """
        if not self.name:
            while True:
                self.name = input('Enter your name: ')
                if len(self.name) > 0:
                    return
                print(color('red', 'Incorrect input'))

    def show_player_info(self) -> None:
        """
        USER ACTION
        Shows all stats of player
        """
        print('\nStatus:')
        print('Name:', self.name)
        print(f'Health: {self.health}/{self.max_hp}')

        # todo: optimize
        if self.weapon:
            unavailable = ''
            if self.drunk < 1:
                unavailable = color('red', ' UNAVAILABLE')
            print(f"Weapon: {self.weapon.name} (attack {self.weapon.attack}){unavailable}")
        if self.armor:
            unavailable = ''
            if self.drunk < 1:
                unavailable = color('red', ' UNAVAILABLE')
            print(f"Armor: {self.armor.name} (defence {self.armor.defence}){unavailable}")

        print('Drunk level:', self.get_condition())
        print('Attack:', self.attack)
        print('Defence:', self.defence)
        print('Endurance:', self.endurance)
        print('Strength:', self.strength)
        print('Agility:', self.agility)
        print('Luck:', self.luck)
        print('Level:', self.level)
        print('Scores:', self.scores, f'(next level {self.next_level})')
        print('Total scores:', self.total_scores)
        print('Gold:', self.gold)

        print('Active quests:')
        with open(Path(main_folder, "quests.pkl"), 'rb') as fd:
            data = pickle.load(fd)
        if not data:
            print('[Empty list]')
        for quest in data:
            print('*', quest.order.name, '-', quest.goal_amount, f'({quest.goal_amount - quest.current_amount} left)')
        if self.available_stats_point:
            self.improve_stats()

    def get_condition(self) -> str:
        """
        Makes "graphic" scale of drinking value
        :return: graphical value of Player.drunk
        """
        drunk = '▇' * (self.drunk // 10) + ' ' * ((100 - self.drunk) // 10)
        return f'[{drunk}] ({self.drunk})'

    def gain_scores(self, scores: int) -> None:
        """
        Gives scores to player and counts current player's level.
        Adds stats points each new level
        """
        old_level = self.level

        self.scores += scores
        self.total_scores += scores
        self.recount_params()
        new_level = self.level
        if difference := new_level - old_level == 1:
            print(color('green', 'NEW LEVEL!'))
            self.available_stats_point += difference

    def set_drunk(self, drunk: int) -> None:
        """
        Set drunk level, counts current player attack and defence
        :param drunk: amount of gained drunk
        """
        self.drunk += drunk
        if self.drunk > 100:
            self.drunk = 100
        elif self.drunk < 0:
            self.drunk = 0
        self.recount_params()

    def improve_stats(self) -> None:
        """
        USER ACTION
        Lets to spend available stats points
        """

        def apply_changes(param: str) -> None:
            attr = getattr(self, param)  # also there is a dirty hack: exec(f'self.{param} += 1')
            setattr(self, param, attr + 1)
            print(f'{param.capitalize()} has been increased! Current value: {getattr(self, param)}')
            self.available_stats_point -= 1
            self.recount_params()

        print('Available stats points:', self.available_stats_point)
        while True:
            answer = answer_handler(
                question='\nDo you want to distribute stats points? (yes/no) ',
                yes=['y', 'yes', '1'],
                no=['n', 'no', '2'])
            if answer[0] == 'no':
                return
            answer2 = answer_handler(
                question='Which one do you want to increase? ',
                yes=['y', 'yes', '1'],
                cancel=['0'])
            if answer[0] == 'cancel':
                return
            if answer2 == '1':
                apply_changes('endurance')
            elif answer2 == '2':
                apply_changes('strength')
            elif answer2 == '3':
                apply_changes('agility')
            elif answer2 == '4':
                apply_changes('luck')

    def recount_params(self) -> None:
        """
        Recounts all player stats after some actions
        """
        self.max_hp = 5 + (self.endurance * 5)
        if self.health > self.max_hp:
            self.health = self.max_hp
        inventory = db.get_inventory()

        # todo: optimize
        weapon = False
        for item in inventory:
            if item[0].used and item[1].type_ == 'weapon':
                self.weapon = item[1]
                weapon = True
                break
        if not weapon:
            self.weapon = None
        armor = False
        for item in inventory:
            if item[0].used and item[1].type_ == 'armor':
                self.armor = item[1]
                armor = True
                break
        if not armor:
            self.armor = None
        self.attack = self.strength + (self.drunk // 10) + (
            (self.weapon.attack if self.weapon else 0) if self.drunk > 0 else 0)
        self.defence = self.strength + (self.drunk // 10) + (
            (self.armor.defence if self.armor else 0) if self.drunk > 0 else 0)

        if self.scores >= self.next_level:
            to_next_level = self.scores - self.next_level
            self.level += 1
            self.scores = to_next_level
            self.next_level = int(self.next_level * 1.2)
            if self.scores > self.next_level:  # todo: for debug
                print(color('red', 'Sanya, look! More than 1 level per time'))
