"""
Google Drive OAuth Diagnostic Script
Executes independent end-to-end diagnostic of Google Drive User OAuth 2.0 authentication,
target folder access, TXT upload, TXT verification, TXT cleanup, WEBM upload, WEBM verification, and WEBM cleanup.

Security Note: NEVER prints secrets or private keys.
"""

import sys
import os
import io
import json
import logging

from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("drive_oauth_diagnostic")

EXPECTED_FOLDER_ID = "1Y0N0v9gj7VumGcnepWqm3ebi4TmgRa9D"

results = {
    "oauth_setup": "FAIL",
    "auth_success": "FAIL",
    "folder_access": "FAIL",
    "txt_upload": "FAIL",
    "webm_upload": "FAIL",
    "fastapi_upload": "FAIL",
    "mongodb_meta": "FAIL",
    "real_recording": "FAIL",
}

root_cause = ""
manual_action = ""

def run_diagnostic():
    global root_cause, manual_action
    print("\n==========================================")
    print("STEP 1 & 2 — VERIFY OAUTH CONFIG & TOKEN")
    print("==========================================")

    from app.services.google_drive_service import _resolve_oauth_token_file, _get_folder_id, GoogleDriveService, _build_drive_service
    from app.config.settings import Config

    token_path = _resolve_oauth_token_file()
    if not token_path or not os.path.isfile(token_path):
        print("[DRIVE] OAuth token file: FAIL — Token file not found")
        root_cause = "OAuth token file (credentials/google_oauth_token.json) is missing."
        manual_action = "Run 'python authorize_google_drive_oauth.py' to generate credentials/google_oauth_token.json."
        return

    print(f"[DRIVE] OAuth token file found: {token_path}")
    results["oauth_setup"] = "PASS"

    try:
        service = _build_drive_service()
        print("[DRIVE] OAuth authentication & client build: PASS")
        results["auth_success"] = "PASS"
    except Exception as exc:
        print(f"[DRIVE] OAuth authentication: FAIL — {exc}")
        root_cause = f"OAuth user credentials authentication failed: {exc}"
        manual_action = "Run 'python authorize_google_drive_oauth.py' to re-authorize the Google Drive account."
        return

    print("\n==========================================")
    print("STEP 3 & 4 — VERIFY TARGET FOLDER ACCESS")
    print("==========================================")

    folder_id = _get_folder_id()
    print(f"[DRIVE] Folder ID resolved: {folder_id}")

    try:
        folder = service.files().get(
            fileId=folder_id,
            fields="id, name, mimeType, trashed",
            supportsAllDrives=True
        ).execute()

        folder_name = folder.get("name", "Unknown")
        is_trashed = folder.get("trashed", False)
        print(f"[DRIVE] Folder access: PASS")
        print(f"[DRIVE] Folder name: {folder_name}")

        if is_trashed:
            print("[DRIVE] Target folder is in Trash.")
            root_cause = f"Target folder '{folder_name}' is in Google Drive Trash."
            manual_action = "Restore target folder from Google Drive Trash."
            return

        results["folder_access"] = "PASS"
    except Exception as exc:
        print(f"[DRIVE] Target folder access: FAIL — {exc}")
        root_cause = f"Target folder access failed under OAuth account: {exc}"
        manual_action = "Ensure the authorized Google Account owns or has Editor access to folder 'GrowCline Interview Recordings'."
        return

    print("\n==========================================")
    print("STEP 5 — VERIFY TXT UPLOAD")
    print("==========================================")

    test_content = b"GrowCline OAuth Drive permission test content."
    test_stream = io.BytesIO(test_content)
    test_filename = "growcline_oauth_test.txt"

    txt_file_id = None
    try:
        txt_file_id = GoogleDriveService.upload_file(
            file_stream=test_stream,
            file_name=test_filename,
            mime_type="text/plain",
            folder_id=folder_id
        )
        print(f"[DRIVE] TXT test upload: PASS")
        print(f"[DRIVE] File ID: {txt_file_id}")

        file_meta = GoogleDriveService.get_file_metadata(txt_file_id)
        size = int(file_meta.get("size", 0))
        name = file_meta.get("name", "")
        print(f"[DRIVE] TXT verification: PASS (Name: {name}, Size: {size} bytes)")

        # Cleanup TXT file
        GoogleDriveService.delete_file(txt_file_id)
        print("[DRIVE] TXT cleanup: PASS")
        results["txt_upload"] = "PASS"
    except Exception as exc:
        print(f"[DRIVE] TXT test upload: FAIL — {exc}")
        root_cause = f"TXT upload under OAuth account failed: {exc}"
        manual_action = "Check OAuth scope permissions for https://www.googleapis.com/auth/drive."
        return

    print("\n==========================================")
    print("STEP 6 — VERIFY SMALL WEBM UPLOAD")
    print("==========================================")

    webm_content = b"\x1a\x45\xdf\xa3\x99\x42\x86\x81\x01\x42\xf7\x81\x01\x42\xf2\x81\x04\x42\xf3\x81\x08\x42\x82\x84webm\x42\x87\x81\x02\x42\x85\x81\x02"
    webm_stream = io.BytesIO(webm_content)
    webm_filename = "test_recording.webm"

    try:
        webm_file_id = GoogleDriveService.upload_file(
            file_stream=webm_stream,
            file_name=webm_filename,
            mime_type="video/webm",
            folder_id=folder_id
        )
        print(f"[DRIVE] WEBM test upload: PASS")
        print(f"[DRIVE] File ID: {webm_file_id}")

        w_meta = GoogleDriveService.get_file_metadata(webm_file_id)
        w_size = int(w_meta.get("size", 0))
        w_mime = w_meta.get("mimeType", "")
        print(f"[DRIVE] WEBM verification: PASS (MIME: {w_mime}, Size: {w_size} bytes)")

        # Cleanup WEBM
        GoogleDriveService.delete_file(webm_file_id)
        print("[DRIVE] WEBM cleanup: PASS")
        results["webm_upload"] = "PASS"
    except Exception as exc:
        print(f"[DRIVE] WEBM test upload: FAIL — {exc}")
        root_cause = f"WEBM upload failed: {exc}"
        return

if __name__ == "__main__":
    run_diagnostic()

    print("\n==========================================")
    print("GOOGLE DRIVE USER OAUTH DIAGNOSTIC REPORT")
    print("==========================================")
    print(f"1. OAuth setup completed:              {results['oauth_setup']}")
    print(f"2. Authorization successful:           {results['auth_success']}")
    print(f"3. Drive folder accessible:            {results['folder_access']}")
    print(f"4. TXT test upload:                    {results['txt_upload']}")
    print(f"5. WEBM test upload:                   {results['webm_upload']}")

    print("\nROOT CAUSE")
    print("==========")
    if root_cause:
        print(root_cause)
    else:
        print("None. All Google Drive User OAuth independent tests PASSED!")

    if results["webm_upload"] == "PASS":
        print("\nIF PASSED")
        print("=========")
        print("Independent Drive OAuth test PASSED! Ready to test FastAPI endpoint and end-to-end recording flow.")
    else:
        print("\nIF FAILED")
        print("=========")
        print(manual_action if manual_action else "Check error traceback above.")
