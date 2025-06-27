from __future__ import annotations

import json
import os
import sqlite3
from typing import Optional

from flask import Blueprint, current_app, redirect, request, session, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request


auth_bp = Blueprint("auth", __name__)

# Default OAuth scopes used for Google APIs
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# Path to the SQLite database that stores OAuth credentials
DB_PATH = os.path.join(os.path.dirname(__file__), "tokens.db")


def _init_db() -> None:
    """Create the tokens table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY,
                credentials TEXT NOT NULL
            )"""
        )
        conn.commit()
    finally:
        conn.close()


def _store_credentials(creds: Credentials) -> None:
    """Persist credentials in the SQLite database."""
    _init_db()
    data = creds.to_json()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM tokens WHERE id = 1")
        conn.execute("INSERT INTO tokens (id, credentials) VALUES (1, ?)", (data,))
        conn.commit()
    finally:
        conn.close()


def _load_credentials() -> Optional[Credentials]:
    """Load stored credentials from the database if available."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("SELECT credentials FROM tokens WHERE id = 1")
        row = cur.fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    data = json.loads(row[0])
    creds = Credentials.from_authorized_user_info(data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _store_credentials(creds)
    return creds


def _flow(state: Optional[str] = None) -> Flow:
    """Create an OAuth Flow instance."""
    client_config = {
        "web": {
            "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
            "client_secret": current_app.config.get("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [url_for("auth.oauth2_callback", _external=True)],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for("auth.oauth2_callback", _external=True)
    return flow


@auth_bp.route("/auth/google")
def authenticate() -> redirect:
    """Start OAuth flow with Google."""
    flow = _flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@auth_bp.route("/auth/google/callback")
def oauth2_callback() -> redirect:
    """Handle the OAuth callback and store tokens."""
    state = session.get("oauth_state")
    flow = _flow(state)
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    _store_credentials(creds)
    return redirect(url_for("index"))


def get_credentials() -> Optional[Credentials]:
    """Retrieve stored credentials, refreshing if needed."""
    return _load_credentials()
