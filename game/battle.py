import random

from console import *
from console import color, print


class Battle:
    def __init__(self, scene):
        self.scene = scene
        self.player = self.scene.player
        self.enemy = scene.enemy
        self.damage_taken = 0
        self.items = self.scene.items

    def show_battle_scene(self) -> None:
        """
        Shows process of the battle
        """
        print(f"""\nYou're in the location "{self.scene.location.name}" ({self.scene.location.type}) """)
        warning('Battle mode')
        print('Drunk level:', self.player.get_condition())
        self.enemy.show_rivals_stats()
        action = self.scene.show_possible_options()
        if action == "attack":
            self.player_attack()
        elif action == "run away":
            self.try_run_away()
        elif action == "inventory":
            self.items.show_inventory()
            return
        elif action == "get status":
            self.player.show_player_info()
            return
        elif action == "exit game":
            self.scene.ask_about_exit()

    def player_attack(self):
        # todo: docstring
        attack = self.player.attack - self.enemy.defence
        if attack < 1:
            attack = 1
        lucky_hit, critical_hit = '', ''
        if self.player.luck > random.randint(1, 100):
            lucky_hit = color('green', 'Lucky hit! ')
        if self.player.luck / 2 + self.player.agility > random.randint(1, 100):
            critical_hit = color('green', 'CRITICAL HIT! ')
        lucky_hit = '' if critical_hit else lucky_hit
        if lucky_hit:
            attack = int(attack * 1.2)
        if critical_hit:
            attack = int(attack * 1.5)
        print(f'{lucky_hit}{critical_hit}Your default attack is {self.player.attack}')
        print(f'{lucky_hit}Enemy defence is {self.enemy.defence}')
        print(f'{lucky_hit}Your actual attack is {attack}')
        self.enemy.get_damage(attack)
        if self.enemy.health <= 0:
            self.enemy.died()
            self.finish_battle(type_='battle')
        else:
            self.enemy.check_specials()
            self.damage_taken += self.enemy.enemy_attack()
            self.show_battle_scene()

    def try_run_away(self) -> None:
        """
        USER ACTION
        Trying to run away from enemy, if attempt is failed, blocks next attempts
        """
        if self.player.agility > self.enemy.agility:
            print('You have ran away')
            self.finish_battle('run')
        else:
            diff = self.enemy.agility - self.player.agility
            if self.player.luck > diff:
                print('Your luck let you to run away')
                self.finish_battle('run')
            else:
                print("You couldn't run away")
                self.enemy.enemy_attack()
                self.scene.run_able = False
                self.show_battle_scene()

    def finish_battle(self, type_: str) -> None:
        """
        Finishes battle
        """
        self.enemy = None
        self.scene.run_able = True
        self.scene.state = 'peace'
        if type_ == 'run':
            self.player.set_drunk(-1)
        elif type_ == 'battle':
            self.player.set_drunk(-3)  # todo: depends on taken damage
        # print(f'Damage taken during battle: {self.damage_taken}')
        return
