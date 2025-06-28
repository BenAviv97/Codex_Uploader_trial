from __future__ import annotations

from flask import Blueprint, jsonify

from .. import models

status_bp = Blueprint("status", __name__)


@status_bp.route("/api/status/<int:project_id>")
def status_api(project_id: int):
    """Return upload status for all videos in the project."""
    schedules = models.get_schedules(project_id)
    results = []
    for item in schedules:
        meta = item.get("metadata") or {}
        results.append(
            {
                "id": item.get("id"),
                "scheduled_at": item.get("scheduled_at"),
                "status": meta.get("status", "pending"),
            }
        )
    return jsonify(results)
