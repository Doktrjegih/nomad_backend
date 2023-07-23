import os


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def console(*args):
    os.system('clear')
    for row in args:
        print(row)


def error(text: str):
    print(f'\n{Colors.FAIL}ERROR! {text}{Colors.ENDC}')


def warning(text: str):
    print(f'{Colors.WARNING}WARNING! {text}{Colors.ENDC}')
