class Battle:
    def __init__(self, scene, player, enemy):
        self.scene = scene
        self.player = player
        self.enemy = enemy

    def show_battle_scene(self) -> None:
        print(f"""\nYou're in the location "{self.scene.location.name}" ({self.scene.location.type}) """)
        print('\nWARNING! Battle mode')
        print('drunk level:', self.player.drunk)
        self.enemy.show_enemy_stats()
        action = self.scene.show_possible_options()
        if action == "attack":
            attack = self.player.attack - self.enemy.defence
            print(f'your attack is {attack}')
            self.enemy.get_damage(attack)
            if self.enemy.health <= 0:
                self.enemy.died()
                self.finish_battle()
            else:
                self.enemy.enemy_attack()
                self.show_battle_scene()
        elif action == "run away":
            self.try_run_away()
        elif action == "get status":
            self.player.show_player_info()
            self.scene.show_current_scene()
        elif action == "exit game":
            exit()

    def try_run_away(self) -> None:
        if self.player.agility > self.enemy.agility:
            print('you have ran away')
            self.finish_battle()
        else:
            diff = self.enemy.agility - self.player.agility
            if self.player.luck > diff:
                print('your luck let you to run away')
                self.finish_battle()
            else:
                print("you couldn't run away")
                self.enemy.enemy_attack()
                self.scene.run_able = False
                self.show_battle_scene()

    def finish_battle(self) -> None:
        self.enemy = None
        self.scene.run_able = True
        self.scene.state = 'peace'
        self.scene.show_current_scene()
