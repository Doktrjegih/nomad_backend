"""Seeded CLI-game simulations. Run from the checkout with the project Python."""
import argparse
import contextlib
import csv
import logging
from pathlib import Path
import random
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db
from console import ExitException
from player import Player
from tests import autoplayer
from tests.framework import world_creation


class MoveLimit(Exception):
    pass


def play(seed, limit, log_path):
    random.seed(seed)
    Player.reset()
    autoplayer.actions = None
    logging.shutdown()
    logging.getLogger().handlers.clear()
    steps = inputs = 0
    with log_path.open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
        scene = world_creation()

        def answer(prompt):
            nonlocal inputs
            inputs += 1
            if scene.player.moves >= limit or inputs > limit * 10:
                raise MoveLimit()
            return autoplayer.make_decision(scene)

        try:
            with patch('builtins.input', side_effect=answer):
                while steps < limit * 5:
                    steps += 1
                    scene.show_current_scene()
            outcome = 'censored'
        except ExitException:
            outcome = 'death'
        except SystemExit as exc:
            if exc.code not in (None, 0):
                raise
            log.flush()
            outcome = 'win' if 'You win!' in log_path.read_text() else 'story_loss'
        except MoveLimit:
            outcome = 'censored'
        finally:
            db.session.close()
            db.engine.dispose()
    return dict(seed=seed, outcome=outcome, moves=scene.player.moves,
                scene_steps=steps, inputs=inputs, plot=scene.player.plot_stage,
                battles_won=scene.player.battles_won)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=int, default=100)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--limit', type=int, default=500)
    parser.add_argument('--output', type=Path, default=Path('temp_files/balance'))
    args = parser.parse_args()
    if min(args.runs, args.limit) <= 0:
        parser.error('runs and limit must be positive')
    args.output.mkdir(parents=True, exist_ok=True)
    rows = [play(seed, args.limit, args.output / f'game-{seed}.txt')
            for seed in range(args.seed, args.seed + args.runs)]
    with (args.output / 'results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    from collections import Counter
    from statistics import median
    print(dict(Counter(row['outcome'] for row in rows)))
    print(f"Moves: min={min(r['moves'] for r in rows)}, "
          f"median={median(r['moves'] for r in rows)}, max={max(r['moves'] for r in rows)}")
    print(f"Within 100–500: {sum(100 <= r['moves'] <= 500 and r['outcome'] != 'censored' for r in rows)}/{len(rows)}")


if __name__ == '__main__':
    main()
