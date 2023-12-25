import random

from enemy import Enemy
from quest import Quest, get_current_quests
from player import Player
from console import *
from items import Items, ALWAYS_SHOWED
import db


class Tavern:
    def __init__(self, scene, player: Player, items: Items) -> None:
        self.tavern_quest = None
        self.scene = scene
        self.player = player
        self.active_quests = True if self.scene.location.name == 'hometown' else random.choice([True, False])
        self.items = items
        self.merchant = random.choice([True, False])

    def tavern_menu(self) -> None:
        """
        USER ACTION
        Shows tavern menu
        """
        print(f"""\nYou're in the tavern""")
        print('Drunk level:', self.player.get_condition())
        action = self.scene.show_possible_options()
        if action == "go out":
            self.scene.state = 'peace'
            self.scene.tavern = self
            self.scene.show_current_scene()
        elif action == "take a beer":
            self.buy_beer(10)
            self.tavern_menu()
        elif action == "take a steak":
            self.buy_steak()
            self.tavern_menu()
        elif action == "merchant":
            self.merchant_dialog()
        elif action == "check quests":
            self.check_quests()
        elif action == "inventory":
            self.items.show_inventory()
            self.tavern_menu()
        elif action == "get status":
            self.player.show_player_info()
            self.tavern_menu()
        elif action == "exit game":
            self.scene.ask_about_exit()

    def buy_beer(self, beer: int) -> None:
        """
        USER ACTION
        Buy a cup of beer for 5 coins, increases Player.drunk level
        """
        if self.player.gold < 5:
            print("Not enough money, it's 5 gold coins for beer")
            return
        self.player.set_drunk(beer)
        self.player.gold -= 5

    def buy_steak(self) -> None:
        """
        USER ACTION
        Buy a steak for 5 coins, increases Player.health level
        """
        if self.player.gold < 5:
            print("Not enough money, it's 5 gold coins for steak")
            return
        self.player.health += 2
        self.player.set_drunk(-2)
        if self.player.health > self.player.max_hp:
            self.player.health = self.player.max_hp
        print(f'Your HP is {self.player.health} now')
        self.player.gold -= 5

    def check_quests(self) -> None:
        """
        USER ACTION
        Checks if there are finished quests, closes quests if yes.
        Generates random new tasks for player, restricts getting of quests if player already has max amount of quests
        """
        # check if there are finished quests
        quests = get_current_quests()
        if quests:
            for quest in quests[:]:
                quest: Quest
                if quest.is_finished:
                    quest.close_quest(quests, self.player)
                    db.add_item_to_inventory(1)

        # check if max value of current quests
        quests = get_current_quests()
        if len(quests) > 2 or not self.active_quests:
            print("Sorry, I don't have quests for you now")
            self.tavern_menu()
            return

        # check if tavern quest was taken
        if not self.tavern_quest:
            if len(quests) == 0:
                order = Enemy(self.player)
            else:
                current_orders = []
                for quest in quests:
                    current_orders.append(quest.order.type)
                order = Enemy(self.player, exclude=current_orders)
            amount = random.randint(2, 5)
            reward = amount * 5 * self.player.level + (random.randint(2, 10) * self.player.level)
            quest = Quest(order=order, amount=amount, reward=reward)
            self.tavern_quest = quest

        print('\nHello stranger!')
        print(f'I need to clean this area from {color("red", self.tavern_quest.order.name + "s")}')
        print(f'Think {self.tavern_quest.goal_amount} ones will be enough for now')
        print(f'Reward for this is {self.tavern_quest.reward} gold coins')

        while True:
            answer = input(f'Are you accept? (yes/no) ')
            if answer.lower() in ['y', 'yes', '1']:
                print('Quest has been taken')
                self.active_quests = False
                self.tavern_quest.add_to_list()
                self.tavern_menu()
            elif answer.lower() in ['n', 'no', '2']:
                self.tavern_menu()
            else:
                error('Incorrect input')

    def merchant_dialog(self) -> None:
        """
        USER ACTION
        Shows menu with merchant
        """
        self.scene.state = 'merchant'
        print("\nYou're in the merchant shop")
        print('Drunk level:', self.player.get_condition())
        action = self.scene.show_possible_options()
        if action == "back to tavern":
            self.scene.state = 'tavern'
            self.tavern_menu()
        elif action == "buy":
            pass  # todo: add mechanics
            self.scene.show_current_scene()
        elif action == "sell":
            self.merchant_sell()
            self.scene.show_current_scene()
        elif action == "inventory":
            self.items.show_inventory()
            self.scene.show_current_scene()
        elif action == "get status":
            self.player.show_player_info()
            self.scene.show_current_scene()
        elif action == "exit game":
            self.scene.ask_about_exit()

    def merchant_sell(self) -> None:
        """
        USER ACTION
        Shows sell menu which manipulates with items
        """
        inventory = db.get_inventory()
        if not inventory:
            print('[Empty inventory]')
            return

        # showing of items
        inventory = [x for x in inventory if x[1].type_ not in ALWAYS_SHOWED]
        if not inventory:
            print('[Nothing to sell]')
            return
        counter = self.items.print_inventory(inventory)

        # dialog for manipulating with items
        answer_item = answer_handler(question="Which one do you want to sell? ",
                                     is_int=True,
                                     items=[x for x in range(1, counter + 1)],
                                     cancel=[0])
        if answer_item[0] == 'cancel':
            return
        item_index = answer_item[1] - 1
        item_name = inventory[item_index][1].name
        amount = inventory[item_index][0].amount
        if amount == 1:
            answer_confirm = answer_handler(question=f'You chose {item_name}. Sell it? (yes/no) ',
                                            is_int=False,
                                            yes=['y', 'yes', '1'],
                                            no=['n', 'no', '2'])
            if answer_confirm[0] == 'no':
                return
            db.remove_item(inventory[item_index][0])
            self.player.gain_scores(inventory[item_index][1].cost)
            print(f'Sold 1 {item_name}')
        else:
            answer_amount = answer_handler(question=f'You chose {item_name} ({amount} ones). '
                                                    f'How many item would you want to sell? (0 for cancel) ',
                                           is_int=True,
                                           correct_range=[x for x in range(1, amount + 1)],
                                           cancel=[0])
            if answer_amount[0] == 'cancel':
                return
            answer_confirm_several = answer_handler(question=f'Sell {answer_amount[1]} ones? (yes/no) ',
                                                    is_int=False,
                                                    yes=['y', 'yes', '1'],
                                                    no=['n', 'no', '2'])
            if answer_confirm_several[0] == 'no':
                return
            db.remove_item(inventory[item_index][0], answer_amount[1])
            self.player.gain_scores(inventory[item_index][1].cost * answer_amount[1])
            print(f'Sold {answer_amount[1]} {item_name}')
        self.player.recount_params()

    def merchant_buy(self) -> None:
        """
        USER ACTION
        Shows buying menu
        """
        # 1. show merchant items
        # 2. ask which one player wants to buy
        # 3. if more than one, ask how many
        # 4. check player's gold is enough
        # 5. confirmation, writing to DB
        pass
