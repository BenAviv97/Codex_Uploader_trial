from __future__ import annotations

import json
from pathlib import Path
from typing import List

REQUIRED_FIELDS = {"title", "description"}
THUMB_EXTS = {".jpg", ".jpeg", ".png"}


def _validate_item(dir_path: Path, errors: List[str]) -> None:
    video = None
    thumb = None
    for p in dir_path.iterdir():
        if p.is_file():
            if p.suffix.lower() == ".mp4":
                video = p
            if p.suffix.lower() in THUMB_EXTS:
                thumb = p
    if video is None:
        errors.append(f"Missing .mp4 file in {dir_path}")
    if thumb is None:
        errors.append(f"Missing thumbnail in {dir_path}")

    meta_path = dir_path / "metadata.json"
    if not meta_path.exists():
        errors.append(f"Missing metadata.json in {dir_path}")
        return
    try:
        data = json.loads(meta_path.read_text())
    except json.JSONDecodeError:
        errors.append(f"Invalid JSON in {meta_path}")
        return
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Metadata missing field '{field}' in {meta_path}")


def validate_project(base_path: Path) -> List[str]:
    """Validate a project directory and return a list of error messages."""

    errors: List[str] = []

    def walk(path: Path, in_shorts: bool = False) -> None:
        shorts_dir = path / "shorts"
        if in_shorts and shorts_dir.exists():
            errors.append(f"Nested shorts directory not allowed: {shorts_dir}")
        for entry in path.iterdir():
            if entry.is_dir():
                if entry.name == "shorts":
                    if in_shorts:
                        errors.append(
                            f"Nested shorts directory not allowed: {entry}")
                        continue
                    walk(entry, True)
                else:
                    walk(entry, in_shorts)
        if any(f.is_file() and f.suffix.lower() == ".mp4" for f in path.iterdir()):
            _validate_item(path, errors)

    walk(base_path)
    return errors


def validate_folder(path: Path) -> List[str]:
    """Validate a single folder containing a video item.

    Returns a list of error messages describing any issues found. If the
    provided path is not a directory, a corresponding error is returned.
    """

    errors: List[str] = []
    if not path.is_dir():
        errors.append(f"{path} is not a directory")
        return errors

    _validate_item(path, errors)
    return errors
