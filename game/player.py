import pickle


class Player:
    def __init__(self) -> None:
        self.name = None
        self.health = 10
        self.attack = 3
        self.defence = 0
        self.strength = 5
        self.agility = 0
        self.luck = 0
        self.level = 1
        self.scores = 0
        self.gold = 20
        self.drunk = 0
        self.create_player()

    def create_player(self) -> None:
        self.name = input('Enter your name: ')
        print(self.name)

    def show_player_info(self) -> None:
        print('\nStatus:')
        print('name =', self.name)
        print('health =', self.health)
        print('drunk level =', self.get_condition(), f'({self.drunk})')
        print('attack =', self.attack)
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
        drunk = '▇' * self.drunk + ' ' * (10 - self.drunk)
        return f'[{drunk}]'
