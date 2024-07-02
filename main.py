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
        with open("last_game.log", "w") as fd:
            fd.write("")
    except FileNotFoundError:
        pass
    db.create_database()
    print('Hello, a big new world!')
    player = Player()
    items = Items(player=player)
    # db.add_item_to_inventory(3)
    # db.add_item_to_inventory(5)
    # for item in db.get_inventory():
    #     db.put_on_off_item(item, state=True)
    # player.recount_params()
    scene = Scene(location=Location(type_='hometown', player_luck=player.luck), player=player, items=items)
    with open(os.path.join(os.getcwd(), "quests.pkl"), 'wb') as fd:
        pickle.dump([], fd)
    while True:
        scene.show_current_scene()


if __name__ == '__main__':
    # run_unit_tests()
    main()
