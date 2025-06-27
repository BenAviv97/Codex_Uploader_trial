import json
from pathlib import Path
import importlib.util
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1].parent
spec = importlib.util.spec_from_file_location(
    "validators", ROOT / "app" / "validators.py"
)
validators = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validators)
validate_project = validators.validate_project


def create_valid_video(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "video.mp4").write_text("dummy")
    (folder / "thumbnail.jpg").write_text("thumb")
    metadata = {"title": "Test", "description": "Desc"}
    (folder / "metadata.json").write_text(json.dumps(metadata))


def test_validate_happy_path(tmp_path: Path):
    video_dir = tmp_path / "video1"
    create_valid_video(video_dir)
    errors = validate_project(tmp_path)
    assert errors == []


def test_missing_files(tmp_path: Path):
    video_dir = tmp_path / "video1"
    video_dir.mkdir()
    (video_dir / "video.mp4").write_text("dummy")
    (video_dir / "metadata.json").write_text(json.dumps({"title": "t", "description": "d"}))
    errors = validate_project(tmp_path)
    assert any("thumbnail" in e.lower() for e in errors)


def test_bad_json(tmp_path: Path):
    video_dir = tmp_path / "video1"
    video_dir.mkdir()
    (video_dir / "video.mp4").write_text("dummy")
    (video_dir / "thumbnail.jpg").write_text("thumb")
    (video_dir / "metadata.json").write_text("{ not json }")
    errors = validate_project(tmp_path)
    assert any("invalid json" in e.lower() for e in errors)


def test_schema_errors(tmp_path: Path):
    video_dir = tmp_path / "video1"
    video_dir.mkdir()
    (video_dir / "video.mp4").write_text("dummy")
    (video_dir / "thumbnail.jpg").write_text("thumb")
    (video_dir / "metadata.json").write_text(json.dumps({"title": "t"}))
    errors = validate_project(tmp_path)
    assert any("description" in e.lower() for e in errors)


def test_nested_shorts(tmp_path: Path):
    nested = tmp_path / "shorts" / "a" / "shorts" / "b"
    create_valid_video(nested)
    errors = validate_project(tmp_path)
    assert any("nested shorts" in e.lower() for e in errors)
