from pathlib import Path

MAIN_FOLDER = Path(__file__).parent
JSONS = Path(MAIN_FOLDER, "jsons")
TEMP_FILES = Path(MAIN_FOLDER, "temp_files")
TESTS = Path(MAIN_FOLDER, "tests")

PLOT_QUESTS = Path(JSONS, "plot_quests.json")
ENEMIES = Path(JSONS, "enemies.json")
ITEMS = Path(JSONS, "items.json")

DB = Path(TEMP_FILES, "sqalch.sqlite")
QUESTS = Path(TEMP_FILES, "quests.pkl")
HIGH_SCORES = Path(TEMP_FILES, "high_scores.txt")
LAST_GAME_LOG = Path(TEMP_FILES, "last_game.log")
