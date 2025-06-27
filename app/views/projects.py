from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

from ..drive_client import list_folders

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def projects_page():
    """Render the project selection page."""
    return render_template("projects.html")


@projects_bp.route("/api/projects")
def projects_api():
    """Return available project folders from Google Drive."""
    path = current_app.config.get("PROJECTS_DRIVE_PATH", "projects")
    try:
        folders = list_folders(path)
    except FileNotFoundError:
        folders = []
    return jsonify(folders)
