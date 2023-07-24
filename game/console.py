import os


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
