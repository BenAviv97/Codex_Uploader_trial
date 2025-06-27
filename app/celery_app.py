from __future__ import annotations

from celery import Celery

from config import Config

celery_app = Celery(
    "codex_uploader",
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
)

# Automatically discover tasks from the "tasks" package
celery_app.autodiscover_tasks(["tasks"])

