import builtins
from unittest.mock import patch

import pytest

from quest import there_are_finished_quests, get_current_quests
from tests.framework import *

actions = None


def make_decision(scene: Scene) -> str:
    global actions

    # check continuous actions
    if actions:
        try:
            return next(actions)
        except StopIteration:
            pass

    # talk with carl
    if scene.state == 'npc':
        actions_list = ['1']
        if scene.location.chest:
            actions_list.append('2')
        actions = turns_generator(actions_list)
        return next(actions)

    # loot chests
    if scene.location.chest:
        return '2'

    # upgrade skills
    if scene.player.available_stats_point > 0:
        actions = turns_generator([open_entrypoint(scene, "get status"), '1', '1'])
        return next(actions)

    # get food, alcohol and better equipment
    inventory = db.get_inventory()
    food_alcohol = ["Beer bottle", "Steak"]
    for index, item in enumerate(inventory, start=1):
        if item[1].name in food_alcohol:
            actions = turns_generator([open_entrypoint(scene, "inventory"), index])
            return next(actions)
        if item[1].type_ == "weapon":
            if not scene.player.weapon or item[1].attack > scene.player.weapon.attack:
                actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                return next(actions)
        if item[1].type_ == "armor":
            if not scene.player.armor or item[1].defence > scene.player.armor.defence:
                actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                return next(actions)

    # enter the tavern
    if scene.location.tavern and scene.state != "tavern":
        return '2'

    # actions in the tavern
    if scene.state == 'tavern':
        actions_list = []
        if (available_purchase := scene.player.gold // 5) > 0:
            needed_operations = (scene.player.max_hp - scene.player.health) // 2
            while available_purchase > 0 and needed_operations > 0:
                available_purchase -= 1
                needed_operations -= 1
                actions_list.append('3')
            needed_operations = (100 - scene.player.drunk) // 10
            while available_purchase > 0 and needed_operations > 0:
                available_purchase -= 1
                needed_operations -= 1
                actions_list.append('2')

        # quests
        quests = get_current_quests()
        finished_quests = there_are_finished_quests(quests)
        if finished_quests or len(quests) < 3:
            if scene.tavern.merchant and scene.player.drunk > 24:
                actions_list.append('5')
            else:
                actions_list.append('4')
            if scene.tavern.active_quests:
                actions_list.append('1')

        # exit from tavern and go forward
        actions_list.extend(['1', '1'])
        actions = turns_generator(actions_list)
        return next(actions)

    # just go until death
    if scene.player.health > 0:
        return '1'


@patch("builtins.input")
@pytest.mark.usefixtures("clear_dir")
@pytest.mark.usefixtures("clear_results")
@pytest.mark.usefixtures("test_counter")
@pytest.mark.parametrize('run', range(10))
def test_autoplayer(mock_input, run) -> None:
    scene = world_creation()
    scene.player.name = "autoplayer"
    mock_input.side_effect = lambda x: make_decision(scene)
    try:
        while True:
            scene.show_current_scene()
    except Exception as e:
        builtins.print(e)
        with open("last_game.log") as fd:
            assert "GAME OVER!" in fd.read()
        with open("results.txt", "a") as fd:
            fd.write(f"total score = {scene.player.scores}\n")
