from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.celery_app import celery_app
from app.auth import get_credentials
from app import models

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.youtube.upload_video")
def upload_video(project_id: int, schedule_id: int, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Upload a video file to YouTube and update status in the DB."""
    logger.info(
        "Uploading video: project_id=%s schedule_id=%s metadata=%s",
        project_id,
        schedule_id,
        metadata,
    )

    if not metadata:
        logger.error("No metadata supplied for schedule %s", schedule_id)
        models.update_schedule_status(schedule_id, "failed")
        return {"error": "missing metadata"}

    video_path = metadata.get("video_path")
    thumb_path = metadata.get("thumbnail_path")
    snippet = metadata.get("snippet", {})
    status_meta = metadata.get("status", {"privacyStatus": "private"})

    if not video_path or not Path(video_path).is_file():
        logger.error("Video file not found: %s", video_path)
        models.update_schedule_status(schedule_id, "failed")
        return {"error": "video file missing"}

    creds = get_credentials()
    if creds is None:
        logger.error("Google credentials unavailable")
        models.update_schedule_status(schedule_id, "failed")
        return {"error": "no credentials"}

    service = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": snippet,
        "status": status_meta,
    }

    try:
        insert = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )
        response = insert.execute()
        video_id = response.get("id")
        logger.info("Uploaded video %s", video_id)

        if thumb_path and Path(thumb_path).is_file():
            service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumb_path),
            ).execute()

        models.update_schedule_status(schedule_id, "uploaded")
        return {"video_id": video_id}
    except Exception as exc:  # pragma: no cover - network errors hard to test
        logger.exception("YouTube upload failed: %s", exc)
        models.update_schedule_status(schedule_id, "failed")
        return {"error": str(exc)}
