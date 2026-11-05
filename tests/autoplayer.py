import random
from json import loads
from unittest.mock import patch

import pytest

from console import ExitException
from constants import *
from quest import there_are_finished_quests, get_current_quests, there_is_plot_quest
from tests.framework import *

actions = None


def equipment_score(item) -> float:
    """Compare current-tier stats; physical gear remains useful without effects."""
    if item.type_ == "weapon":
        return item.attack + sum(effect.get("damage", 0) for effect in item.effects or [])
    return item.defence + sum(effect.get("resist", 0) for effect in item.effects or [])


def make_decision(scene: Scene) -> str:
    global actions
    if actions:
        try:
            return next(actions)
        except StopIteration:
            actions = None

    def queue(values):
        global actions
        actions = turns_generator(values)
        return next(actions)

    if scene.state == "npc":
        return queue(['1', '2'] if scene.location.chest else ['1'])
    if scene.location.chest and scene.state == "peace":
        return str(open_entrypoint(scene, "check a chest"))

    for index, (entry, item) in enumerate(scene.items.get_inventory(), start=1):
        if item.type_ == "food" and scene.player.health <= scene.player.max_hp - FOOD_HP:
            return queue([open_entrypoint(scene, "inventory"), index])
        if item.type_ == "alcohol" and scene.player.drunk <= 10:
            return queue([open_entrypoint(scene, "inventory"), index])
        if item.type_ in ("weapon", "armor"):
            current = getattr(scene.player, item.type_)
            if not current or equipment_score(item) > equipment_score(current):
                return queue([open_entrypoint(scene, "inventory"), index])

    if scene.state == "peace" and scene.location.tavern:
        return str(open_entrypoint(scene, "enter tavern"))
    if scene.state == "tavern":
        plan = []
        budget = scene.player.gold
        meals = min(budget // FOOD_PRICE,
                    (scene.player.max_hp - scene.player.health + FOOD_HP - 1) // FOOD_HP)
        plan.extend(['3'] * meals)
        budget -= meals * FOOD_PRICE
        beers = min(budget // BEER_PRICE, max(0, (20 - scene.player.drunk) // BEER_DRUNK))
        plan.extend(['2'] * beers)
        quests = get_current_quests(ignore_plot=True)
        if there_are_finished_quests(quests) or (len(quests) < 3 and scene.tavern.active_quests):
            plan.append(open_entrypoint(scene, "check quests"))
            if len([q for q in quests if not q.is_finished]) < 3 and scene.tavern.active_quests:
                plan.append('1')
        plot = [q for q in get_current_quests() if q.plot_quest]
        if scene.tavern.aleg and (not plot or plot[0].is_finished):
            plan.append(open_entrypoint(scene, "talk with Aleg"))
            if plot:
                # Alternate offence and defence upgrades rather than unused stats.
                plan.extend(['1', '2' if scene.player.strength <= scene.player.agility else '3'])
            plan.append('1')
        plan.extend(['1', '1'])
        return queue(plan)
    return '1'


@patch("builtins.input")
# @pytest.mark.usefixtures("clear_dir")
@pytest.mark.usefixtures("clear_results")
# @pytest.mark.usefixtures("test_counter")
@pytest.mark.parametrize("run", range(100))
def test_autoplayer(mock_input, run) -> None:
    global actions
    actions = None
    random.seed(run)
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
