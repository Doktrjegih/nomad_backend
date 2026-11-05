"""Run one isolated CLI game over a JSON-lines button protocol."""
import json
import re
import sys

import console
from player import Player

ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
OPTION = re.compile(r'^(\d+)\s*-\s*(.+)$')


class BrowserUI:
    def __init__(self):
        self.lines = []
        self.revision = 0

    def write(self, row):
        self.lines.extend(ANSI.sub('', row).splitlines())

    def emit(self, **data):
        player = Player()
        data['player'] = {key: getattr(player, key) for key in
                          ('health', 'max_hp', 'attack', 'defence', 'gold', 'drunk',
                           'moves', 'plot_stage', 'strength', 'agility', 'luck')}
        data['player']['weapon'] = player.weapon.name if player.weapon else 'Unarmed'
        data['player']['armor'] = player.armor.name if player.armor else 'No armor'
        data['lines'] = self.lines
        self.lines = []
        data['revision'] = self.revision
        sys.stdout.write(json.dumps(data) + '\n')
        sys.stdout.flush()

    def choose(self, question, groups):
        labels = {}
        narrative = []
        for line in self.lines:
            match = OPTION.match(line)
            if match:
                labels[match[1]] = match[2]
            else:
                narrative.append(line)
        self.lines = narrative
        options = []
        accepted = {}
        for group, values in groups.items():
            if group == 'cheats':
                continue
            # Synonyms such as y/yes/1 become one button.
            if group in ('yes', 'no', 'cancel'):
                values = [next(iter(values))]
            for value in values:
                value = str(value)
                label = group.capitalize() if group in ('yes', 'no', 'cancel') else labels.get(value, value)
                options.append({'id': value, 'label': label})
                accepted[value] = group
        self.revision += 1
        self.emit(status='playing', question=question.strip(), options=options)
        request = json.loads(sys.stdin.readline())
        value = request.get('action')
        if request.get('revision') != self.revision or value not in accepted:
            raise ValueError('Invalid or stale action')
        return accepted[value], value


def run():
    ui = BrowserUI()
    console.browser_ui = ui
    from main import main
    try:
        main()
    except (console.ExitException, SystemExit):
        ui.revision += 1
        ui.emit(status='finished', question='Your journey has ended.', options=[])
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stderr)
        ui.revision += 1
        ui.emit(status='error', question='This journey could not continue. Start a new game.', options=[])


if __name__ == '__main__':
    run()
