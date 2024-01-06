from unittest.mock import patch

import pytest

from tests.framework import *


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
def test_inventory_check(mock_input):
    scene = world_creation()

    scene.player.drunk = 25
    db.add_item_to_inventory(3)

    gen = turns_generator([4, 3, 1, 3, 0, 4])
    mock_input.side_effect = lambda x: next(gen)
    try:
        while True:
            scene.show_current_scene()
    except StopIteration:
        with open('etalon_inventory_checks.log', 'r') as fd:
            with open('last_game.log', 'r') as fd2:
                assert fd2.read() == fd.read()
