import json
import os

from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

base_path = os.path.dirname(__file__)
db_path = os.path.join(base_path, "sqalch.sqlite")
items_path = os.path.join(base_path, "items.json")

engine = create_engine(f'sqlite:///{db_path}', echo=False)
base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# with open(items_path, 'r', encoding='utf-8') as fd:
#     GAME_ITEMS = json.load(fd)


# class Items(base):
#     __tablename__ = 'items'

#     item_id = Column(Integer, primary_key=True)
#     name = Column(String)
#     type_ = Column(String)
#     attack = Column(Integer)
#     defence = Column(Integer)
#     boss = Column(String)
#     effect = Column(String)
#     effect_damage = Column(Integer)
#     effect_resist = Column(Integer)
#     effect_vulnerability = Column(Integer)
#     cost = Column(Integer)

#     def __init__(self, item_id, name, type_, cost, attack, defence, boss, effect, effect_damage, effect_resist, effect_vulnerability):
#         self.item_id = item_id
#         self.name = name
#         self.type_ = type_
#         self.attack = attack
#         self.defence = defence
#         self.cost = cost
#         self.boss = boss
#         self.effect = effect
#         self.effect_damage = effect_damage
#         self.effect_resist = effect_resist
#         self.effect_vulnerability = effect_vulnerability


class Inventory(base):
    __tablename__ = 'inventory'

    item_id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    used = Column(Boolean)

    def __init__(self, item_id, amount, used):
        self.item_id = item_id
        self.amount = amount
        self.used = used


def create_database() -> None:
    """
    Creates database if it's needed, clear DB before new game if it exists
    """
    if not os.path.exists(db_path):
        base.metadata.create_all(engine)
    else:
        inv_items = session.query(Inventory).all()
        for item in inv_items:
            session.delete(item)
        # items = session.query(Items).all()
        # for item in items:
        #     session.delete(item)
    session.commit()
    # for item in GAME_ITEMS:
    #     add_item_to_game(item)


# def add_item_to_game(data: dict) -> None:
#     """
#     Add a new game item to database
#     :param data: contains params for new item
#     """
#     item_id = data["id"]
#     name = data["name"]
#     type_ = data["type"]
#     attack = data.get("attack")
#     defence = data.get("defence")
#     boss = data.get("boss")
#     cost = data["cost"]
#     effect = data.get("effect")
#     effect_damage = data.get("effect_damage")
#     effect_resist = data.get("effect_resist")
#     effect_vulnerability = data.get("effect_vulnerability")

#     tr = Items(item_id, name, type_, attack, defence, boss, cost, effect, effect_damage, effect_resist, effect_vulnerability)
#     session.add(tr)
#     session.commit()


def add_item_to_inventory(item_id: int, amount: int = 1) -> None:
    """
    Add an item to player inventory table
    :param item_id: contains id of adding item
    :param amount: contains amount of adding item (1 by default)
    """
    item = session.query(Inventory).filter(Inventory.item_id == item_id).first()
    if item:
        item.amount += 1
    else:
        tr = Inventory(item_id=item_id, amount=amount, used=False)
        session.add(tr)
    session.commit()


# def get_all_items() -> list:
#     """
#     Returns all game items
#     :return: list of items
#     """
#     return session.query(Items).all()


# def get_item_by_name(name: str) -> type(Items):
#     """
#     Returns specified game item
#     :return: one item
#     """
#     return session.query(Items).filter(Items.boss == name).first()


# def get_inventory() -> list[tuple[Inventory, Items]]:
def get_inventory() -> list[Inventory]:
    """
    Returns inventory items
    :return: list of items in player inventory
    """
    # if inventory := session.query(Inventory, Items).select_from(Inventory).join(Items, Inventory.item_id == Items.item_id).all():
    if inventory := session.query(Inventory).select_from(Inventory).all():
        return inventory
    return []


def remove_item(item: Inventory, amount: int = 1) -> None:
    """
    Removes item from inventory, reduces amount if possible
    :param item: Inventory object to removing
    :param amount: specifies amount of removing items
    """
    item = session.query(Inventory).filter(Inventory.item_id == item.item_id).first()
    if item.amount > amount:
        item.amount -= amount
    elif item.amount == amount:
        session.delete(item)
    session.commit()


def put_on_off_item(item: Inventory, state: bool) -> None:
    """
    :param item: Inventory object to removing
    :param on: if True, puts on the item, otherwise puts off
    """
    item = session.query(Inventory).filter(Inventory.item_id == item.item_id).first()
    item.used = state
    session.commit()
