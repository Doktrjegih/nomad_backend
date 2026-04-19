import json
import random

import db
from console import print, color, answer_handler
from enemy import Enemy, Boss
from items import Items, Equipment, JsonToEquipment
from paths import PLOT_QUESTS
from player import Player
from quest import Quest, get_current_quests, there_is_plot_quest


class Tavern:
    player: Player
    items: Items

    def __init__(self, scene) -> None:
        self.tavern_quest = None
        self.scene = scene
        self.player = scene.player
        self.active_quests = True if self.scene.location.name == "hometown" else random.choice([True, False])
        self.items = scene.items
        self.merchant = True if self.scene.location.name == "hometown" else random.choice([True, False])
        self.aleg = self.spawn_aleg()
        self.reaction = False

    def tavern_menu(self) -> None:
        """
        USER ACTION
        Shows tavern menu
        """
        print("\nYou're in the tavern")
        print('Drunk level:', self.player.get_condition())
        action = self.scene.show_possible_options()
        if action == "go out":
            self.scene.state = 'peace'
            self.scene.tavern = self
        elif action == "take a beer":
            self.buy_beer(10)
        elif action == "take a steak":
            self.buy_steak()
        elif action == "merchant":
            self.merchant_dialog()
        elif action == "talk with Aleg":
            self.aleg_dialog()
        elif action == "check quests":
            self.check_quests()
        else:
            self.scene.check_common_actions(action)

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
        for quest in quests:
            quest: Quest
            if not quest.plot_quest and quest.is_finished:
                quest.close_quest(quests, self.player)
                db.add_item_to_inventory(1)  # todo: hardcode

        # check if max value of current quests
        quests = get_current_quests(ignore_plot=True)
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
                    current_orders.append(quest.order)
                order = Enemy(self.player, exclude=current_orders)
            amount = random.randint(2, 5)
            reward = amount * 5 + (random.randint(2, 10))  # todo: use smth instead of lvl
            quest = Quest(order=order.name, amount=amount, reward=reward)
            self.tavern_quest = quest

        print('\nHello stranger!')
        print(f'I need to clean this area from {color("red", self.tavern_quest.order + "s")}')
        print(f'Think {self.tavern_quest.goal_amount} ones will be enough for now')
        print(f'Reward for this is {self.tavern_quest.reward} gold coins')

        answer = answer_handler(
            question=f'Are you accept? (yes/no) ',
            yes=['y', 'yes', '1'],
            no=['n', 'no', '2'])
        if answer[0] == 'no':
            return
        print("Quest has been taken")
        self.active_quests = False
        self.tavern_quest.add_to_list()

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
            self.merchant_buy()
        elif action == "sell":
            self.merchant_sell()
        else:
            self.scene.check_common_actions(action)

    def merchant_sell(self) -> None:
        """
        USER ACTION
        Shows sell menu which manipulates with items
        """
        inventory = db.get_inventory()
        if not inventory:
            print(color("yellow", '[Empty inventory]'))
            return

        # showing of items
        inventory = [x for x in inventory if x[1].type_ not in ["food", "alcohol"]]
        if not inventory:
            print('[Nothing to sell]')
            return
        counter = self.items.print_inventory(inventory)

        # dialog for manipulating with items
        answer_item = answer_handler(question="Which one do you want to sell? ",
                                     correct_range=[str(x) for x in range(1, counter + 1)],
                                     cancel=['0'])
        if answer_item[0] == 'cancel':
            return
        item_index = int(answer_item[1]) - 1
        item_name = inventory[item_index][1].name
        amount = inventory[item_index][0].amount
        if amount == 1:
            answer_confirm = answer_handler(question=f'You chose {item_name}. Sell it? (yes/no) ',
                                            yes=['y', 'yes', '1'],
                                            no=['n', 'no', '2'])
            if answer_confirm[0] == 'no':
                return
            db.remove_item(inventory[item_index][0])
            self.player.gold += round(inventory[item_index][1].cost / 2)
            print(f'Sold 1 {item_name}')
        else:
            answer_amount = answer_handler(question=f'You chose {item_name} ({amount} ones). '
                                                    'How many item would you want to sell? (0 for cancel) ',
                                           correct_range=[str(x) for x in range(1, amount + 1)],
                                           cancel=['0'])
            if answer_amount[0] == 'cancel':
                return
            answer_confirm_several = answer_handler(question=f'Sell {answer_amount[1]} ones? (yes/no) ',
                                                    yes=['y', 'yes', '1'],
                                                    no=['n', 'no', '2'])
            if answer_confirm_several[0] == 'no':
                return
            db.remove_item(inventory[item_index][0], int(answer_amount[1]))
            self.player.gold += round(inventory[item_index][1].cost / 2)
            print(f'Sold {answer_amount[1]} {item_name}')
        self.player.recount_params()

    def merchant_buy(self) -> None:
        """
        USER ACTION
        Shows buying menu
        """
        items_for_sell = [Equipment(JsonToEquipment(x), self.player.drunk) for x in db.GAME_ITEMS
                          if x["type"] in ["weapon", "armor"] and not x.get("boss")]
        while True:
            print()
            for counter, item in enumerate(items_for_sell, start=1):
                match item.type:
                    case "weapon":
                        print(f"{counter} - {item} - {item.cost} gold coins")
                    case "armor":
                        print(f"{counter} - {item} - {item.cost} gold coins")
            print("0 - cancel")
            answer_amount = answer_handler(question=f'What do you want to buy? (you have {self.player.gold} gold coins) ',
                                           correct_range=[str(x) for x in range(1, len(items_for_sell) + 1)],
                                           cancel=['0'])
            if answer_amount[0] == 'cancel':
                return

            chosen_item = items_for_sell[int(answer_amount[1]) - 1]
            if (price := chosen_item.cost) > self.player.gold:
                print("You don't have enough gold coins for that")
            else:
                confirm_buying = answer_handler(question=f'\nYou chose {(item_name := chosen_item.name)}. '
                                                         'Buy it? (yes/no) ',
                                                yes=['y', 'yes', '1'],
                                                no=['n', 'no', '2'])
                if confirm_buying[0] == 'no':
                    return
                db.add_item_to_inventory(chosen_item.id)
                self.player.gold -= price
                print(f'Bought {item_name}')

    def aleg_dialog(self) -> None:
        """
        USER ACTION
        Shows menu within meeting Aleg (plot quests)
        """
        print("\nYou're sitting across from Aleg")
        print("Drunk level:", self.player.get_condition())

        if not self.reaction:
            print(color("green", "Hello there!"))
            self.reaction = True

        # checking quest's state if there is one
        if there_is_plot_quest():
            quests = get_current_quests()
            for quest in quests:
                if quest.plot_quest and quest.is_finished:
                    print("Oh, nice work! I see you've done well")
                    self.player.plot_stage += 1
                    quest.close_quest(quests=quests, player=self.player)
                    self.player.improve_stats()
                    break
            else:
                print("Come back when you've finished")
                return

        # if there is no active quest
        with open(PLOT_QUESTS, "r", encoding="utf-8") as fd:
            json_quests = json.loads(fd.read())
            for json_quest in json_quests:
                if json_quest["id"] == self.player.plot_stage:

                    # check if player is drunk enough
                    if json_quest["needed_drunk"] > self.player.drunk:
                        print("Sorry, not sure if you're ready for this now")
                        return

                    print("I have a quest for you:")
                    if json_quest.get("boss"):
                        order = Boss(self.player, name=json_quest["target"])
                        boss = True
                        print(f"Well, it's time. I have a tough one for you, {color('red', order.name)}")
                        print("You need to finish him")
                    else:
                        order = Enemy(self.player, random_enemy=False, name=json_quest["target"])
                        boss = False
                        print(json_quest["description"])
                        print(f"You need kill {color('red', order.name)} {json_quest['amount']} times")
                    quest = Quest(order=order.name, amount=json_quest["amount"], is_plot=True, boss=boss)
                    break
        answer = answer_handler(
            question="Are you accept? (yes/no) ",
            yes=["y", "yes", "1"],
            no=["n", "no", "2"])
        if answer[0] == "no":
            return
        print("Quest has been taken")
        quest.add_to_list()

    def spawn_aleg(self) -> bool:
        """
        Spawns Aleg when necessary
        :return: True if Aleg should be spawned, otherwise False
        """
        if there_is_plot_quest():
            quests = get_current_quests()
            for quest in quests:
                if quest.plot_quest and quest.is_finished:
                    return True
        if self.scene.location.name == "hometown":
            return True
        if random.randint(1, 3) == 3:
            return True
        return False
