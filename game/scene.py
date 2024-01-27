from battle import Battle
from console import *
from enemy import *
from items import Items
from location import Location
from npc import Npc
from player import Player
from tavern import Tavern


class Scene:
    def __init__(self, location: Location, player: Player, items: Items) -> None:
        self.run_able = True
        self.location = location
        self.player = player
        self.state = 'peace'
        self.enemy = None
        self.tavern = None
        self.npc = None
        self.items = items
        self.turn_without_tavern = 0

    def show_current_scene(self) -> None:
        """
        Shows current scene during some actions if needed
        """
        if self.state == 'battle':
            battle = Battle(scene=self)  # todo: constant recreating of object during battle (try/except?)
            battle.show_battle_scene()
        elif self.state == 'peace':
            self.show_peace_scene()
        elif self.state == 'tavern':
            self.tavern.tavern_menu()
        elif self.state == 'npc':
            self.npc.npc_dialog()
        elif self.state == 'merchant':
            self.tavern.merchant_dialog()

    def show_peace_scene(self) -> None:
        """
        Shows actions outside tavern in peaceful time
        """
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type})""")
        print('Drunk level:', self.player.get_condition())
        action = self.show_possible_options()
        if action == "go forward":
            self.new_scene()
        elif action == "enter tavern":
            self.state = "tavern"
            if not self.tavern:
                self.tavern = Tavern(scene=self, player=self.player, items=self.items)
            self.tavern.tavern_menu()
        elif action == "check a chest":
            self.items.get_chest_item()
            self.location.chest = False
            return
        elif action == 'inventory':
            self.items.show_inventory()
            return
        elif action == "get status":
            self.player.show_player_info()
            return
        elif action == "exit game":
            self.ask_about_exit()

    def show_possible_options(self) -> str | None:
        """
        USER ACTION
        Shows possible actions for each type of scene depends on current status (peaceful, battle, tavern)
        Waits of user choice
        :return: str type of action
        """
        options = self.get_possible_options()
        options_len = len(options)
        highlight_actions = ['enter tavern', 'check a chest']
        while True:
            try:
                for counter, act in enumerate(options, start=1):
                    print(f'{counter} - {act if act not in highlight_actions else color("green", act)}')
                action = input(f'What do you want to do? ')
                if action == "HESOYAM":
                    self.player.health = 10
                    self.player.gold += 250
                    return
                else:
                    action = int(action)
                if 1 <= action <= options_len:
                    return options[action - 1]
                else:
                    error(f'You must choose options only from 1-{options_len} range')
            except ValueError:
                error('Incorrect input')

    def get_possible_options(self) -> list[str]:
        options = []
        if self.state == 'battle':
            options = ['attack', 'run away', 'inventory', 'get status', 'exit game']
            if not self.run_able:
                options.remove('run away')
        elif self.state == 'peace':
            options = ['go forward', 'enter tavern', 'check a chest', 'inventory', 'get status', 'exit game']
            if not self.location.tavern:
                options.remove('enter tavern')
            if not self.location.chest:
                options.remove('check a chest')
        elif self.state == 'tavern':
            options = ['go out', 'take a beer', 'take a steak', 'merchant', 'check quests', 'inventory', 'get status',
                       'exit game']
            if not self.tavern.merchant or self.player.drunk < 25:
                options.remove('merchant')
        elif self.state == 'merchant':
            options = ['back to tavern', 'buy', 'sell', 'inventory', 'get status', 'exit game']
        elif self.state == 'npc':
            options = ['go forward', 'check a chest', 'talk with Carl', 'inventory', 'get status', 'exit game']
            if not self.npc:
                options.remove('talk with Carl')
            if not self.location.chest:
                options.remove('check a chest')
        return options

    def new_scene(self) -> None:
        """
        USER ACTION
        Leads player through new random locations, checks either there are enemies or not
        """
        new_location_type = random.choice(['peaceful', 'hostile'])
        self.turn_without_tavern += 1
        if self.location.tavern:
            self.tavern = None
            self.turn_without_tavern = 1
        location = Location(new_location_type, self.player.luck, self.turn_without_tavern)
        self.location = location
        if self.player.drunk > 0:
            self.player.set_drunk(-1)
        if self.location.enemies:
            self.state = 'battle'
            self.enemy = generate_enemy(self.player)
            battle = Battle(scene=self)
            battle.show_battle_scene()
            return
        if self.location.npc:
            self.npc = Npc(scene=self)
            self.npc.npc_dialog()
            return
        self.show_peace_scene()

    @staticmethod
    def ask_about_exit() -> None:
        """
        Dialog for confirmation if player wants to exit
        """
        while True:
            answer = input('\nDo you want to exit? (yes/no) ')
            if answer.lower() in ['y', 'yes', '1']:
                exit()
            elif answer.lower() in ['n', 'no', '2']:
                return
            else:
                error('Incorrect input')
