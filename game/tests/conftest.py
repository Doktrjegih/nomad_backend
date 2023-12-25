from pathlib import Path

import pytest


@pytest.fixture
def clear_dir():
    yield
    directory_path = Path(".")
    files_to_delete = directory_path.glob("*.log")
    try:
        for file in files_to_delete:
            file.unlink() if "etalon" not in file.name else 0
    except FileNotFoundError:
        pass


@pytest.fixture(scope='session')
def test_counter(request):
    count = [0]

    def increment_counter():
        count[0] += 1
        return count[0]

    yield increment_counter


def pytest_sessionfinish(session, exitstatus):
    total_tests = 10
    if session.testscollected >= total_tests:
        average = 0
        session.config.pluginmanager.getplugin('terminalreporter').write_line("Running post process script")
        with open("results.txt", "r", encoding="utf-8") as fd:
            for line in fd.readlines():
                average += int(line.split("=")[1].strip())
        with open("results.txt", "a", encoding="utf-8") as fd:
            fd.write(f"average value = {average / total_tests}")
