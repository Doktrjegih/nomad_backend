from location import Location
from player import Player
from scene import Scene


def main():
    print('Hello, a big new world!')
    player = Player()
    scene = Scene(location=Location('hometown'), player=player)
    scene.show_peace_scene()


if __name__ == '__main__':
    main()
