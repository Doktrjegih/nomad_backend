from unittest.mock import patch
from enemy import Enemy


def test_player_battle(game_world):
    game_world.enemy = Enemy(game_world.player, random_enemy=False, name='Wet dog')
    game_world.enemy.health = 1
    game_world.state = 'battle'
    hp = game_world.player.health
    gold = game_world.player.gold
    with patch('builtins.input', return_value='1'), patch('scene.random.randint', return_value=1):
        game_world.show_current_scene()
    assert game_world.state == 'peace'
    assert game_world.enemy is None
    assert game_world.player.health == hp  # Killing blow prevents retaliation.
    assert game_world.player.gold > gold
    assert game_world.player.battles_won == 1
    assert game_world.player.moves == 1
