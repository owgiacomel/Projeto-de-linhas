"""Create a distributable ZIP archive for the Flight Line Connector plugin."""

from __future__ import annotations

import pathlib
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "flight_line_connector"
DIST_DIR = REPO_ROOT / "dist"
ZIP_PATH = DIST_DIR / "flight_line_connector.zip"


def main() -> None:
    if not PLUGIN_DIR.is_dir():
        raise SystemExit(f"Plugin folder not found: {PLUGIN_DIR}")

    DIST_DIR.mkdir(exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in PLUGIN_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(REPO_ROOT))

    print(f"Created {ZIP_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
