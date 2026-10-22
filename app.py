import hashlib
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, send_from_directory

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

FILES_DIR = Path(Config.FILES_DIR).resolve()
FILES_DIR.mkdir(parents=True, exist_ok=True)

# (relative path, mtime, size) -> sha256, so big files are only hashed once
_checksums = {}


def is_hidden(rel: Path) -> bool:
    return any(part.startswith(".") for part in rel.parts)


def human_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    size = float(num_bytes)
    for unit in ("KB", "MB", "GB"):
        size /= 1024
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"


def list_files():
    items = []
    for path in FILES_DIR.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(FILES_DIR)
        if is_hidden(rel):
            continue
        stat = path.stat()
        items.append(
            {
                "path": rel.as_posix(),
                "size": stat.st_size,
                "size_label": human_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime),
            }
        )
    items.sort(key=lambda f: f["modified"], reverse=True)
    return items


def resolve_file(filename: str):
    """Return (relative path, absolute path) for a servable file, or 404."""
    rel = Path(filename)
    if rel.is_absolute() or is_hidden(rel):
        abort(404)
    target = (FILES_DIR / rel).resolve()
    if FILES_DIR not in target.parents or not target.is_file():
        abort(404)
    return rel, target


@app.route("/")
def index():
    files = list_files()
    total = human_size(sum(f["size"] for f in files))
    return render_template(
        "index.html",
        title=Config.TITLE,
        files=files,
        total=total,
        files_dir=str(FILES_DIR),
    )


@app.route("/download/<path:filename>")
def download(filename):
    rel, _ = resolve_file(filename)
    return send_from_directory(FILES_DIR, rel.as_posix(), as_attachment=True)


@app.route("/checksum/<path:filename>")
def checksum(filename):
    rel, target = resolve_file(filename)
    stat = target.stat()
    key = (rel.as_posix(), stat.st_mtime_ns, stat.st_size)
    if key not in _checksums:
        digest = hashlib.sha256()
        with open(target, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        _checksums[key] = digest.hexdigest()
    return jsonify(path=rel.as_posix(), sha256=_checksums[key])


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    from waitress import serve

    print(f"Serving {FILES_DIR} on http://{Config.HOST}:{Config.PORT}")
    serve(app, host=Config.HOST, port=Config.PORT, threads=8)
