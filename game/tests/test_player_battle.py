from unittest.mock import patch

import pytest

from enemy import Enemy
from tests.framework import *


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
def test_player_battle(mock_input):
    scene = world_creation()

    # set player's stats
    scene.player.drunk = 30
    scene.player.level = 1
    scene.player.health = 10
    scene.player.attack = 1
    scene.player.defence = 1
    scene.player.strength = 1
    scene.player.endurance = 1
    scene.player.agility = 1
    scene.player.luck = 1

    # add the main weapon
    db.add_item_to_game({'id': 666, 'name': 'any gun', 'type': 'weapon', 'attack': 0, 'cost': 1})  # set gun stats here
    db.add_item_to_inventory(666)
    inventory = db.get_inventory()
    db.put_on_off_item(inventory[0][0], on=True)
    scene.player.recount_params()

    # create the enemy
    scene.enemy = Enemy(player=scene.player)
    scene.enemy.name = "Wet dog"
    scene.enemy.level = 5
    scene.enemy.health = 5
    scene.enemy.attack = 1
    scene.enemy.defence = 1
    scene.enemy.agility = 10

    # start the battle
    scene.state = 'battle'

    # start test
    gen = turns_generator([4, 3, 0, 2, 1, 3, 1])
    mock_input.side_effect = lambda x: next(gen)
    try:
        while True:
            scene.show_current_scene()
    except StopIteration:
        etalon_log = read_file_ignoring_rows('etalon_battle.log', ignore=[122])
        actual_log = read_file_ignoring_rows('last_game.log', ignore=[122])
        assert etalon_log == actual_log
        compare_strings_ignore_numbers(get_row_from_file('etalon_battle.log', 122),
                                       get_row_from_file('last_game.log', 122))
