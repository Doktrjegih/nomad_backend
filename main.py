import os
import pickle
import sys

import pytest

import db
from console import print, start_logger
from items import Items
from location import Location
from paths import MAIN_FOLDER, TESTS, QUESTS
from player import Player
from scene import Scene


def run_unit_tests():
    """
    Runs all tests
    """
    start_logger()
    os.chdir(TESTS)
    result = pytest.main(['-x', '.'])
    if result != pytest.ExitCode.OK:
        sys.exit(1)
    os.chdir(MAIN_FOLDER)


def main() -> None:
    """
    Entrypoint for game
    """
    start_logger()
    db.create_database()
    print('Hello, a big new world!')
    player = Player()
    items = Items(player=player)
    scene = Scene(location=Location(type_='hometown', player_luck=player.luck), player=player, items=items)
    with open(QUESTS, 'wb') as fd:
        pickle.dump([], fd)
    db.add_item_to_inventory(1, 10)
    db.add_item_to_inventory(3 )
    while True:
        scene.show_current_scene()


if __name__ == '__main__':
    # run_unit_tests()
    main()
