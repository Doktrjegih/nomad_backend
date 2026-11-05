from unittest.mock import patch
import db


def test_inventory_check(game_world):
    db.add_item_to_inventory(3)
    with patch('builtins.input', return_value='1'):
        game_world.items.show_inventory()
    assert game_world.player.weapon is None
    with patch('builtins.input', return_value='1'):
        game_world.items.show_inventory()
    assert game_world.player.weapon.name == 'Broken Spear'
    spear = next(entry for entry, item in game_world.items.get_inventory() if item.item_id == 3)
    assert spear.amount == 2
    assert spear.used
