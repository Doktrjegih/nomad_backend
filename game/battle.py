from console import warning


class Battle:
    def __init__(self, scene, player, enemy):
        self.scene = scene
        self.player = player
        self.enemy = enemy
        self.damage_taken = 0

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
            attack = self.player.attack - self.enemy.defence
            if attack < 1:
                attack = 1
            print(f'Your attack is {attack}')
            self.enemy.get_damage(attack)
            if self.enemy.health <= 0:
                self.enemy.died()
                self.finish_battle(type_='battle')
            else:
                self.damage_taken += self.enemy.enemy_attack()
                self.show_battle_scene()
        elif action == "run away":
            self.try_run_away()
        elif action == "inventory":
            self.player.show_inventory()
            self.scene.show_current_scene()
        elif action == "get status":
            self.player.show_player_info()
            self.scene.show_current_scene()
        elif action == "exit game":
            self.scene.ask_about_exit()

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
        self.scene.show_current_scene()
