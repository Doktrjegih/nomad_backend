import os
import pickle
import sys

import pytest
from pathlib import Path
import db
from console import print, start_logger
from items import Items
from location import Location
from player import Player
from scene import Scene

main_folder = Path(__file__).parent


def run_unit_tests():
    """
    Runs all tests
    """
    start_logger()
    os.chdir('tests')
    result = pytest.main(['-x', '.'])
    if result != pytest.ExitCode.OK:
        sys.exit(1)
    os.chdir(os.path.dirname(__file__))


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
    with open(Path(main_folder, "quests.pkl"), 'wb') as fd:
        pickle.dump([], fd)
    while True:
        scene.show_current_scene()


if __name__ == '__main__':
    run_unit_tests()
    main()
