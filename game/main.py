import os
import pickle
import sys

import pytest

import db
from console import print
from items import Items
from location import Location
from player import Player
from scene import Scene


def run_unit_tests():
    """
    Runs all tests
    """
    os.chdir('tests')
    result = pytest.main(['-x', '.'])
    if result != pytest.ExitCode.OK:
        sys.exit(1)
    os.chdir(os.path.dirname(__file__))


def main() -> None:
    """
    Entrypoint for game
    """
    try:
        os.remove('last_game.log')
    except FileNotFoundError:
        pass
    db.create_database()
    print('Hello, a big new world!')
    player = Player()
    items = Items(player=player)
    scene = Scene(location=Location(type_='hometown', player=player), player=player, items=items)
    with open(os.path.join(os.getcwd(), "quests.pkl"), 'wb') as fd:
        pickle.dump([], fd)
    scene.show_peace_scene()


if __name__ == '__main__':
    run_unit_tests()
    main()
