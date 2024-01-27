import linecache
import os
import pickle
import re
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
    scene = Scene(location=Location(type_='hometown', player_luck=player.luck), player=player, items=items)
    with open(os.path.join(os.getcwd(), "quests.pkl"), 'wb') as fd:
        pickle.dump([], fd)
    return scene


def turns_generator(data) -> GeneratorType:
    for item in data:
        yield str(item)


def open_entrypoint(scene: Scene, name: str) -> int:
    options = scene.get_possible_options()
    return options.index(name) + 1


def read_rows_in_range(file_path, start_row: int, finish_row: int) -> str:
    if start_row >= finish_row:
        raise ValueError('Start row must be less than finish')
    content = ""
    with open(file_path, 'r') as file:
        for counter, line in enumerate(file, start=1):
            if counter < start_row:
                continue
            if counter > finish_row:
                break
            content += line
    return content


def read_file_ignoring_rows(file_path: str, ignore: list[int]) -> str:
    content = ""
    with open(file_path, 'r') as file:
        for counter, line in enumerate(file, start=1):
            if counter in ignore:
                continue
            content += line
    return content


def compare_strings_ignore_numbers(str1: str, str2: str) -> None:
    str1_without_numbers = re.sub(r'\d', '', str1)
    str2_without_numbers = re.sub(r'\d', '', str2)
    assert str1_without_numbers == str2_without_numbers


def get_row_from_file(file_path, row: int) -> str:
    return linecache.getline(file_path, row)
