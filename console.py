import os
import builtins


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def console(*args):
    os.system('clear')
    for row in args:
        print(row)


def print(*args):
    row = " ".join(f"{value}" for value in args)
    builtins.print(row)
    with open('last_game.log', 'a') as fd:
        fd.write(row + '\n')


def error(text: str) -> None:
    """
    Colors text to red and print warning
    :param text: error message
    """
    print(f'\n{Colors.RED}ERROR! {text}{Colors.ENDC}')


def warning(text: str) -> None:
    """
    Colors text to yellow and print warning
    :param text: warning message
    """
    print(f'{Colors.YELLOW}WARNING! {text}{Colors.ENDC}')


def color(color: str, text: str) -> str:
    """
    Colors text to entered color and print it
    :param color: color of message
    :param text: message text
    """
    if color == 'red':
        return Colors.RED + text + Colors.ENDC
    elif color == 'yellow':
        return Colors.YELLOW + text + Colors.ENDC
    elif color == 'green':
        return Colors.GREEN + text + Colors.ENDC


def answer_handler(question: str, is_int: bool, **kwargs) -> (str, str | int):
    """
    USER ACTION
    Global answer handler. Works with any question-answer dialogs
    :param question: text showing during question
    :param is_int: checks either answer is int or str type
    :param kwargs: gets string with group name as key and list with conditional as value
    For example: items=[x for x in range(1, counter + 1)] - it will check if answer in list
    :return: tuple with group name and user answer if answer in one of the groups
    """
    while True:
        try:
            if is_int:
                answer = int(input(question))
            else:
                answer = input(question).lower()

            for group, conditional in kwargs.items():
                if answer in conditional:
                    return group, answer
            error('Incorrect input')
        except ValueError:
            error('Incorrect input (value error)')
