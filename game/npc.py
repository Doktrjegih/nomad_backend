import random

import db
from console import error, color, print
from enemy import enemy_for_npc_quest
from items import Items
from player import Player
from quest import Quest, get_current_quests


class Npc:
    def __init__(self, scene, player: Player, items: Items) -> None:
        self.scene = scene
        self.player = player
        self.items = items
        self.phrase = 'Random welcome phrase'
        self.active_quests = True if random.randint(1, 10) > 2 else False  # shows if NPC has quest
        self.npc_quest = None  # keeps object of Quest class
        self.reaction = False  # shows if it's first meeting with NPC

    def npc_dialog(self) -> None:
        """
        USER ACTION
        Shows menu within meeting NPC
        """
        print(f"""\nYou're in the location "{self.scene.location.name}" ({self.scene.location.type}) """)
        if not self.reaction:
            print(f"""You've met Carl""")
        elif self.reaction and self.npc_quest:
            print('Carl is waiting for you')
        print('Drunk level:', self.player.get_condition())
        quests = get_current_quests()
        if not self.reaction:
            print(color('green', '\n' + self.phrase))
        if len(quests) < 3:
            if not self.reaction:
                if self.player.drunk > 24 and self.active_quests:
                    self.check_npc_quests()
                elif self.player.drunk < 25 and random.randint(1, 10) > 6:
                    db.add_item_to_inventory(1)
                    print("I see you need a drink, take it")
                    print(f"You've gotten Beer bottle")
                self.scene.state = 'peace'
                self.scene.npc = None
        action = self.scene.show_possible_options(npc_quest=False) if not self.npc_quest \
            else self.scene.show_possible_options()
        if action == "go forward":
            self.scene.npc = None
            self.scene.state = 'peace'
            self.scene.new_scene()
        if action == "talk with Carl":
            self.check_npc_quests()
        if action == "check a chest":
            self.items.get_chest_item()
            self.scene.location.chest = False
            self.scene.show_current_scene()
        if action == "inventory":
            self.items.show_inventory()
            self.scene.show_current_scene()
        elif action == "get status":
            self.player.show_player_info()
            self.scene.show_current_scene()
        elif action == "exit game":
            self.scene.ask_about_exit()

    def check_npc_quests(self) -> None:
        """
        USER ACTION
        Generates random new tasks for player with some chance
        """
        quests = get_current_quests()
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

        print() if self.reaction else None
        print(f'I need to clean this area from {color("red", self.npc_quest.order.name + "s")}')
        print(f'Think {self.npc_quest.goal_amount} ones will be enough for now')
        print(f'Reward for this is {self.npc_quest.reward} gold coins')

        while True:
            answer = input(f'Are you accept? (yes/no) ')
            if answer.lower() in ['y', 'yes', '1']:
                print('Quest has been taken')
                self.npc_quest.add_to_list()
                self.scene.npc = None
                self.scene.state = 'peace'
                self.scene.show_current_scene()
            elif answer.lower() in ['n', 'no', '2']:
                self.reaction = True
                self.npc_dialog()
            else:
                error('Incorrect input')
