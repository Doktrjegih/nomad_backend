import dill as pickle

from console import print
from paths import QUESTS


def get_current_quests(ignore_plot: bool = False) -> list:
    """
    Reads active quests from pickle file as list of objects
    :return: list of Enemy objects or None
    """
    try:
        with open(QUESTS, 'rb') as fd:
            data = pickle.load(fd)
        return data if not ignore_plot else [quest for quest in data if not quest.plot_quest]
    except EOFError:
        return list()


def there_are_finished_quests(quests: list) -> bool:
    for quest in quests:
        quest: Quest
        if quest.is_finished:
            return True
    return False


def there_is_plot_quest():
    quests = get_current_quests()
    for quest in quests:
        quest: Quest
        if quest.plot_quest:
            return quest
    return None


class Quest:
    def __init__(self, order, amount, reward=0, is_plot=False) -> None:
        self.order = order
        self.goal_amount = amount
        self.current_amount = 0
        self.reward = reward
        self.is_finished = False
        self.plot_quest = is_plot

    def add_to_list(self) -> None:
        """
        Adds quests objects to pickle file
        """
        active = get_current_quests()
        if not active:
            with open(QUESTS, 'wb') as fd:
                pickle.dump([self], fd)
        else:
            active.append(self)
            with open(QUESTS, 'wb') as fd:
                pickle.dump(active, fd)

    def update_quest(self, quests: list) -> None:
        """
        Updates quest's goal in the pickle file
        """
        self.current_amount += 1
        if self.current_amount >= self.goal_amount:
            self.is_finished = True
            print("You've finished the quest conditions!")
            print("You can get a reward in any tavern")
        with open(QUESTS, 'wb') as fd:
            pickle.dump(quests, fd)

    def close_quest(self, quests, player) -> None:
        """
        Removes quest from player's activities, gives reward for mission
        :param quests: list of active player's quests
        # :param quest: target quest for closing
        :param player: object of Player class
        """
        player.gold += self.reward
        quests.remove(self)
        with open(QUESTS, 'wb') as fd:
            pickle.dump(quests, fd)
        print(f"\nThanks! Your reward is: {self.reward} gold coins")
