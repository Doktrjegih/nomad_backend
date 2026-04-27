import random
from json import loads, dumps
from typing import TYPE_CHECKING

import db
from console import print, answer_handler, color, get_effect_color
from constants import *

if TYPE_CHECKING:
    from player import Player


class Items:
    def __init__(self, player: "Player") -> None:
        self.player = player

    def get_inventory(self):
        updated_inventory = []
        for item in db.get_inventory():
            if item[1].type_ in ['weapon', 'armor']:
                updated_inventory.append((item[0], Equipment(item[1], self.player.drunk)))
            else:
                updated_inventory.append(item)
        return updated_inventory

    def show_inventory(self) -> None:
        """
        USER ACTION
        Shows inventory and lets to manage it
        """
        inventory = self.get_inventory()
        if inventory:

            # showing of items
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
            match type_of_item:
                case "food":
                    self.player.health += FOOD_HP
                    self.player.set_drunk(-FOOD_DRUNK_LOSS)
                    db.remove_item(inventory[item_index][0])
                    print(f"Your HP is {self.player.health} now")
                case "alcohol":
                    self.player.set_drunk(BEER_DRUNK)
                    db.remove_item(inventory[item_index][0])
                    print(f"You've drunk {item_name}")
                case "weapon":
                    if self.player.weapon and self.player.weapon.name == item_name:
                        db.put_on_off_item(self.player.weapon, state=False)
                        self.player.recount_params()
                        return
                    if self.player.weapon:
                        db.put_on_off_item(self.player.weapon, state=False)
                        db.put_on_off_item(inventory[item_index][0], state=True)
                    else:
                        db.put_on_off_item(inventory[item_index][0], state=True)
                    print(f"Current weapon: {item_name}")
                case "armor":
                    if self.player.armor and self.player.armor.name == item_name:
                        db.put_on_off_item(self.player.armor, state=False)
                        self.player.recount_params()
                        return
                    if self.player.armor:
                        db.put_on_off_item(self.player.armor, state=False)
                        db.put_on_off_item(inventory[item_index][0], state=True)
                    else:
                        db.put_on_off_item(inventory[item_index][0], state=True)
                    print(f"Current armor: {item_name}")
                case "loot":
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
        counter = 0
        for counter, item in enumerate(inventory, start=1):

            # todo: optimize again?
            active_weapon, active_armor = '', ''
            if self.player.weapon:
                if item[1].name == self.player.weapon.name:  # todo: may be weak spot, need to observe usefulness
                    active_weapon = color('okblue', ' active weapon')
            if self.player.armor:
                if item[1].name == self.player.armor.name:
                    active_armor = color('okblue', ' active armor')
            active_equipment = f"{active_weapon}{active_armor}"
            string = f"{counter} - {item[1].name if not isinstance(item[1], Equipment) else item[1]}" + f": {item[0].amount}" + active_equipment

            print(string)
        print("0 - cancel")
        return counter

    def get_chest_item(self) -> None:
        """
        USER ACTION
        Gives random item from chest to player
        """
        item = random.choice([x for x in db.get_all_items() if not x.boss and x.type_ != "loot"])
        print(f"You've found {item.name}")
        db.add_item_to_inventory(item.item_id)
        self.player.gold += (loot := random.randint(MIN_CHEST_GOLD_REWARD, MAX_CHEST_GOLD_REWARD))
        print(f"You've found {loot} gold coins")


class JsonToEquipment:
    def __init__(self, init_dict) -> None:
        for key, value in init_dict.items():
            setattr(self, key, value)
            match key:
                case "type":
                    self.type_ = init_dict["type"]
                case "levels":
                    self.levels = dumps(init_dict["levels"])


class Equipment:
    def __init__(self, item: db.Row, drunk: int) -> None:
        self._row = item
        drunk_stage = str(min(drunk // 25, 3))
        match self.type_:
            case 'weapon':
                self.attack = loads(self.levels).get(drunk_stage).get('attack')
                if not self.attack:
                    raise KeyError(f"Item {self.name} doesn't have stage {drunk_stage}")
            case 'armor':
                self.defence = loads(self.levels).get(drunk_stage).get('defence')
                if not self.defence:
                    raise KeyError(f"Item {self.name} doesn't have stage {drunk_stage}")
            case _:
                raise ValueError(f'{self.name} is not an equipment')
        self.effects = loads(self.levels).get(drunk_stage).get('effects')

    def __getattr__(self, attr):
        row = self.__dict__.get("_row", None)
        if row is None:
            raise AttributeError(attr)
        return getattr(row, attr)

    def __repr__(self) -> str:
        match self.type_:
            case 'weapon':
                effects = "".join(
                    [f" [+{effect['damage']} {get_effect_color(effect['name'])} damage]" for effect
                     in self.effects] if self.effects else "")
                return f"""{self.name} {f'(attack {self.attack})' if not self.effects
                else f'(attack {self.attack})'}{effects}"""
            case 'armor':
                effects = "".join(
                    [f" [+{effect['resist']} {get_effect_color(effect['name'])} resist]" for effect
                     in self.effects] if self.effects else "")
                return f"""{self.name} {f'(defence {self.defence})' if not self.effects
                else f'(defence {self.defence})'}{effects}"""
            case _:
                raise ValueError(f'{self.name} is not an equipment')
