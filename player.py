class Player:
    def __init__(self):
        self.name = None
        self.health = 10
        self.attack = 3
        self.defence = 0
        self.level = 1
        self.scores = 0
        self.gold = 0
        self.create_player()

    def create_player(self):
        self.name = input('Enter your name: ')
        print(self.name)

    def show_player_info(self):
        print('\nStatus:')
        print('name =', self.name)
        print('health =', self.health)
        print('attack =', self.attack)
        print('defence =', self.defence)
        print('scores =', self.scores)
        print('gold =', self.gold)
