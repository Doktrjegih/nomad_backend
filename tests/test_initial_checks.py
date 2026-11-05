from unittest.mock import patch


def test_initial_checks(game_world):
    # Visit tavern, buy beer/food, inspect inventory/status, cancel exit, leave.
    with patch('builtins.input', side_effect=['2', '2', '3', '7', '0', '8', '9', '2', '1']):
        for _ in range(7):
            game_world.show_current_scene()
    assert game_world.state == 'peace'
    assert game_world.player.gold == 0
    assert game_world.player.health == game_world.player.max_hp
    assert game_world.player.drunk == 8
    assert game_world.player.weapon.name == 'Broken Spear'
    assert game_world.player.armor.name == "Anthoha's underpants"
