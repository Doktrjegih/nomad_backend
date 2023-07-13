import pickle

from location import Location
from player import Player
from scene import Scene
from console import console


def main() -> None:
    print('Hello, a big new world!')
    # console('Hello, a big new world!')
    player = Player()
    scene = Scene(location=Location('hometown'), player=player)
    with open('quests.pkl', 'wb') as fd:
        pickle.dump([], fd)
    scene.show_peace_scene()


if __name__ == '__main__':
    main()
