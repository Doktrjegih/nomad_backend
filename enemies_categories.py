from dataclasses import dataclass

from constants import *


@dataclass(frozen=True)
class EnemyTemplate:
    name: str
    attack: int
    defence: int


ENEMIES_PARAMS = {
    "humans": {
        1: EnemyTemplate("Homeless guy", ATK_LV_1, DEF_LV_1),
        2: EnemyTemplate("Bandit", ATK_LV_2, DEF_LV_2),
        3: EnemyTemplate("Knight", ATK_LV_3, DEF_LV_3),
        4: EnemyTemplate("Berserk", ATK_LV_4, DEF_LV_4),
    },
    "dogs": {
        1: EnemyTemplate("Wet dog", ATK_LV_1, DEF_LV_1),
        2: EnemyTemplate("Hyena", ATK_LV_2, DEF_LV_2),
        3: EnemyTemplate("Wolf", ATK_LV_3, DEF_LV_3),
        4: EnemyTemplate("Werewolf", ATK_LV_4, DEF_LV_4),
    },
    "test": {
        1: EnemyTemplate("test1", ATK_LV_1, DEF_LV_1),
        2: EnemyTemplate("test2", ATK_LV_2, DEF_LV_2),
        3: EnemyTemplate("test3", ATK_LV_3, DEF_LV_3),
        4: EnemyTemplate("test4", ATK_LV_4, DEF_LV_4),
    },
}
