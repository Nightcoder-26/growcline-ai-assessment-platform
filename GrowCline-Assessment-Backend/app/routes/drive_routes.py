"""
Google Drive OAuth Authorization Routes
Endpoints for one-time admin/owner authorization of the target Google Drive account.
"""

import os
import json
import logging
import urllib.parse
import urllib.request
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse

from app.config.settings import Config
from app.services.google_drive_service import GoogleDriveService, _resolve_oauth_token_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/drive", tags=["Google Drive OAuth"])

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


@router.get("/status")
async def get_drive_status():
    """Check whether Google Drive OAuth authorization token is active."""
    token_file = _resolve_oauth_token_file()
    if token_file and os.path.isfile(token_file):
        try:
            service = GoogleDriveService.verify_connection()
            return {
                "authorized": True,
                "token_file": token_file,
                "status": "OPERATIONAL",
                "folder_id": Config.GOOGLE_DRIVE_FOLDER_ID,
            }
        except Exception as exc:
            return {
                "authorized": False,
                "token_file": token_file,
                "status": "ERROR",
                "message": str(exc),
            }
    return {
        "authorized": False,
        "status": "UNAUTHORIZED",
        "message": "credentials/google_oauth_token.json not found. Authorize at /api/drive/auth-url",
    }


@router.get("/auth-url")
async def get_auth_url(
    client_id: Optional[str] = Query(None),
    redirect_uri: Optional[str] = Query(None),
):
    """Generate the Google OAuth 2.0 authorization URL."""
    c_id = client_id or Config.GOOGLE_CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")
    r_uri = redirect_uri or Config.GOOGLE_REDIRECT_URI or "http://localhost:5001/api/drive/callback"

    if not c_id:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_CLIENT_ID is not configured. Provide client_id query param or set GOOGLE_CLIENT_ID in env."
        )

    params = {
        "client_id": c_id,
        "redirect_uri": r_uri,
        "response_type": "code",
        "scope": OAUTH_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return {
        "auth_url": url,
        "client_id": c_id,
        "redirect_uri": r_uri,
        "instructions": "Open auth_url in your browser while logged in as the Google account that owns 'GrowCline Interview Recordings'."
    }


@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    client_secret: Optional[str] = Query(None),
    redirect_uri: Optional[str] = Query(None),
):
    """Callback handler for Google OAuth 2.0 redirection."""
    if error:
        return HTMLResponse(
            f"<h3>Google OAuth Authorization Failed:</h3><p>{error}</p>",
            status_code=400,
        )

    if not code:
        return HTMLResponse(
            "<h3>Missing authorization code.</h3>",
            status_code=400,
        )

    c_id = client_id or Config.GOOGLE_CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")
    c_secret = client_secret or Config.GOOGLE_CLIENT_SECRET or os.environ.get("GOOGLE_CLIENT_SECRET", "")
    r_uri = redirect_uri or Config.GOOGLE_REDIRECT_URI or "http://localhost:5001/api/drive/callback"

    if not c_id or not c_secret:
        return HTMLResponse(
            f"<h3>OAuth Client credentials missing.</h3><p>Code received: <code>{code}</code>. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend .env to exchange tokens automatically.</p>",
            status_code=400,
        )

    try:
        data = urllib.parse.urlencode({
            "client_id": c_id,
            "client_secret": c_secret,
            "redirect_uri": r_uri,
            "code": code,
            "grant_type": "authorization_code",
        }).encode("utf-8")

        req = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))

        refresh_token = tokens.get("refresh_token", "")
        access_token = tokens.get("access_token", "")

        token_file = Config.GOOGLE_TOKEN_FILE or "credentials/google_oauth_token.json"
        os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)

        token_data = {
            "token": access_token,
            "refresh_token": refresh_token,
            "token_uri": TOKEN_URL,
            "client_id": c_id,
            "client_secret": c_secret,
            "scopes": [OAUTH_SCOPE]
        }

        with open(token_file, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        return HTMLResponse(
            "<h2>✅ Google Drive OAuth Authorization Successful!</h2>"
            "<p>Backend token file <code>credentials/google_oauth_token.json</code> saved.</p>"
            "<p>You can now upload recordings directly to <strong>GrowCline Interview Recordings</strong>.</p>"
        )

    except Exception as exc:
        return HTMLResponse(
            f"<h3>Token Exchange Failed:</h3><p>{exc}</p>",
            status_code=500,
        )


@router.post("/save-token")
async def save_token_payload(payload: dict = Body(...)):
    """Save raw OAuth token JSON payload securely to token file."""
    client_id = payload.get("client_id") or Config.GOOGLE_CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = payload.get("client_secret") or Config.GOOGLE_CLIENT_SECRET or os.environ.get("GOOGLE_CLIENT_SECRET", "")
    refresh_token = payload.get("refresh_token") or payload.get("refreshToken") or ""
    access_token = payload.get("access_token") or payload.get("accessToken") or payload.get("token") or ""

    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token field is required in payload.")

    token_data = {
        "token": access_token,
        "refresh_token": refresh_token,
        "token_uri": TOKEN_URL,
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": [OAUTH_SCOPE]
    }

    token_file = Config.GOOGLE_TOKEN_FILE or "credentials/google_oauth_token.json"
    os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)

    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

    logger.info("Saved OAuth token payload to %s", token_file)
    return {
        "success": True,
        "message": f"OAuth token saved to {token_file}",
        "authorized": True
    }
