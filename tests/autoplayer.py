import random
from unittest.mock import patch
from json import loads
import pytest

from console import ExitException
from constants import *
from quest import there_are_finished_quests, get_current_quests, there_is_plot_quest
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
    # if scene.player.available_stats_point > 0:
    #     actions = turns_generator([open_entrypoint(scene, "get status"), '1', '1'])
    #     return next(actions)

    # get food, alcohol and better equipment
    inventory = scene.items.get_inventory()
    food_alcohol = ["Beer bottle", "Steak"]
    for index, item in enumerate(inventory, start=1):
        if item[1].name in food_alcohol:
            actions = turns_generator([open_entrypoint(scene, "inventory"), index])
            return next(actions)
        if item[1].type_ == "weapon":
            if not scene.player.weapon:
                actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                return next(actions)
            else:
                current_total_attack = scene.player.weapon.attack + sum([x.get('damage') for x in loads(scene.player.weapon.levels).get('3').get('effects')]) if scene.player.weapon.effects else 0
                new_total_attack = item[1].attack + sum([x.get('damage') for x in loads(item[1].levels).get('3').get('effects')]) if item[1].effects else 0
                if new_total_attack > current_total_attack:
                    actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                    return next(actions)
        if item[1].type_ == "armor":
            if not scene.player.armor:
                actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                return next(actions)
            else:
                current_total_defence = scene.player.armor.defence + sum([x.get('resist') for x in loads(scene.player.armor.levels).get('3').get('effects')]) if scene.player.armor.effects else 0
                new_total_defence = item[1].defence + sum([x.get('resist') for x in loads(item[1].levels).get('3').get('effects')]) if item[1].effects else 0
                if new_total_defence > current_total_defence:
                    actions = turns_generator([open_entrypoint(scene, "inventory"), index])
                    return next(actions)

    # enter the tavern
    if scene.location.tavern and scene.state != "tavern":
        return '2'

    # actions in the tavern
    if scene.state == 'tavern':
        actions_list = []
        if (available_purchase := scene.player.gold // FOOD_PRICE) > 0:
            needed_operations = (scene.player.max_hp - scene.player.health) // FOOD_HP
            while available_purchase > 0 and needed_operations > 0:
                available_purchase -= 1
                needed_operations -= 1
                actions_list.append('3')
        if (available_purchase := scene.player.gold // BEER_PRICE) > 0:
            needed_operations = (100 - scene.player.drunk) // BEER_DRUNK
            while available_purchase > 0 and needed_operations > 0:
                available_purchase -= 1
                needed_operations -= 1
                actions_list.append('2')

        # quests
        quests = get_current_quests(ignore_plot=True)
        finished_quests = there_are_finished_quests(quests)
        if finished_quests or len(quests) < 3:
            if scene.tavern.merchant and scene.tavern.aleg:
                actions_list.append('6')
            elif scene.tavern.merchant or scene.tavern.aleg:
                actions_list.append('5')
            else:
                actions_list.append('4')
            if scene.tavern.active_quests:
                actions_list.append('1')

        # check aleg
        if scene.tavern.aleg:
            if there_is_plot_quest():
                quests = get_current_quests()
                for quest in quests:
                    if quest.plot_quest and quest.is_finished:
                        # take random skill improvement if the plot quest is finished
                        actions_list.extend(['4', '1', str(random.randint(1, 4))])
            else:
                # to talk and accept a new quest
                actions_list.extend(['4', '1'])

        # exit from the tavern and go forward
        actions_list.extend(['1', '1'])
        actions = turns_generator(actions_list)
        return next(actions)

    # just going until death
    if scene.player.health > 0:
        return '1'


@patch("builtins.input")
# @pytest.mark.usefixtures("clear_dir")
@pytest.mark.usefixtures("clear_results")
# @pytest.mark.usefixtures("test_counter")
@pytest.mark.parametrize("run", range(100))
def test_autoplayer(mock_input, run) -> None:
    scene = world_creation()
    scene.player.name = "autoplayer"
    mock_input.side_effect = lambda x: make_decision(scene)
    with open("stats.csv", "a") as fd:
        try:
            step = 1
            while True:
                scene.show_current_scene()
                fd.write(
                    f"{step}, "
                    f"{scene.player.health}, "
                    f"{scene.player.max_hp}, "
                    f"{scene.player.drunk}, "
                    f"{scene.player.attack}, "
                    f"{scene.player.defence}, "
                    f"{scene.player.endurance}, "
                    f"{scene.player.strength}, "
                    f"{scene.player.agility}, "
                    f"{scene.player.luck}, "
                    f"{scene.player.gold}, "
                    f"{'tavern' if scene.location.tavern else ''}, "
                    f"{scene.player.plot_stage}, "
                    f"{scene.location.name}, "
                    f"{scene.enemy.name if scene.enemy else ''}, "
                    f"{scene.enemy.health if scene.enemy else ''}, "
                    f"{scene.enemy.attack if scene.enemy else ''}, "
                    f"{scene.enemy.defence if scene.enemy else ''}, "
                    f"{scene.enemy.special_name if hasattr(scene.enemy, 'special_name') else ''}, "
                    f"{'chest' if scene.location.chest else ''}, "
                    f"{'npc' if scene.location.npc else ''}, "
                    f"{scene.player.armor.name if scene.player.armor else ''}, "
                    f"{scene.player.weapon.name if scene.player.weapon else ''}\n"
                    )
                step += 1
        except ExitException:
            # with open("last_game.log") as fd:
            #     assert "GAME OVER!" in fd.read()
            # with open("results.txt", "a") as fd2:
            #     fd2.write(f"killed by = {scene.enemy.name}\n")
            # fd.write(f"killed by = {scene.enemy.name}\n")
            # fd.write("-" * 50 + '\n')
            fd.write("\n")
