import json

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///sqalch.sqlite', echo=False)
base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

with open('items.json', 'r', encoding='utf-8') as fd:
    GAME_ITEMS = json.load(fd)


class Items(base):
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True)
    name = Column(String)
    type_ = Column(String)
    attack = Column(Integer)
    cost = Column(Integer)

    def __init__(self, item_id, name, type_, attack, cost):
        self.item_id = item_id
        self.name = name
        self.type_ = type_
        self.attack = attack
        self.cost = cost


class Inventory(base):
    __tablename__ = 'inventory'

    item_id = Column(Integer, primary_key=True)
    amount = Column(Integer)

    def __init__(self, item_id, amount):
        self.item_id = item_id
        self.amount = amount


def create_database() -> None:
    """
    Creates database if it's needed, clear DB before new game if it exists
    """
    base.metadata.create_all(engine)
    session.query(Items).delete()
    session.query(Inventory).delete()
    session.commit()
    for item in GAME_ITEMS:
        add_item_to_game(item)


def add_item_to_game(data: dict) -> None:
    """
    Add a new game item to database
    :param data: contains params for new item
    """
    item_id = data["id"]
    name = data["name"]
    type_ = data["type"]
    attack = data["attack"]
    cost = data["cost"]

    tr = Items(item_id=item_id, name=name, type_=type_, attack=attack, cost=cost)
    session.add(tr)
    session.commit()


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
        tr = Inventory(item_id=item_id, amount=amount)
        session.add(tr)
    session.commit()


def get_all_items() -> list:
    """
    Returns all game items
    :return: list of items
    """
    return session.query(Items).all()


def get_item(item_id: int) -> type(Items):
    """
    Returns specified game item
    :return: one item
    """
    return session.query(Items).filter(Items.item_id == item_id).first()


def get_inventory() -> list:
    """
    Returns inventory items
    :return: list of items in player inventory
    """
    if inventory := session.query(Inventory, Items).select_from(Inventory).join(Items, Inventory.item_id == Items.item_id).all():
        return inventory
    else:
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
