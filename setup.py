import json
from pathlib import Path

from config import BASE_DIR, Config, load_settings


def main():
    current = Path(Config.FILES_DIR).expanduser()
    print("Choose the folder Filedrop will share.")
    print("Enter a full folder path, such as C:\\Users\\you\\Documents or ~/Documents.")
    entered = input(f"Folder [{current}]: ").strip().strip('"')
    selected = Path(entered).expanduser() if entered else current
    try:
        selected = selected.resolve(strict=True)
    except (OSError, RuntimeError):
        print(f"Folder does not exist: {selected}")
        return 1
    if not selected.is_dir():
        print(f"That path is not a folder: {selected}")
        return 1

    settings_path = Path(BASE_DIR) / "settings.json"
    settings = load_settings()
    settings["files_dir"] = str(selected)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print(f"Saved. Filedrop will serve: {selected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
