import linecache
import pickle
import re
from types import GeneratorType
import difflib
from pathlib import Path

import db
from console import print, start_logger
from items import Items
from location import Location
from player import Player
from scene import Scene

tests_folder = Path(__file__).parent


def world_creation() -> Scene:
    start_logger()
    db.create_database()
    print('Hello, a big new world!')
    player = Player()
    items = Items(player=player)
    scene = Scene(location=Location(type_='hometown', player_luck=player.luck), player=player, items=items)
    with open(Path(tests_folder.parent, "quests.pkl"), 'wb') as fd:
        pickle.dump([], fd)
    return scene


def turns_generator(data) -> GeneratorType:
    for item in data:
        yield str(item)


def open_entrypoint(scene: Scene, name: str) -> int:
    options = scene.get_possible_options()
    return options.index(name) + 1


def read_rows_in_range(file_path, start_row: int, finish_row: int) -> str:
    if start_row >= finish_row:
        raise ValueError('Start row must be less than finish')
    content = ""
    with open(file_path, 'r') as file:
        for counter, line in enumerate(file, start=1):
            if counter < start_row:
                continue
            if counter > finish_row:
                break
            content += line
    return content


def read_file_ignoring_rows(file_path: str, ignore: list[int]) -> str:
    content = ""
    with open(file_path, 'r') as file:
        for counter, line in enumerate(file, start=1):
            if counter in ignore:
                continue
            content += line
    return content


def compare_strings_ignore_numbers(str1: str, str2: str) -> None:
    str1_without_numbers = re.sub(r'\d', '', str1)
    str2_without_numbers = re.sub(r'\d', '', str2)
    assert str1_without_numbers == str2_without_numbers


def get_row_from_file(file_path, row: int) -> str:
    return linecache.getline(file_path, row)


def read_file_by_lines(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def get_discrepancies(file1_content, file2_content, ignore=None):
    if ignore is None:
        ignore = []

    filtered_file1_content = [line for idx, line in enumerate(file1_content) if idx not in ignore]
    filtered_file2_content = [line for idx, line in enumerate(file2_content) if idx not in ignore]

    diff = difflib.ndiff(filtered_file1_content, filtered_file2_content)
    discrepancies = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
    return discrepancies

def assert_files_equal(file1_path, file2_path, ignore=None):
    file1_content = read_file_by_lines(file1_path)
    file2_content = read_file_by_lines(file2_path)

    discrepancies = get_discrepancies(file1_content, file2_content, ignore)
    if discrepancies:
        diff = '\n'.join(discrepancies)
        raise AssertionError(f"Files have discrepancies:\n{diff}")
