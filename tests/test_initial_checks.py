from pathlib import Path
from unittest.mock import patch

import pytest

from paths import LAST_GAME_LOG, TESTS
from tests.framework import world_creation, turns_generator, assert_files_equal

tests_folder = Path(__file__).parent


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
def test_initial_checks(mock_input):
    scene = world_creation()

    gen = turns_generator([2, 2, 3, 7, 8, 9, 2, 1])  # todo: add "exit" option log
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
        assert_files_equal(Path(TESTS, 'etalon_initial_checks.log'),
                           LAST_GAME_LOG)
