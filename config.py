from __future__ import annotations
import os
from typing import List, Optional
from dotenv import load_dotenv


load_dotenv()


def _str_to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "y", "on"}


class Config:
    """Application configuration loaded from environment variables."""

    # OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")

    # BROKER connection string
    BROKER_URL = os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672//")
    CELERY_BROKER_URL: str = BROKER_URL
    CELERY_RESULT_BACKEND: str = BROKER_URL

    # Default upload schedule as a list of HH:MM strings
    DEFAULT_UPLOAD_TIMES: List[str] = os.getenv(
        "DEFAULT_UPLOAD_TIMES", "09:00"
    ).split(",")

    # HTTPS/SSL settings
    USE_HTTPS: bool = _str_to_bool(os.getenv("USE_HTTPS"))
    SSL_CERT_PATH: Optional[str] = os.getenv("SSL_CERT_PATH")
    SSL_KEY_PATH: Optional[str] = os.getenv("SSL_KEY_PATH")

    # Path on Google Drive containing project folders
    PROJECTS_DRIVE_PATH: str = os.getenv("PROJECTS_DRIVE_PATH", "projects")
