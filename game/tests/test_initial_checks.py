from unittest.mock import patch

import pytest

from tests.framework import *


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
def test_initial_checks(mock_input):
    scene = world_creation()

    gen = turns_generator([2, 2, 3, 5, 6, 7, 2, 1])  # todo: add "exit" option log
    mock_input.side_effect = lambda x: next(gen)
    try:
        while True:
            scene.show_current_scene()
    except StopIteration:
        with open('etalon_initial_checks.log', 'r') as fd:
            with open('last_game.log', 'r') as fd2:
                assert fd2.read() == fd.read()
