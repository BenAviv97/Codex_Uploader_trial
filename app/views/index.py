from __future__ import annotations

from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def index():
    """Render the application home page."""
    return render_template("index.html")
