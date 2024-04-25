from console import *
from enemy import *
from quest import Quest, get_current_quests
from items import Items
from location import Location
from player import Player
from tavern import Tavern
import random

import db


class Scene:
    def __init__(self, location: Location, player: Player, items: Items) -> None:
        self.location = location
        self.player = player
        self.state = 'peace'
        self.enemy = None
        self.tavern = None
        self.items = items
        self.turns_without_tavern = 0
      
        self.npc_quest = None  # keeps object of Quest class
        self.reaction = False  # shows if it's first meeting with NPC

    def show_current_scene(self) -> None:
        """
        Shows current scene during some actions if needed
        """
        if self.state == 'battle':
            # self.battle.show_battle_scene()
            self.show_battle_scene()
        elif self.state == 'peace':
            self.show_peace_scene()
        elif self.state == 'tavern':
            self.tavern.tavern_menu()
        elif self.state == 'npc':
            self.npc_dialog()
        elif self.state == 'merchant':
            self.tavern.merchant_dialog()

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
        for counter, act in enumerate(options, start=1):
            print(f'{counter} - {act if act not in highlight_actions else color("green", act)}')
        answer = answer_handler(
            question='What do you want to do? ',
            correct_range=[str(x) for x in range(1, options_len + 1)],
            cheats=["hesoyam"])
        if answer[0] == "cheats":
            self.player.health = 10
            self.player.gold += 250
            return
        action = int(answer[1])
        return options[action - 1]
    
    def get_possible_options(self) -> list[str]:
        options = []
        if self.state == 'battle':
            options = ['attack', 'run away', 'inventory', 'get status', 'exit game']
            if not self.enemy.run_away_able:
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
            if not self.npc_quest:
                options.remove('talk with Carl')
            if not self.location.chest:
                options.remove('check a chest')
        return options

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
            return
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

    def show_battle_scene(self) -> None:
        """
        Shows process of the battle
        """
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        warning('Battle mode')
        print('Drunk level:', self.player.get_condition())
        self.enemy.show_rivals_stats()
        action = self.show_possible_options()
        if action == "attack":
            self.player_attack()
        elif action == "run away":
            self.try_run_away()
        elif action == "inventory":
            self.items.show_inventory()
            return
        elif action == "get status":
            self.player.show_player_info()
            return
        elif action == "exit game":
            self.ask_about_exit()

    def player_attack(self):
        """
        Counts player's attack for each turn, then hits enemy.
        Finishes battle if enemy's been slayed, else hits player in response
        """
        attack = self.player.attack - self.enemy.defence
        if attack < 1:
            attack = 1
        lucky_hit, critical_hit = '', ''
        if self.player.luck > random.randint(1, 100):
            lucky_hit = color('green', 'Lucky hit! ')
        if self.player.luck / 2 + self.player.agility > random.randint(1, 100):
            critical_hit = color('green', 'CRITICAL HIT! ')
        lucky_hit = '' if critical_hit else lucky_hit
        if lucky_hit:
            attack = int(attack * 1.2)
        if critical_hit:
            attack = int(attack * 1.5)
        print(f'{lucky_hit}{critical_hit}Your default attack is {self.player.attack}')
        print(f'Enemy defence is {self.enemy.defence}')
        print(f'Your actual attack is {attack}')
        self.enemy.get_damage(attack)
        if self.enemy.health <= 0:
            self.enemy.died()
            self.finish_battle(type_='battle')
        else:
            self.enemy.check_specials()
            # self.damage_taken += self.enemy.enemy_attack()
            self.enemy.enemy_attack()
            self.show_battle_scene()

    def try_run_away(self) -> None:
        """
        USER ACTION
        Trying to run away from enemy, if attempt is failed, blocks next attempts
        """
        if self.player.agility > self.enemy.agility:
            print('You have ran away')
            self.finish_battle('run')
        else:
            diff = self.enemy.agility - self.player.agility
            if self.player.luck > diff:
                print('Your luck let you to run away')
                self.finish_battle('run')
            else:
                print("You couldn't run away")
                self.enemy.enemy_attack()
                self.enemy.run_away_able = False
                self.show_battle_scene()

    def finish_battle(self, type_: str) -> None:
        """
        Finishes battle
        """
        self.enemy = None
        self.state = 'peace'
        if type_ == 'run':
            self.player.set_drunk(-1)
        elif type_ == 'battle':
            self.player.set_drunk(-3)  # todo: depends on taken damage
        # print(f'Damage taken during battle: {self.damage_taken}')
        return

    def npc_dialog(self) -> None:
        """
        USER ACTION
        Shows menu within meeting NPC
        """
        print(f"""\nYou're in the location "{self.location.name}" ({self.location.type}) """)
        if not self.reaction:
            print("You've met Carl")
            print(color('green', 'Random welcome phrase'))
        elif self.reaction:
            print('Carl is waiting for you')
        print('Drunk level:', self.player.get_condition())
        quests = get_current_quests()
        if len(quests) < 3:
            if not self.reaction:
                if self.player.drunk > 24 and random.randint(1, 10) > 2:
                    self.check_npc_quests(quests)
                    return
                elif self.player.drunk < 25 and random.randint(1, 10) > 6:
                    db.add_item_to_inventory(1)
                    print("I see you need a drink, take it")
                    print("You've gotten Beer bottle")
        action = self.show_possible_options()
        if action == "go forward":
            self.npc_quest = None
            self.state = 'peace'
            self.new_scene()
        if action == "talk with Carl":
            self.check_npc_quests(quests)
        if action == "check a chest":
            self.items.get_chest_item()
            self.location.chest = False
            return
        if action == "inventory":
            self.items.show_inventory()
            return
        elif action == "get status":
            self.player.show_player_info()
            return
        elif action == "exit game":
            self.ask_about_exit()

    def check_npc_quests(self, quests) -> None:
        """
        USER ACTION
        Generates random new tasks for player
        """
        if not self.npc_quest:
            if len(quests) == 0:
                order = enemy_for_npc_quest(self.player)
            else:
                current_orders = []
                for quest in quests:
                    current_orders.append(quest.order.type)
                order = enemy_for_npc_quest(self.player, exclude=current_orders)
            amount = random.randint(2, 5)
            reward = amount * 5 * self.player.level + (random.randint(2, 10) * self.player.level)
            quest = Quest(order=order, amount=amount, reward=reward)
            self.npc_quest = quest
            if self.state != 'npc':
                self.state = 'npc'

        print() if self.reaction else None
        print(f'I need to clean this area from {color("red", self.npc_quest.order.name + "s")}')
        print(f'Think {self.npc_quest.goal_amount} ones will be enough for now')
        print(f'Reward for this is {self.npc_quest.reward} gold coins')

        answer = answer_handler(
            question=f'Are you accept? (yes/no) ',
            yes=['y', 'yes', '1'],
            no=['n', 'no', '2'])
        if answer[0] == 'no':
            self.reaction = True
            return
        print('Quest has been taken')
        self.npc_quest.add_to_list()
        self.npc_quest = None
        self.state = 'peace'

    def new_scene(self) -> None:
        """
        USER ACTION
        Leads player through new random locations, checks either there are enemies or not
        """
        # choosing of next location
        if not hasattr(self, "first_location"):
            self.first_location = Location(random.choice(['peaceful', 'hostile']), self.player.luck, self.turns_without_tavern)
            self.second_location = Location(random.choice(['peaceful', 'hostile']), self.player.luck, self.turns_without_tavern)
        next_location = answer_handler(
            question=f'\n1 - {self.first_location.name} ({self.first_location.type})\n'
            f'2 - {self.second_location.name} ({self.second_location.type})\n\n'
            'Where do you want to go? (0 for cancel) ',
            path=['1', '2'],
            cancel=['0'])
        if next_location[0] == 'cancel':
            return
        if next_location[1] == '1':
            self.location = self.first_location
        if next_location[1] == '2':
            self.location = self.second_location
        del self.first_location
        del self.second_location

        # actions after location has been selected
        self.turns_without_tavern += 1
        if self.location.tavern:
            self.tavern = None
            self.turns_without_tavern = 1
        if self.location.enemies:
            self.state = 'battle'
            self.enemy = generate_enemy(self.player)
            self.show_battle_scene()
            return
        if self.player.drunk > 0:
            self.player.set_drunk(-1)
        if self.location.npc:
            self.npc_dialog()
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
