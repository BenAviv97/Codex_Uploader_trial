from __future__ import annotations

import io
import os
from typing import Iterable, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from .auth import get_credentials


FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


def _get_service():
    """Return an authorized Drive API client."""
    creds = get_credentials()
    if creds is None:
        raise RuntimeError("Google credentials are not available")
    return build("drive", "v3", credentials=creds)


def _find_child_folder(service, parent_id: str, name: str) -> str | None:
    """Return the ID of a child folder with the given name under parent."""
    query = (
        f"'{parent_id}' in parents and "
        f"mimeType='{FOLDER_MIME_TYPE}' and name='{name}' and trashed=false"
    )
    response = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id,name)")
        .execute()
    )
    files = response.get("files", [])
    if not files:
        return None
    return files[0]["id"]


def _resolve_path(service, path: str) -> str:
    """Resolve a '/' separated Drive path to a folder ID."""
    parts = [p for p in path.strip("/").split("/") if p]
    folder_id = "root"
    for part in parts:
        child = _find_child_folder(service, folder_id, part)
        if child is None:
            raise FileNotFoundError(f"Drive folder '{path}' not found")
        folder_id = child
    return folder_id


def list_folders(path: str) -> List[dict]:
    """Return all child folders of the given Drive path."""
    service = _get_service()
    parent_id = _resolve_path(service, path)
    query = (
        f"'{parent_id}' in parents and mimeType='{FOLDER_MIME_TYPE}' "
        "and trashed=false"
    )
    page_token = None
    folders: List[dict] = []
    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            )
            .execute()
        )
        folders.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return folders


def _download_file(service, file_id: str, dest_path: str) -> None:
    request = service.files().get_media(fileId=file_id)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with io.FileIO(dest_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            try:
                _, done = downloader.next_chunk()
            except HttpError as err:
                raise RuntimeError(f"Failed downloading file {file_id}: {err}") from err


def _download_folder_by_id(service, folder_id: str, dest_dir: str) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    query = f"'{folder_id}' in parents and trashed=false"
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        for item in response.get("files", []):
            target = os.path.join(dest_dir, item["name"])
            if item["mimeType"] == FOLDER_MIME_TYPE:
                _download_folder_by_id(service, item["id"], target)
            else:
                _download_file(service, item["id"], target)
        page_token = response.get("nextPageToken")
        if not page_token:
            break


def download_folder(path: str, destination: str) -> None:
    """Download the entire Drive folder to the destination path."""
    service = _get_service()
    folder_id = _resolve_path(service, path)
    _download_folder_by_id(service, folder_id, destination)
