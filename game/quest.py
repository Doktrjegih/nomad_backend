import pickle


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
    def __init__(self, order, amount, award) -> None:
        self.order = order
        self.goal_amount = amount
        self.current_amount = 0
        self.award = award
        self.is_finished = False

    def add_to_list(self) -> None:  # todo: several quests simultaneously
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

    def increase_goal(self) -> None:
        """
        Updates quest's goal in the pickle file
        """
        self.current_amount += 1
        if self.current_amount >= self.goal_amount:
            self.is_finished = True
            print("you've finish the quest conditions!")
            print("you can get a reward in any tavern")
        with open('quests.pkl', 'wb') as fd:
            pickle.dump([self], fd)

    def close_quest(self, player) -> None:
        """
        Removes quest from player's activities, gives award for mission
        :param player: object of Player class
        """
        player.gold += self.award
        with open('quests.pkl', 'wb') as fd:
            pickle.dump([], fd)
        print(f"thanks! your reward is: {self.award} coins")
