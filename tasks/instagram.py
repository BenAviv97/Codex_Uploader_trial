from __future__ import annotations

import logging
from typing import Optional

import requests

from app.celery_app import celery_app
from config import Config

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.instagram.upload_video")
def upload_video(
    project_id: int,
    schedule_id: int,
    video_path: str,
    caption: str,
    thumbnail_path: Optional[str] = None,
    access_token: Optional[str] = None,
    ig_user_id: Optional[str] = None,
):
    """Upload a video to Instagram via the Graph API.

    Parameters are kept generic so this task can easily be wired up
    by higher level scheduler logic. The implementation follows the
    official Graph API flow of creating a media container and then
    publishing it. Thumbnails are optionally uploaded via the
    ``cover_url`` parameter when provided.
    """

    access_token = access_token or getattr(Config, "INSTAGRAM_ACCESS_TOKEN", None)
    ig_user_id = ig_user_id or getattr(Config, "INSTAGRAM_USER_ID", None)
    if not access_token or not ig_user_id:
        raise ValueError("Missing Instagram credentials")

    logger.info(
        "Uploading to Instagram: project=%s schedule=%s video=%s", project_id, schedule_id, video_path
    )

    creation_url = f"https://graph.facebook.com/v17.0/{ig_user_id}/media"
    files = {"video_file": open(video_path, "rb")}
    data = {"caption": caption, "access_token": access_token}
    if thumbnail_path:
        files["cover_photo"] = open(thumbnail_path, "rb")
    resp = requests.post(creation_url, files=files, data=data)
    resp.raise_for_status()
    creation_id = resp.json().get("id")

    publish_url = f"https://graph.facebook.com/v17.0/{ig_user_id}/media_publish"
    publish_resp = requests.post(
        publish_url, data={"creation_id": creation_id, "access_token": access_token}
    )
    publish_resp.raise_for_status()
    result = publish_resp.json()

    logger.info(
        "Uploaded to Instagram: project=%s schedule=%s media_id=%s", project_id, schedule_id, result.get("id")
    )
    return result
