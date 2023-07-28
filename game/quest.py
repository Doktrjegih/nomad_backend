import pickle
from console import print


def get_current_quests() -> list:
    """
    Reads active quests from pickle file as list of objects
    :return: list of Enemy objects or None
    """
    try:
        with open('quests.pkl', 'rb') as fd:
            data = pickle.load(fd)
        return data
    except EOFError:
        return list()


class Quest:
    def __init__(self, order, amount, reward) -> None:
        self.order = order
        self.goal_amount = amount
        self.current_amount = 0
        self.reward = reward
        self.is_finished = False
        self.xp_for_quest = 0

    def add_to_list(self) -> None:
        """
        Adds quests objects to pickle file
        """
        active = get_current_quests()
        if not active:
            with open('quests.pkl', 'wb') as fd:
                pickle.dump([self], fd)
        else:
            active.append(self)
            with open('quests.pkl', 'wb') as fd:
                pickle.dump(active, fd)

    def update_quest(self, quests: list, xp: int) -> None:
        """
        Updates quest's goal in the pickle file
        """
        self.current_amount += 1
        if self.current_amount >= self.goal_amount:
            self.is_finished = True
            print("You've finished the quest conditions!")
            print("You can get a reward in any tavern")
        self.xp_for_quest += xp
        with open('quests.pkl', 'wb') as fd:
            pickle.dump(quests, fd)

    def close_quest(self, quests, player) -> None:
        """
        Removes quest from player's activities, gives reward for mission
        :param quests: list of active player's quests
        # :param quest: target quest for closing
        :param player: object of Player class
        """
        player.gold += self.reward
        player.gain_scores(self.xp_for_quest)
        quests.remove(self)
        with open('quests.pkl', 'wb') as fd:
            pickle.dump(quests, fd)
        print(f"\nThanks! Your reward is: {self.reward} coins")
