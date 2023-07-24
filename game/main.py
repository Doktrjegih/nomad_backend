import pickle

from location import Location
from player import Player
from scene import Scene


def main() -> None:
    """
    Entrypoint for game
    """
    print('Hello, a big new world!')
    player = Player()
    scene = Scene(location=Location(type_='hometown', player=player), player=player)
    with open('quests.pkl', 'wb') as fd:
        pickle.dump([], fd)
    scene.show_peace_scene()


if __name__ == '__main__':
    main()
