import pickle

import db
from console import print, answer_handler
from paths import QUESTS

STATS = ("\n1 - beer (endurance)\n"
          "2 - vodka (strength)\n"
          "3 - whiskey (agility)\n"
          "4 - rum (luck)\n"
          "0 - cancel")


class Player:
    _instance = None

    def __new__(cls):
        """
        Implementing a Singleton pattern.
        This method allows to return already created instance of the class
        if it exists, otherwise create a new one
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self.name = None
            self.health = 10
            self.max_hp = 10
            self.attack = 1
            self.defence = 1
            self.endurance = 1  # influences HP
            self.strength = 1  # influences attack
            self.agility = 1  # influences attack + side-roll (currently is not used?)
            self.luck = 1  # increases rewards and chances to get good loot
            self.gold = 10
            self.drunk = 0
            self.weapon = None
            self.armor = None
            self.plot_stage = 1
            self.aleg_drinks = 0
            self._initialized = True

    @classmethod
    def reset(cls):
        cls._instance = None

    def show_player_info(self) -> None:
        """
        USER ACTION
        Shows all stats of player
        """
        print('\nStatus:')
        print('Name:', self.name)
        print(f'Health: {self.health}/{self.max_hp}')

        if self.weapon:
            print(self.weapon)
        if self.armor:
            print(self.armor)

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
            print('*', quest.order, '-', quest.goal_amount, f'({quest.goal_amount - quest.current_amount} left){is_plot}')
            is_plot = ""

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

    def improve_stats(self) -> None:
        """
        USER ACTION
        Lets to spend available stats points
        """

        def apply_changes(param: str) -> None:
            attr = getattr(self, param)  # also there is a dirty hack: exec(f'self.{param} += 1')
            setattr(self, param, attr + 1)
            print(f"{param.capitalize()} has been increased! Current value: {getattr(self, param)}\n")
            self.aleg_drinks += 1
            self.recount_params()

        answer = answer_handler(
            question="Wanna drink with me? (yes/no) ",
            yes=["y", "yes", "1"],
            no=["n", "no", "2"])
        if answer[0] == "no":
            print("As you wish...\n")
            return
        print(STATS)
        answer2 = answer_handler(
            question="What do you want to drink? (0 for cancel) ",
            skills=["1", "2", "3", "4"],
            cancel=["0"])
        if answer2[0] == "cancel":
            print("As you wish...\n")
            return
        if answer2[1] == "1":
            apply_changes("endurance")
        elif answer2[1] == "2":
            apply_changes("strength")
        elif answer2[1] == "3":
            apply_changes("agility")
        elif answer2[1] == "4":
            apply_changes("luck")

    def recount_params(self) -> None:
        """
        Recounts all player stats after some actions
        """
        self.max_hp = 5 + (self.endurance * 5)
        self.health = min(self.health, self.max_hp)
        inventory = db.get_inventory()

        self.weapon, self.armor = None, None
        for item in inventory:
            if item[0].used and (type_ := item[1].type_) in ['weapon', 'armor']:
                from items import Equipment
                if type_ == 'weapon':
                    self.weapon = Equipment(item[1], self.drunk)
                else:
                    self.armor = Equipment(item[1], self.drunk)

        self.attack = self.strength + (self.drunk // 10) + (self.weapon.attack if self.weapon else 0)
        self.defence = self.strength + (self.drunk // 10) + (self.armor.defence if self.armor else 0)
