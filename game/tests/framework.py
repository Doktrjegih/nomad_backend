import os
import pickle
from types import GeneratorType

import db
from console import print
from items import Items
from location import Location
from player import Player
from scene import Scene


def world_creation() -> Scene:
    try:
        os.remove('last_game.log')
    except FileNotFoundError:
        pass
    db.create_database()
    print('Hello, a big new world!')
    player = Player()
    items = Items(player=player)
    scene = Scene(location=Location(type_='hometown', player=player), player=player, items=items)
    with open('quests.pkl', 'wb') as fd:
        pickle.dump([], fd)
    return scene


def turns_generator(data) -> GeneratorType:
    for item in data:
        yield str(item)
