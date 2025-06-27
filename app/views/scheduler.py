from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

scheduler_bp = Blueprint("scheduler", __name__)


@scheduler_bp.route("/scheduler")
def scheduler_page():
    """Render the schedule picker page."""
    default_times = current_app.config.get("DEFAULT_UPLOAD_TIMES", ["09:00"])
    return render_template("scheduler.html", default_times=default_times)


@scheduler_bp.route("/api/schedule", methods=["POST"])
def schedule_api():
    """Receive a user-defined schedule."""
    data = request.get_json(silent=True) or {}
    schedule = data.get("schedule", [])
    # In a real app this would persist the schedule
    return jsonify({"received": schedule})
