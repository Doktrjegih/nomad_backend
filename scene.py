import random

from enemy import Enemy
from location import Location
from player import Player


class Scene:
    def __init__(self, location: Location, player: Player):
        self.location = location
        self.player = player
        self.state = 'peace'
        self.enemy = None

    def show_current_scene(self):
        if self.state == 'battle':
            self.show_battle_scene()
        elif self.state == 'peace':
            self.show_peace_scene()

    def show_peace_scene(self):
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        action = self.show_possible_options()
        if action == 1:
            self._new_scene()
        elif action == 2:
            self.player.show_player_info()
            self.show_current_scene()
        elif action == 3:
            exit()

    def show_battle_scene(self):
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        print('WARNING! Battle mode')
        self.enemy.show_enemy_stats()
        action = self.show_possible_options()
        if action == 1:
            attack = self.player.attack - self.enemy.defence
            print(f'your attack is {attack}')
            self.enemy.get_damage(attack)
            if self.enemy.health <= 0:
                self.enemy.died()
                self.enemy = None
                self.state = 'peace'
                self.show_current_scene()
            else:
                self.enemy.enemy_attack()
                self.show_battle_scene()
        elif action == 2:
            pass
        elif action == 3:
            self.player.show_player_info()
            self.show_current_scene()
        elif action == 4:
            exit()

    def show_possible_options(self):
        options = []
        if self.state == 'battle':
            options = ['attack', 'run away', 'get status', 'exit game']
        elif self.state == 'peace':
            options = ['go forward', 'get status', 'exit game']
        options_len = len(options)
        while True:
            try:
                for counter, act in enumerate(options, start=1):
                    print(f'{counter} - {act}')
                action = int(input(f'What do you want to do? '))
                if 1 <= action <= options_len:
                    return action
                else:
                    print(f'\nERROR! You must choose options only from 1-{options_len} range')
            except ValueError:
                print('\nERROR! Incorrect input')

    def _new_scene(self):
        new_location_type = random.choice(['peaceful', 'hostile'])
        location = Location(new_location_type)
        self.location = location
        if self.location.enemies > 7:
            self.state = 'battle'
            self.enemy = Enemy(self.player)
            self.show_battle_scene()
            return
        self.show_peace_scene()
