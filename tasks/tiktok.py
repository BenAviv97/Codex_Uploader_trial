from __future__ import annotations

import logging
from typing import Any, Dict

import requests

from app.celery_app import celery_app
from config import Config

logger = logging.getLogger(__name__)

TIKTOK_UPLOAD_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/"


@celery_app.task(name="tasks.tiktok.upload_video")
def upload_video(project_id: int, schedule_id: int, metadata: dict | None = None) -> Dict[str, Any]:
    """Upload a video to TikTok using the Open API.

    Parameters
    ----------
    project_id: int
        Identifier for the project the video belongs to.
    schedule_id: int
        Identifier of the scheduled upload entry.
    metadata: dict | None
        Optional metadata containing at minimum `video_path` and `caption`.
    """

    if metadata is None:
        metadata = {}

    video_path = metadata.get("video_path")
    caption = metadata.get("caption", "")
    access_token = metadata.get("access_token") or getattr(Config, "TIKTOK_ACCESS_TOKEN", None)

    if not access_token:
        raise ValueError("TikTok access token not provided")
    if not video_path:
        raise ValueError("No video file specified for TikTok upload")

    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"caption": caption}

    try:
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            response = requests.post(
                TIKTOK_UPLOAD_ENDPOINT,
                files=files,
                data=data,
                headers=headers,
                timeout=30,
            )
        response.raise_for_status()
        result = response.json()
        logger.info(
            "TikTok upload succeeded: project_id=%s schedule_id=%s response=%s",
            project_id,
            schedule_id,
            result,
        )
        return result
    except FileNotFoundError as exc:
        logger.exception("Video file not found: %s", exc)
        raise
    except requests.RequestException as exc:
        logger.exception("TikTok upload failed: %s", exc)
        raise
