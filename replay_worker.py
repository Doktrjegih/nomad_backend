"""Reconstruct one turn from validated button history in a disposable process."""
import json
import random
import sys

import console
from web_worker import BrowserUI


class PromptReady(BaseException):
    pass


class ReplayUI(BrowserUI):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.position = 0

    def choose(self, question, groups):
        if self.position == len(self.history):
            return super().choose(question, groups)
        value = self.history[self.position]
        for group, values in groups.items():
            if group != 'cheats' and value in [str(v) for v in values]:
                self.position += 1
                self.revision += 1
                self.lines = []
                return group, value
        raise ValueError('Invalid action history')

    def read_action(self):
        raise PromptReady()


def run():
    request = json.loads(sys.stdin.readline())
    random.seed(request['seed'])
    ui = ReplayUI(request['history'])
    console.browser_ui = ui
    from main import main
    try:
        main()
    except PromptReady:
        pass
    except (console.ExitException, SystemExit):
        if ui.position != len(ui.history):
            raise ValueError('Actions after the ending')
        ui.revision += 1
        ui.emit(status='finished', question='Your journey has ended.', options=[])


if __name__ == '__main__':
    run()
