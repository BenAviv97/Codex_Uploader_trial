from __future__ import annotations

from datetime import datetime

from app.celery_app import celery_app
from app import models


@celery_app.task(name="tasks.scheduler.enqueue_uploads")
def enqueue_uploads(project_id: int) -> int:
    """Enqueue upload tasks for the given project based on its schedule."""
    schedules = models.get_schedules(project_id)
    count = 0
    for item in schedules:
        eta = datetime.fromisoformat(item["scheduled_at"])
        celery_app.send_task(
            "tasks.youtube.upload_video",
            args=[project_id, item["id"], item.get("metadata")],
            eta=eta,
        )
        count += 1
    return count

