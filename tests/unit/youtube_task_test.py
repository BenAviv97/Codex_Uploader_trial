import importlib
import pytest

try:
    from app.celery_app import celery_app
except ModuleNotFoundError:
    celery_app = None


@pytest.mark.skipif(celery_app is None, reason="Celery not installed")
def test_youtube_task_importable():
    assert "tasks.youtube.upload_video" in celery_app.tasks
