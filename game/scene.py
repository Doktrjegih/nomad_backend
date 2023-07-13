import random

# from console import console
from enemy import Enemy
from location import Location
from player import Player
from tavern import Tavern
from battle import Battle


class Scene:
    def __init__(self, location: Location, player: Player) -> None:
        self.run_able = True
        self.location = location
        self.player = player
        self.state = 'peace'
        self.enemy = None
        self.tavern = None

    def show_current_scene(self) -> None:
        if self.state == 'battle':
            battle = Battle(scene=self, player=self.player, enemy=self.player)
            battle.show_battle_scene()
        elif self.state == 'peace':
            self.show_peace_scene()

    def show_peace_scene(self) -> None:
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        print('drunk level:', self.player.get_condition())
        # console(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        action = self.show_possible_options()
        if action == "go forward":
            self._new_scene()
        elif action == "enter tavern":
            self.state = 'tavern'
            if not self.tavern:
                self.tavern = Tavern(scene=self, player=self.player)
            self.tavern.tavern_menu()
        elif action == "get status":
            self.player.show_player_info()
            self.show_current_scene()
        elif action == "exit game":
            exit()

    def show_possible_options(self) -> str:
        options = []
        if self.state == 'battle':
            options = ['attack', 'run away', 'get status', 'exit game']
            if not self.run_able:
                options.remove('run away')
        elif self.state == 'peace':
            options = ['go forward', 'enter tavern', 'get status', 'exit game']
            if not self.location.tavern:
                options.remove('enter tavern')
        elif self.state == 'tavern':
            options = ['go out', 'take a beer', 'get quest', 'get status', 'exit game']
        options_len = len(options)
        while True:
            try:
                for counter, act in enumerate(options, start=1):
                    print(f'{counter} - {act}')
                action = int(input(f'What do you want to do? '))
                if 1 <= action <= options_len:
                    return options[action - 1]
                else:
                    print(f'\nERROR! You must choose options only from 1-{options_len} range')
            except ValueError:
                print('\nERROR! Incorrect input')

    def _new_scene(self) -> None:
        new_location_type = random.choice(['peaceful', 'hostile'])
        location = Location(new_location_type)
        self.location = location
        if self.location.enemies:
            self.state = 'battle'
            self.enemy = Enemy(self.player)
            battle = Battle(scene=self, player=self.player, enemy=self.enemy)
            battle.show_battle_scene()
            return
        self.show_peace_scene()
