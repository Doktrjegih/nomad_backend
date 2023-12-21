import os
import pickle

import db
from console import print
from items import Items
from location import Location
from player import Player
from scene import Scene

base_path = os.getcwd()
quests_file = os.path.join(base_path, "quests.pkl")


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
    with open(quests_file, 'wb') as fd:
        pickle.dump([], fd)
    scene.show_peace_scene()


if __name__ == '__main__':
    main()
