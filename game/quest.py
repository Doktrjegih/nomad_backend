import pickle


class Quest:
    def __init__(self, order, amount, award):
        self.order = order
        self.goal_amount = amount
        self.current_amount = 0
        self.award = award

    @staticmethod
    def _get_current_quests():
        try:
            with open('quests.pkl', 'rb') as fd:
                data = pickle.load(fd)
            return data
        except EOFError:
            return list()

    def add_to_list(self):
        active = self._get_current_quests()
        if not active:
            with open('quests.pkl', 'wb') as fd:
                pickle.dump([self], fd)
        else:
            active.append(self)
            with open('quests.pkl', 'wb') as fd:
                pickle.dump(active, fd)
