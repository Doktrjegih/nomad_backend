import random

from enemy import Enemy
from quest import Quest, get_current_quests
from player import Player
from console import error, color


class Tavern:
    def __init__(self, scene, player: Player) -> None:
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
        print('Drunk level:', self.player.get_condition())
        action = self.scene.show_possible_options()
        if action == "go out":
            self.scene.state = 'peace'
            self.scene.tavern = self
            self.scene.show_current_scene()
        elif action == "take a beer":
            self.buy_beer(10)
            self.tavern_menu()
        elif action == "take a steak":
            self.buy_steak()
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
        Buy a cup of beer for 5 coins, increases Player.drunk level
        """
        if self.player.gold < 5:
            print("Not enough money, it's 5 gold coins for beer")
            return
        self.player.set_drunk(beer)
        self.player.gold -= 5

    def buy_steak(self) -> None:
        """
        USER ACTION
        Buy a steak for 5 coins, increases Player.health level
        """
        if self.player.gold < 5:
            print("Not enough money, it's 5 gold coins for steak")
            return
        self.player.health += 2
        self.player.set_drunk(-3)
        if self.player.health > self.player.max_hp:
            self.player.health = self.player.max_hp
        self.player.gold -= 5

    def check_quests(self) -> None:
        """
        USER ACTION
        Checks if there are finished quests, closes quests if yes.
        Generates random new tasks for player, restricts getting of quests if player already has active mission
        """
        # check if there are finished quests
        quests = get_current_quests()
        if quests:
            for quest in quests:
                if quest.is_finished:
                    quest.close_quest(self.player)

        # check if max value of current quests
        quests = get_current_quests()
        if len(quests) == 3 or not self.active_quests:
            print("Sorry, I don't have quests for you now")
            self.tavern_menu()
            return

        # check if tavern quest was taken
        if not self.tavern_quest:
            if len(quests) == 0:
                order = Enemy(self.player)
            else:
                current_orders = []
                for quest in quests:
                    current_orders.append(quest.order.type)
                order = Enemy(self.player, exclude=current_orders)
            amount = random.randint(2, 5)
            reward = amount * 5 * self.player.level + (random.randint(2, 10) * self.player.level)
            quest = Quest(order=order, amount=amount, reward=reward)
            self.tavern_quest = quest

        print('\nHello stranger!')
        print(f'I need to clean this area from {color("red", self.tavern_quest.order.name + "s")}')
        print(f'Think {self.tavern_quest.goal_amount} ones will be enough for now')
        print(f'Reward for this is {self.tavern_quest.reward} gold coins')

        while True:
            answer = input(f'Are you accept? (yes/no) ')
            if answer.lower() in ['y', 'yes', '1']:
                print('Quest has been taken')
                self.active_quests = False
                self.tavern_quest.add_to_list()
                self.tavern_menu()
            elif answer.lower() in ['n', 'no', '2']:
                self.tavern_menu()
            else:
                error('Incorrect input')
