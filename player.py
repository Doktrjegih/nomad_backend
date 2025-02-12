import pickle

import db
from console import color, print, answer_handler
from paths import QUESTS

STATS = "\n1 - endurance\n2 - strength\n3 - agility\n4 - luck\n0 - cancel"


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
        self.gold = 0
        self.drunk = 0
        self.inventory = []
        self.weapon = None
        self.armor = None
        self.plot_stage = 1

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
        print('Gold coins:', self.gold)

        print('Active quests:')
        with open(QUESTS, 'rb') as fd:
            data = pickle.load(fd)
        if not data:
            print('[Empty list]')
        is_plot = ""
        for quest in data:
            if quest.plot_quest:
                is_plot = " [Plot quest]"
            print('*', quest.order.name, '-', quest.goal_amount, f'({quest.goal_amount - quest.current_amount} left){is_plot}')

    def get_condition(self) -> str:
        """
        Makes "graphic" scale of drinking value
        :return: graphical value of Player.drunk
        """
        drunk = '▇' * (self.drunk // 10) + ' ' * ((100 - self.drunk) // 10)
        return f'[{drunk}] ({self.drunk})'

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

    def improve_stats(self) -> None:  # todo: add to dialog w/ Aleg
        """
        USER ACTION
        Lets to spend available stats points
        """

        def apply_changes(param: str) -> None:
            attr = getattr(self, param)  # also there is a dirty hack: exec(f'self.{param} += 1')
            setattr(self, param, attr + 1)
            print(f'{param.capitalize()} has been increased! Current value: {getattr(self, param)}')
            self.recount_params()

        answer = answer_handler(
            question='Do you want to distribute stats points? (yes/no) ',
            yes=['y', 'yes', '1'],
            no=['n', 'no', '2'])
        if answer[0] == 'no':
            return
        print(STATS)
        answer2 = answer_handler(
            question=f'Which one do you want to increase? ',
            skills=['1', '2', '3', '4'],
            cancel=['0'])
        if answer2[0] == 'cancel':
            return
        if answer2[1] == '1':
            apply_changes('endurance')
        elif answer2[1] == '2':
            apply_changes('strength')
        elif answer2[1] == '3':
            apply_changes('agility')
        elif answer2[1] == '4':
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
