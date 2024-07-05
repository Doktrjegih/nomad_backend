from unittest.mock import patch
import pytest
from tests.framework import world_creation, turns_generator, assert_files_equal
from pathlib import Path
import db

tests_folder = Path(__file__).parent


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
        assert_files_equal(Path(tests_folder, 'etalon_inventory_checks.log'), Path(tests_folder.parent, 'last_game.log'))
