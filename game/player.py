import pickle

from console import error


class Player:
    def __init__(self) -> None:
        self.name = None
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
        self.available_stats_point = 0

    def create_player(self) -> None:
        """
        USER ACTION
        Add name to player in the beginning of game
        """
        while True:
            self.name = input('Enter your name: ')
            if len(self.name) > 1:
                return
            error('Incorrect input')

    def show_player_info(self) -> None:
        """
        USER ACTION
        Shows all stats of player
        """
        print('\nStatus:')
        print('Name:', self.name)
        print('Health:', self.health)
        print('Drunk level:', self.get_condition())
        print('Attack:', self.attack)
        print('Defence:', self.defence)
        print('Endurance:', self.endurance)
        print('Strength:', self.strength)
        print('Agility:', self.agility)
        print('Luck:', self.luck)
        print('Level:', self.level)
        print('Scores:', self.scores)
        print('Gold:', self.gold)

        print('Active quests: ')
        with open('quests.pkl', 'rb') as fd:
            data = pickle.load(fd)
        if not data:
            print('[Empty list]')
        for quest in data:
            print('*', quest.order.name, '-', quest.goal_amount, f'({quest.goal_amount - quest.current_amount} left)')

        print('Available stats points:', self.available_stats_point)

    def get_condition(self) -> str:
        """
        Makes "graphic" scale of drinking value
        :return: graphical value of Player.drunk
        """
        drunk = '▇' * (self.drunk // 10) + ' ' * ((100 - self.drunk) // 10)
        return f'[{drunk}] ({self.drunk})'

    def reward_for_enemy(self) -> None:
        """
        Gives reward and counts current player's level
        """
        print('You get 100 XP and 5 gold coins')
        self.gain_scores(100)
        self.gold += 5

    def gain_scores(self, scores: int) -> None:
        """
        Gives reward and counts current player's level
        """
        old_level = self.level
        self.scores += scores
        self.level = 1 + (self.scores // 1000)
        new_level = self.level
        if difference := new_level - old_level > 0:
            self.available_stats_point += difference
