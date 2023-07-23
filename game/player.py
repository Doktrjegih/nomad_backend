import pickle

from console import error, color

STATS = "\n1 - endurance\n2 - strength\n3 - agility\n4 - luck"


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
        self.scores = 960
        self.total_scores = 960
        self.gold = 0
        self.drunk = 0
        self.available_stats_point = 0
        self.next_level = 1000
        self.create_player()

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
        print(f'Health: {self.health}/{self.max_hp}')
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

        print('Active quests: ')
        with open('quests.pkl', 'rb') as fd:
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

    def reward_for_enemy(self, enemy_level: int) -> None:
        """
        Gives reward for killed enemy
        :param enemy_level: enemy level for counting
        """
        reward = 50 * enemy_level
        print(f'You get {reward} XP')
        self.gain_scores(reward)

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
        elif self.drunk < 1:
            self.drunk = 0
        self.recount_params()

    def improve_stats(self):
        """
        USER ACTION
        Lets to spend available stats points
        """
        print('Available stats points:', self.available_stats_point)
        while True:
            answer = input(f'\nDo you want to distribute stats points? (yes/no) ')
            if answer.lower() in ['y', 'yes', '1']:
                print(f'{STATS}')
                answer2 = input(f'Which one do you want to increase? ')
                if answer2 == '1':
                    self.endurance += 1
                    print(f'Endurance has been increased! Current value: {self.endurance}')
                elif answer2 == '2':
                    self.strength += 1
                    print(f'Strength has been increased! Current value: {self.strength}')
                elif answer2 == '3':
                    self.agility += 1
                    print(f'Agility has been increased! Current value: {self.agility}')
                elif answer2 == '4':
                    self.luck += 1
                    print(f'Luck has been increased! Current value: {self.luck}')
                else:
                    error('Incorrect input')
                self.available_stats_point -= 1
                self.recount_params()
                return
            elif answer.lower() in ['n', 'no', '2']:
                return
            else:
                error('Incorrect input')

    def recount_params(self):
        """
        Recount all player stats after some actions
        """
        self.max_hp = 5 + (self.endurance * 5)
        self.attack = self.strength + (self.drunk // 10)
        self.defence = self.strength + (self.drunk // 10)
        if self.scores > self.next_level:
            to_next_level = self.scores - self.next_level
            self.level += 1
            self.scores = to_next_level
            self.next_level = int(self.next_level * 1.2)
            if self.scores > self.next_level:  # todo: for debug
                error(f'Sanya look! More than 1 level per time')
