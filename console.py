import builtins
import logging
from pathlib import Path
from enum import Enum

main_folder = Path(__file__).parent
logging.basicConfig(filename=f'{main_folder}/last_game.log', filemode='a', level=logging.INFO, format='%(message)s')
# todo: 1. print logs without printing (stupid I know, but let's try if it works)
# todo: 2. launch logging only after game start

class Colors(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print(*args):
    """
    A wrapper for logging the game during printing messages
    """
    row = " ".join(f"{value}" for value in args)
    builtins.print(row)
    logging.info(row)


def color(color: str, text: str) -> str:
    """
    Colors text to entered color and print it
    :param color: color of message
    :param text: message text
    """
    color_enum = Colors[color.upper()]
    return color_enum.value + text + Colors.ENDC.value


def answer_handler(question: str, **kwargs) -> (str, str | int):
    """
    USER ACTION
    Global answer handler. Works with any question-answer dialogs
    :param question: text showing during question
    :param kwargs: gets string with group name as key and list with conditional as value
    For example: items=[x for x in range(1, counter + 1)] - it will check if answer is in list
    :return: tuple with group name and user answer if answer in one of the groups
    """
    while True:
        try:
            answer = input(question).lower()
            for group, conditional in kwargs.items():
                if answer in conditional:
                    return group, answer
            print(color('red', 'Incorrect input'))
        except ValueError:
            print(color('red', 'Incorrect input (value error)'))
