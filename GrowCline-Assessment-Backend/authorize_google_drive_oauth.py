"""
Google Drive OAuth 2.0 One-Time Setup & Token Helper
Generates Google Drive User OAuth authorization URL and exchanges authorization code/refresh token
to save credentials/google_oauth_token.json.

Usage:
  python authorize_google_drive_oauth.py

Security Note:
  Never prints or commits private secrets or token files to Git.
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import logging

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config.settings import Config

OAUTH_SCOPE = "https://www.googleapis.com/auth/drive"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_FILE_PATH = os.path.abspath(Config.GOOGLE_TOKEN_FILE or "credentials/google_oauth_token.json")

def generate_auth_url(client_id: str, redirect_uri: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": OAUTH_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

def exchange_code_for_tokens(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        return res_data

def save_token_file(client_id: str, client_secret: str, refresh_token: str, access_token: str = ""):
    token_json = {
        "token": access_token,
        "refresh_token": refresh_token,
        "token_uri": TOKEN_URL,
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": [OAUTH_SCOPE]
    }
    os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
    with open(TOKEN_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(token_json, f, indent=2)
    print(f"\n[OAUTH] Tokens successfully saved to: {TOKEN_FILE_PATH}")

def main():
    print("==================================================")
    print("GOOGLE DRIVE USER OAUTH 2.0 AUTHORIZATION SETUP")
    print("==================================================")

    client_id = Config.GOOGLE_CLIENT_ID or os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = Config.GOOGLE_CLIENT_SECRET or os.environ.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = Config.GOOGLE_REDIRECT_URI or os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:5001/api/drive/callback")

    if not client_id:
        client_id = input("Enter GOOGLE_CLIENT_ID: ").strip()
    if not client_secret:
        client_secret = input("Enter GOOGLE_CLIENT_SECRET: ").strip()

    if not client_id or not client_secret:
        print("\nERROR: Both GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required.")
        sys.exit(1)

    auth_url = generate_auth_url(client_id, redirect_uri)

    print("\n1. OPEN THIS AUTHORIZATION URL IN YOUR BROWSER:")
    print("--------------------------------------------------")
    print(auth_url)
    print("--------------------------------------------------")
    print("Log in with the Google Account that owns 'GrowCline Interview Recordings'.")

    print("\n2. AFTER AUTHORIZATION:")
    auth_code = input("Paste the Authorization Code (or redirected code query parameter): ").strip()

    if not auth_code:
        print("ERROR: Authorization code cannot be empty.")
        sys.exit(1)

    print("\n[OAUTH] Exchanging code for refresh token...")
    try:
        tokens = exchange_code_for_tokens(client_id, client_secret, redirect_uri, auth_code)
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token", "")

        if not refresh_token:
            print("\nWARNING: No refresh_token was returned in response. Make sure access_type=offline & prompt=consent.")

        save_token_file(client_id, client_secret, refresh_token or "", access_token)
        print("[OAUTH] SETUP COMPLETED SUCCESSFULLY!")

    except Exception as exc:
        print(f"\n[OAUTH] ERROR: Token exchange failed: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
