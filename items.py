import random

from console import print, answer_handler, color
import db
from player import Player

ALWAYS_SHOWED = ['food', 'alcohol', 'garbage']


class Items:
    def __init__(self, player: Player) -> None:
        self.player = player

    def show_inventory(self) -> None:
        """
        Shows inventory and lets to manage it
        """
        inventory = db.get_inventory()
        if inventory:

            # showing of items
            if self.player.drunk < 1:
                inventory = [x for x in inventory if x[1].type_ in ALWAYS_SHOWED]
                if not inventory:
                    print(color("yellow", '[Empty inventory]'))
                    return
            counter = self.print_inventory(inventory)

            # dialog for manipulating with items
            answer = answer_handler('Which one do you want to use? ',
                                    correct_range=[str(x) for x in range(1, counter + 1)],
                                    cancel=['0'])
            if answer[0] == 'cancel':
                return
            item_index = int(answer[1]) - 1
            item_name = inventory[item_index][1].name
            type_of_item = inventory[item_index][1].type_
            if type_of_item == "food":
                self.player.health += 2
                self.player.set_drunk(-2)
                db.remove_item(inventory[item_index][0])
                print(f"Your HP is {self.player.health} now")
            elif type_of_item == "alcohol":
                self.player.set_drunk(10)
                db.remove_item(inventory[item_index][0])
                print(f"You've drunk {item_name}")
            elif type_of_item == "weapon":
                if self.player.weapon:
                    db.put_on_off_item(self.player.weapon, on=False)
                db.put_on_off_item(inventory[item_index][0], on=True)
                print(f"Current weapon: {item_name} (attack {inventory[item_index][1].attack})")
            elif type_of_item == "armor":
                if self.player.armor:
                    db.put_on_off_item(self.player.armor, on=False)
                db.put_on_off_item(inventory[item_index][0], on=True)
                print(f"Current armor: {item_name} (defence {inventory[item_index][1].defence})")
            elif type_of_item == "garbage":
                print(f"You can't use {item_name}, but you will be able to sell it sometime")
            self.player.recount_params()
            return
        print(color("yellow", '[Empty inventory]'))

    def print_inventory(self, inventory: list) -> int:
        """
        Prints inventory with serial numbers for further interaction
        :param inventory: list with items from DB
        :return: int value with actual len of inventory (amount of different items)
        """
        print()
        for counter, item in enumerate(inventory, start=1):

            # todo: optimize
            active_weapon, attack, active_armor, defence = '', '', '', ''
            if self.player.weapon:
                if item[1].name == self.player.weapon.name:  # todo: may be weak spot, need to observe usefulness
                    active_weapon = ' [active weapon]'
            if item[1].type_ == 'weapon':
                attack = f' (attack {item[1].attack})'
            if self.player.armor:
                if item[1].name == self.player.armor.name:
                    active_armor = ' [active armor]'
            if item[1].type_ == 'armor':
                defence = f' (defence {item[1].defence})'
            equipment_params = f"{attack}{defence}"
            active_equipment = f"{active_weapon}{active_armor}"
            string = f"{counter} - {item[1].name}" + equipment_params + f": {item[0].amount}" + active_equipment

            print(string)
        print("0 - cancel")
        return counter

    def get_chest_item(self) -> None:
        """
        Gives random item from chest to player
        """
        item = random.choice(db.get_all_items())
        if item.type_ in ALWAYS_SHOWED:
            print(f"You've found {item.name}")
            db.add_item_to_inventory(item.item_id)
        else:
            if self.player.drunk > 0:
                print(f"You've found {item.name}")
                db.add_item_to_inventory(item.item_id)
        self.player.gold += (loot := random.randint(5, 25))
        print(f"You've found {loot} gold coins")
