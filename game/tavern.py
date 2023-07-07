import random

from enemy import Enemy
from quest import Quest


class Tavern:
    def __init__(self, scene, player) -> None:
        self.scene = scene
        self.player = player
        self.active_quests = True

    def tavern_menu(self) -> None:
        print(f"""\nYou're in the tavern""")
        print('drunk level:', self.player.get_condition())
        action = self.scene.show_possible_options()
        if action == "go out":
            self.scene.state = 'peace'
            self.scene.tavern = self
            self.scene.show_current_scene()
        elif action == "take a beer":
            self.buy_beer(1)
            self.tavern_menu()
        elif action == 'get quest':
            self.get_quest()
        elif action == "get status":
            self.player.show_player_info()
            self.tavern_menu()
        elif action == "exit game":
            exit()

    def buy_beer(self, beer: int) -> None:
        if self.player.gold < 10:
            print('not enough money, is 10 gold for beer')
            return
        self.player.drunk += beer
        if self.player.drunk > 10:
            self.player.drunk = 10
        self.player.gold -= 10

    def get_quest(self) -> None:
        if not self.active_quests:
            print("sorry, I don't have quests for you now")
            self.tavern_menu()
            return
        order = Enemy(self.player)
        amount = random.randint(2, 5)
        award = amount * 5

        print('\nHello stranger!')
        print(f'I need to clean this area from {order.name}s')
        print(f'Think {amount} ones will be enough for now')
        print(f'Award for this is {award} gold coins')
        answer = input(f'Are you accept? (yes/no)')
        if answer.lower() in ['y', 'yes']:
            print('quest has been taken')
            self.active_quests = False
            quest = Quest(order=order, amount=amount, award=award)
            quest.add_to_list()
            self.tavern_menu()
