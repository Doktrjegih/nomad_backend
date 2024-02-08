from pathlib import Path

import pytest


@pytest.fixture
def clear_dir() -> None:
    yield
    directory_path = Path(".")
    files_to_delete = directory_path.glob("*.log")
    try:
        for file in files_to_delete:
            file.unlink() if "etalon" not in file.name else 0
    except FileNotFoundError:
        pass


@pytest.fixture(scope='session')
def clear_results() -> None:
    with open("results.txt", 'w') as fd:
        fd.write("")


def finish() -> None:
  average = 0
  try:
      with open("results.txt", "r", encoding="utf-8") as fd:
          for total_tests, line in enumerate(fd.readlines(), start=1):
              average += int(line.split("=")[1].strip())
      with open("results.txt", "a", encoding="utf-8") as fd:
          fd.write(f"average value = {average / total_tests}")
  except FileNotFoundError:
      print("File 'results.txt' not found")


@pytest.fixture(scope='session')
def test_counter(request) -> None:
    request.addfinalizer(finish)
