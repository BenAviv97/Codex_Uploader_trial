from __future__ import annotations

import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.youtube.upload_video")
def upload_video(project_id: int, schedule_id: int, metadata: dict | None = None):
    """Placeholder task to upload a video to YouTube."""
    logger.info(
        "Uploading video: project_id=%s schedule_id=%s metadata=%s",
        project_id,
        schedule_id,
        metadata,
    )
    return {
        "project_id": project_id,
        "schedule_id": schedule_id,
        "metadata": metadata,
    }
