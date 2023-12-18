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
