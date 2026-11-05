"""Regression checks for progression and combat, independent of rendered logs."""
import random
from unittest.mock import patch

import pytest
from enemy import Boss, Enemy, generate_enemy
from quest import Quest


@pytest.mark.parametrize('name', ['Van Helsing', 'Aleg'])
def test_boss_has_real_template_and_health(game_world, name):
    boss = Boss(game_world.player, name)
    assert boss.name == name and boss.boss
    assert boss.health == boss.max_hp > 50
    assert boss.attack > 0 and boss.defence > 0


def test_endurance_does_not_scale_enemy_health(game_world):
    random.seed(5)
    first = Enemy(game_world.player)
    game_world.player.endurance += 3
    game_world.player.recount_params()
    random.seed(5)
    second = Enemy(game_world.player)
    assert game_world.player.max_hp == 160
    assert first.health == second.health


def test_agility_improves_defence_independently(game_world):
    attack, defence = game_world.player.attack, game_world.player.defence
    game_world.player.agility += 1
    game_world.player.recount_params()
    assert game_world.player.attack == attack
    assert game_world.player.defence > defence


def test_alcohol_does_not_change_enemy_tier(game_world):
    game_world.player.plot_stage = 2
    for alcohol in [0, 25, 26, 50, 100]:
        game_world.player.set_drunk(alcohol - game_world.player.drunk)
        assert generate_enemy(game_world.player).stage == 2


def test_travel_guarantees_safe_tavern(game_world):
    game_world.turns_without_tavern = 8
    game_world.turns_in_biome_left = 2
    game_world.new_scene()
    assert game_world.location.tavern
    assert not game_world.location.enemies
    assert game_world.player.travel_moves == game_world.player.moves == 1


def test_starter_damage_is_not_floored_at_one(game_world):
    game_world.enemy = Enemy(game_world.player, random_enemy=False, name='Wet dog')
    game_world.enemy.defence = 15
    game_world.enemy.health = 1000
    hp = game_world.enemy.health
    with patch('scene.random.randint', return_value=1):
        game_world.player_attack()
    assert hp - game_world.enemy.health >= 4


def test_regular_upgrade_rewards(game_world):
    for _ in range(4):
        game_world.finish_battle()
    inventory = {item.item_id for _, item in game_world.items.get_inventory()}
    assert {99, 95} <= inventory


def test_plot_boss_reachable_in_any_biome(game_world):
    Quest('Van Helsing', 1, is_plot=True, boss=True).add_to_list()
    with patch('enemy.random.random', return_value=0):
        enemy = generate_enemy(game_world.player)
    assert enemy.name == 'Van Helsing' and enemy.boss


def test_luck_improves_accuracy(game_world):
    game_world.enemy = Enemy(game_world.player, random_enemy=False, name='Wet dog')
    game_world.enemy.health = 1000
    with patch('scene.random.randint', return_value=92):
        game_world.player_attack()
        assert game_world.enemy.health == 1000
        game_world.player.luck = 3
        game_world.player_attack()
        assert game_world.enemy.health < 1000


def test_hyena_rage_does_not_stack(game_world):
    enemy = Enemy(game_world.player, random_enemy=False, name='Hyena', stage=2)
    base = enemy.attack
    enemy.health = 1
    enemy.hyena()
    first = enemy.attack
    enemy.hyena()
    assert first == enemy.attack == round(base * 1.5)


def test_seeded_game_reaches_a_real_ending(tmp_path):
    import csv
    from pathlib import Path
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, 'tools/balance_simulation.py', '--runs', '1', '--seed', '100',
         '--output', str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1], check=True, timeout=30,
        capture_output=True, text=True,
    )
    with (tmp_path / 'results.csv').open() as stream:
        result = next(csv.DictReader(stream))
    assert result['outcome'] == 'win'
    assert 100 <= int(result['moves']) <= 500
    assert 'You win!' in (tmp_path / 'game-100.txt').read_text()
