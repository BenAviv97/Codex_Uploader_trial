from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .. import models


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard_page():
    """Render dashboard with status bars."""
    return render_template("dashboard.html")


@dashboard_bp.route("/api/status")
def status_api():
    """Return JSON status for all scheduled uploads."""
    statuses = models.get_all_statuses()
    return jsonify(statuses)
