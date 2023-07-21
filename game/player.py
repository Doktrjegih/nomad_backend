import pickle


class Player:
    def __init__(self) -> None:
        self.name = None  # todo: fix bug with empty name
        self.health = 10
        self.attack = 1
        self.defence = 1
        self.endurance = 1  # influences HP
        self.strength = 1  # influences attack
        self.agility = 1  # influences attack + side-roll
        self.luck = 1  # increases rewards and chances to get good loot
        self.level = 1
        self.scores = 0
        self.gold = 20
        self.drunk = 0
        self.create_player()

    def create_player(self) -> None:
        """
        USER ACTION
        Add name to player in the beginning of game
        """
        self.name = input('Enter your name: ')
        print(self.name)

    def show_player_info(self) -> None:
        """
        USER ACTION
        Shows all stats of player
        """
        print('\nStatus:')
        print('name =', self.name)
        print('health =', self.health)
        print('drunk level =', self.get_condition(), f'({self.drunk})')
        print('attack =', self.attack)  # todo: 12 attack with 10 drunk (refactor the counter of stats)
        print('defence =', self.defence)
        print('strength =', self.strength)
        print('agility =', self.agility)
        print('luck =', self.luck)
        print('level =', self.level)
        print('scores =', self.scores)
        print('gold =', self.gold)

        print('active quests: ')
        with open('quests.pkl', 'rb') as fd:
            data = pickle.load(fd)
        if not data:
            print('[empty list]')
        for quest in data:
            print('*', quest.order.name, '-', quest.goal_amount, f'({quest.goal_amount - quest.current_amount} left)')

    def get_condition(self) -> str:
        """
        Makes "graphic" scale of drinking value
        :return: graphical value of Player.drunk
        """
        drunk = '▇' * self.drunk + ' ' * (10 - self.drunk)
        return f'[{drunk}]'

    def award_for_enemy(self) -> None:
        """
        Gives award and counts current player's level
        """
        print('you get 100 XP and 5 gold coins')
        self.scores += 100
        self.level = 1 + (self.scores // 500)
        self.gold += 5
        if self.drunk > 0:
            self.drunk -= 1
