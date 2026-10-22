import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")


def configured_files_dir():
    # An environment variable remains useful for deployments and overrides setup.
    override = os.environ.get("FILEDROP_DIR")
    if override:
        return override
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as settings:
            return json.load(settings)["files_dir"]
    except (OSError, ValueError, KeyError, TypeError):
        return os.path.join(BASE_DIR, "files")


class Config:
    # Folder that gets served. Override with the FILEDROP_DIR environment variable.
    FILES_DIR = configured_files_dir()
    HOST = os.environ.get("FILEDROP_HOST", "0.0.0.0")
    PORT = int(os.environ.get("FILEDROP_PORT", "8080"))
    TITLE = os.environ.get("FILEDROP_TITLE", "FileZ")
