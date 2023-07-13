import os


def console(*args):
    os.system('clear')
    for row in args:
        print(row)
