from unittest.mock import patch
import pytest
from pathlib import Path
from tests.framework import world_creation, turns_generator, assert_files_equal

tests_folder = Path(__file__).parent


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
def test_initial_checks(mock_input):
    scene = world_creation()

    gen = turns_generator([2, 2, 3, 5, 6, 7, 2, 1])  # todo: add "exit" option log
    # enter tavern
    # buy beer
    # buy steak
    # check inventory
    # get status
    # click exit
    # cancel exiting
    # go outside

    mock_input.side_effect = lambda x: next(gen)
    try:
        while True:
            scene.show_current_scene()
    except StopIteration:
        assert_files_equal(Path(tests_folder, 'etalon_initial_checks.log'),
                           Path(tests_folder.parent, 'last_game.log'))
