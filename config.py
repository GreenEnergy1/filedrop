import os
import json
import uuid

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")


def load_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as settings:
            value = json.load(settings)
            return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def ensure_server_id():
    settings = load_settings()
    server_id = settings.get("server_id")
    if isinstance(server_id, str) and server_id:
        return server_id

    server_id = str(uuid.uuid4())
    settings["server_id"] = server_id
    temporary = SETTINGS_FILE + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(settings, handle, indent=2)
        handle.write("\n")
    os.replace(temporary, SETTINGS_FILE)
    return server_id


def configured_files_dir():
    # An environment variable remains useful for deployments and overrides setup.
    override = os.environ.get("FILEDROP_DIR")
    if override:
        return override
    return load_settings().get("files_dir", os.path.join(BASE_DIR, "files"))


class Config:
    # Folder that gets served. Override with the FILEDROP_DIR environment variable.
    FILES_DIR = configured_files_dir()
    HOST = os.environ.get("FILEDROP_HOST", "0.0.0.0")
    PORT = int(os.environ.get("FILEDROP_PORT", "1080"))
    TITLE = os.environ.get("FILEDROP_TITLE", "FileZ")
    SERVICE_NAME = os.environ.get("FILEDROP_NAME", "")
    SERVER_ID = ensure_server_id()
