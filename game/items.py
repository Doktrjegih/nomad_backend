import random

from console import error, print
import db
from player import Player

ALWAYS_SHOWED = ['food', 'alcohol', 'garbage']


class Items:
    def __init__(self, player: Player) -> None:
        self.player = player

    def show_inventory(self) -> None:
        """
        Shows inventory and lets to manage it
        :return:
        """
        inventory = db.get_inventory()
        if inventory:

            # showing of items
            if self.player.drunk < 1:
                inventory = [x for x in inventory if x[1].type_ in ALWAYS_SHOWED]
                if not inventory:
                    print('[Empty inventory]')
                    return
            print()
            for counter, item in enumerate(inventory, start=1):
                active_weapon, attack = '', ''
                if item[1].name == self.player.weapon[0]:  # todo: may be weak spot, need to observe usefulness
                    active_weapon = ' [active weapon]'
                if item[1].type_ == 'weapon':
                    attack = f' (attack {item[1].attack})'
                print(f"{counter} - {item[1].name}{attack}: {item[0].amount}{active_weapon}")
            print(f"0 - cancel")

            # dialog for manipulating with items
            while True:
                try:
                    answer = input(f'Which one do you want to use? ')
                    if answer in [str(x) for x in range(1, counter + 1)]:
                        item_index = int(answer) - 1
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
                            self.player.weapon = [item_name, (attack := inventory[item_index][1].attack)]
                            print(f"Current weapon: {item_name} (attack {attack})")
                        elif type_of_item == "garbage":
                            print(f"You can't use {item_name}, but you will be able to sell it sometime")
                        self.player.recount_params()
                        return
                    elif answer == '0':
                        return
                    else:
                        error('Incorrect input')
                except ValueError:
                    error('Incorrect input')
        else:
            print('[Empty inventory]')

    def get_chest_item(self):
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
