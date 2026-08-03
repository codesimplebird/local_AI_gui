import os

PROJECT_ROOT = os.path.normpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ICON_DIR = os.path.join(ASSETS_DIR, "icon")

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
CHAT_HISTORY_PATH = os.path.join(DATA_DIR, "chat_history.json")
CHAT_TEMPLATE_PATH = os.path.join(ASSETS_DIR, "chat_template.html")


def icon_path(filename: str) -> str:
    return os.path.join(ICON_DIR, filename)
