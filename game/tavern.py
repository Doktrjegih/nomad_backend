import random

from enemy import Enemy
from quest import Quest, get_current_quests


class Tavern:
    def __init__(self, scene, player) -> None:
        self.tavern_quest = None
        self.scene = scene
        self.player = player
        self.active_quests = True

    def tavern_menu(self) -> None:
        """
        USER ACTION
        Shows tavern menu
        """
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
        elif action == 'check quests':
            self.check_quests()
        elif action == "get status":
            self.player.show_player_info()
            self.tavern_menu()
        elif action == "exit game":
            exit()

    def buy_beer(self, beer: int) -> None:
        """
        USER ACTION
        Buy a cup of beer for 10 coins, increases Player.drunk level
        """
        if self.player.gold < 10:
            print('not enough money, is 10 gold coins for beer')
            return
        self.player.drunk += beer
        self.player.health += 2
        if self.player.health > 10:
            self.player.health = 10
        if self.player.drunk > 10:
            self.player.drunk = 10
        self.player.gold -= 10

    def check_quests(self) -> None:
        """
        USER ACTION
        Checks if there are finished quests, closes quests if yes.
        Generates random new tasks for player, restricts getting of quests if player already has active mission
        """
        quests = get_current_quests()
        if quests:
            if quests[0].is_finished:
                quests[0].close_quest(self.player)
                self.active_quests = True
        if not self.active_quests:
            print("sorry, I don't have quests for you now")
            self.tavern_menu()
            return
        if not self.tavern_quest:
            order = Enemy(self.player)
            amount = random.randint(2, 5)
            award = amount * 5
            quest = Quest(order=order, amount=amount, award=award)
            self.tavern_quest = quest

        print('\nHello stranger!')
        print(f'I need to clean this area from {self.tavern_quest.order.name}s')
        print(f'Think {self.tavern_quest.goal_amount} ones will be enough for now')
        print(f'Award for this is {self.tavern_quest.award} gold coins')

        while True:
            answer = input(f'Are you accept? (yes/no)')
            if answer.lower() in ['y', 'yes', '1']:
                print('quest has been taken')
                self.active_quests = False
                self.tavern_quest.add_to_list()
                self.tavern_menu()
            elif answer.lower() in ['n', 'no', '2']:
                self.tavern_menu()
            else:
                print('ERROR! incorrect input')
