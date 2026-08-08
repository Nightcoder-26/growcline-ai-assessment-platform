"""
Google Drive Service
Isolated Google Drive API client for the Video Recording module.

Responsibilities:
- Authenticate to Google Drive via Service Account (or Application Default Credentials)
- Verify Google Drive connection on application startup
- Upload recording files to a configured private Drive folder
- Delete Drive files (for recording deletion and rollback cleanup)
- Check file existence
- Stream/download Drive file content for backend-proxied playback

Authentication:
    Credentials are loaded from the path specified in GOOGLE_APPLICATION_CREDENTIALS
    or GOOGLE_DRIVE_CREDENTIALS_FILE.
    The service account must have Editor access to the GOOGLE_DRIVE_FOLDER_ID folder.
    NEVER hardcode credentials in this file.
"""

import io
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — the google libraries are optional at import time so that
# other modules do not break if they are not yet installed.
# ---------------------------------------------------------------------------

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account
    from google.auth.exceptions import GoogleAuthError
    from google.auth import default as google_auth_default
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False

# Scope required to manage files in Drive
_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

# Global cached drive service client instance
_drive_service_instance = None


def _resolve_credentials_file() -> Optional[str]:
    """
    Search candidate paths for the Service Account JSON credentials file.
    Returns the absolute or relative path to a valid existing file, or None.
    """
    try:
        from app.config.settings import Config
    except ImportError:
        from config.settings import Config  # type: ignore

    candidates = [
        getattr(Config, "GOOGLE_APPLICATION_CREDENTIALS", None),
        getattr(Config, "GOOGLE_DRIVE_CREDENTIALS_FILE", None),
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        os.environ.get("GOOGLE_DRIVE_CREDENTIALS_FILE"),
        "credentials/google-drive-credentials.json",
        "credentials/google-drive-credentials.json.json",
        "credentials/google_drive_credentials.json",
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _resolve_oauth_token_file() -> Optional[str]:
    """
    Search candidate paths for the User OAuth JSON token file.
    Returns the absolute or relative path to a valid existing file, or None.
    """
    try:
        from app.config.settings import Config
    except ImportError:
        from config.settings import Config  # type: ignore

    candidates = [
        getattr(Config, "GOOGLE_TOKEN_FILE", None),
        os.environ.get("GOOGLE_TOKEN_FILE"),
        "credentials/google_oauth_token.json",
        "tokens/google_oauth_token.json",
        "token.json",
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _build_drive_service():
    """
    Build and return an authenticated Google Drive v3 service object.
    Priority 1: User OAuth 2.0 Credentials (from token file)
    Priority 2: Service Account JSON Credentials
    Priority 3: Application Default Credentials

    Returns:
        googleapiclient Resource — the authenticated Drive v3 service.

    Raises:
        RuntimeError: if google libraries are not installed or auth fails.
    """
    global _drive_service_instance
    if _drive_service_instance is not None:
        return _drive_service_instance

    if not _GOOGLE_AVAILABLE:
        raise RuntimeError(
            "Google Drive client libraries are not installed. "
            "Run: pip install google-api-python-client google-auth google-auth-httplib2"
        )

    # ── Priority 1: User OAuth 2.0 Credentials ───────────────────────────────
    token_file = _resolve_oauth_token_file()
    if token_file:
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            creds = Credentials.from_authorized_user_file(token_file, scopes=_DRIVE_SCOPES)
            if creds and creds.expired and creds.refresh_token:
                logger.info("Google Drive: refreshing expired OAuth access token...")
                creds.refresh(Request())
                try:
                    with open(token_file, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
                except Exception as w_err:
                    logger.warning("Could not persist refreshed OAuth token to file: %s", w_err)

            if creds and creds.valid:
                service = build("drive", "v3", credentials=creds, cache_discovery=False)
                _drive_service_instance = service
                logger.info("Google Drive: authenticated via OAuth 2.0 User Account.")
                return service
        except Exception as exc:
            logger.warning("Google Drive: OAuth token authentication failed, attempting fallback: %s", exc)

    # ── Priority 2 & 3: Service Account / ADC ────────────────────────────────
    credentials_file = _resolve_credentials_file()
    credentials = None

    if credentials_file:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=_DRIVE_SCOPES,
            )
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
            logger.debug("Google Drive: authenticated via service account file.")
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load Google Drive service account credentials: {exc}"
            ) from exc
    else:
        try:
            credentials, _ = google_auth_default(scopes=_DRIVE_SCOPES)
            logger.debug("Google Drive: authenticated via Application Default Credentials.")
        except Exception as exc:
            raise RuntimeError(
                "Google Drive authentication failed. "
                "Configure OAuth token file, GOOGLE_APPLICATION_CREDENTIALS, or Application Default Credentials. "
                f"Details: {exc}"
            ) from exc

    try:
        service = build("drive", "v3", credentials=credentials, cache_discovery=False)
        _drive_service_instance = service
        return service
    except Exception as exc:
        raise RuntimeError(
            f"Failed to build Google Drive service client: {exc}"
        ) from exc


def _get_folder_id() -> str:
    """
    Return the configured Google Drive folder ID.

    Raises:
        RuntimeError: when GOOGLE_DRIVE_FOLDER_ID is not set.
    """
    try:
        from app.config.settings import Config
    except ImportError:
        from config.settings import Config  # type: ignore

    folder_id = getattr(Config, "GOOGLE_DRIVE_FOLDER_ID", "") or os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
    if not folder_id:
        raise RuntimeError(
            "GOOGLE_DRIVE_FOLDER_ID is not configured. "
            "Set it to the Google Drive folder ID where recordings should be stored."
        )
    return folder_id


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class GoogleDriveService:
    """
    Stateless service class providing Google Drive operations
    for the Video Recording module.
    """

    @staticmethod
    def verify_connection() -> bool:
        """
        Verify Google Drive API authentication and folder access on startup.
        Confirms service account credentials and folder existence without uploading files.

        Returns:
            bool — True if authentication and folder access succeeded.

        Raises:
            RuntimeError: if credentials or folder access verification fails.
        """
        try:
            service = _build_drive_service()
            folder_id = _get_folder_id()

            # Retrieve folder metadata to confirm permission & access
            folder = (
                service.files()
                .get(fileId=folder_id, fields="id, name, mimeType")
                .execute()
            )

            logger.info("Google Drive storage initialized successfully")
            return True

        except Exception as exc:
            logger.error("Google Drive connection verification failed: %s", exc)
            raise RuntimeError(
                f"Google Drive initialization failed: {exc}"
            ) from exc

    @staticmethod
    def upload_file(
        file_stream: io.IOBase,
        file_name: str,
        mime_type: str,
        folder_id: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> str:
        """
        Upload a file stream to Google Drive.

        The file is uploaded into the configured folder with the given name.
        Visibility is restricted — no public sharing is applied.

        Args:
            file_stream: A readable binary stream (e.g., UploadFile.file).
            file_name:   Safe server-generated filename (e.g., interview_abc_20260806T143000Z.webm).
            mime_type:   Validated MIME type string (e.g., "video/webm").
            folder_id:   Override folder ID; falls back to GOOGLE_DRIVE_FOLDER_ID if None.
            file_size:   Optional byte count for resumable upload chunking.

        Returns:
            str — the Google Drive file ID of the uploaded file.

        Raises:
            RuntimeError: on authentication failure or API error.
        """
        if folder_id is None:
            folder_id = _get_folder_id()

        service = _build_drive_service()

        file_metadata = {
            "name": file_name,
            "parents": [folder_id],
        }

        # Rewind the stream before upload
        try:
            file_stream.seek(0)
        except Exception:
            pass  # Some streams do not support seek

        import socket
        socket.setdefaulttimeout(120)

        media = MediaIoBaseUpload(
            file_stream,
            mimetype=mime_type,
            resumable=True,
            chunksize=1024 * 1024,  # 1 MB chunks for reliable SSL streaming
        )

        try:
            logger.info("Google Drive: starting upload of '%s' to folder '%s'.", file_name, folder_id)
            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,name,size,mimeType",
            )

            response = None
            retry_count = 0
            max_retries = 3

            while response is None:
                try:
                    status, response = request.next_chunk(num_retries=3)
                    if status:
                        logger.debug(
                            "Google Drive: uploaded %d%% of '%s'",
                            int(status.progress() * 100),
                            file_name,
                        )
                except Exception as exc:
                    err_str = str(exc)
                    if (
                        "EOF" in err_str
                        or "ssl" in err_str.lower()
                        or "socket" in err_str.lower()
                        or "connection" in err_str.lower()
                    ) and retry_count < max_retries:
                        retry_count += 1
                        logger.warning(
                            "Google Drive: SSL socket connection drop during upload of '%s', retrying attempt %d/%d: %s",
                            file_name,
                            retry_count,
                            max_retries,
                            exc,
                        )
                        import time
                        time.sleep(1)
                        continue
                    raise

            drive_file_id = response.get("id") if response else None
            logger.info(
                "Google Drive: upload completed. file_name='%s' drive_file_id='%s'.",
                file_name,
                drive_file_id,
            )
            return drive_file_id

        except HttpError as exc:
            status_code = exc.resp.status if exc.resp else "unknown"
            logger.error(
                "Google Drive: upload failed for '%s'. HTTP %s: %s",
                file_name,
                status_code,
                exc,
            )
            if status_code == 403:
                raise RuntimeError(
                    "Google Drive upload failed: insufficient permissions. "
                    "Ensure the service account has Editor access to the target folder."
                ) from exc
            if status_code == 507 or "storageQuotaExceeded" in str(exc):
                raise RuntimeError(
                    "Google Drive upload failed: storage quota exceeded."
                ) from exc
            raise RuntimeError(
                f"Google Drive upload failed (HTTP {status_code}). Please try again."
            ) from exc

        except Exception as exc:
            logger.error("Google Drive: unexpected error during upload of '%s': %s", file_name, exc)
            err_msg = str(exc)
            if "EOF" in err_msg or "ssl" in err_msg.lower():
                raise RuntimeError(
                    "Google Drive upload failed due to a temporary SSL connection drop. Please click Upload again to retry."
                ) from exc
            raise RuntimeError(
                f"Google Drive upload failed: {exc}"
            ) from exc

    @staticmethod
    def delete_file(drive_file_id: str) -> bool:
        """
        Permanently delete a file from Google Drive by its file ID.

        Args:
            drive_file_id: str — the Google Drive file ID.

        Returns:
            bool — True if deletion succeeded, False if already absent or error occurred.
        """
        service = _build_drive_service()

        try:
            service.files().delete(fileId=drive_file_id).execute()
            logger.info("Google Drive: deleted file '%s'.", drive_file_id)
            return True

        except HttpError as exc:
            status_code = exc.resp.status if exc.resp else None
            if status_code == 404:
                logger.warning(
                    "Google Drive: file '%s' not found during deletion (already removed).",
                    drive_file_id,
                )
                return True  # Idempotent delete

            logger.error(
                "Google Drive: failed to delete file '%s'. HTTP %s: %s",
                drive_file_id,
                status_code,
                exc,
            )
            return False

        except Exception as exc:
            logger.error(
                "Google Drive: unexpected error deleting file '%s': %s",
                drive_file_id,
                exc,
            )
            return False

    @staticmethod
    def get_file_metadata(drive_file_id: str) -> dict:
        """
        Retrieve metadata for a Drive file.

        Args:
            drive_file_id: str — the Google Drive file ID.

        Returns:
            dict — with keys: id, name, size, mimeType.

        Raises:
            ValueError: if the file is not found (404).
            RuntimeError: on other API errors.
        """
        service = _build_drive_service()

        try:
            metadata = (
                service.files()
                .get(fileId=drive_file_id, fields="id,name,size,mimeType")
                .execute()
            )
            return metadata

        except HttpError as exc:
            status_code = exc.resp.status if exc.resp else None
            if status_code == 404:
                raise ValueError(
                    f"Google Drive file '{drive_file_id}' not found."
                ) from exc
            raise RuntimeError(
                f"Google Drive metadata fetch failed (HTTP {status_code})."
            ) from exc

    @staticmethod
    def file_exists(drive_file_id: str) -> bool:
        """
        Check whether a Drive file with the given ID exists and is accessible.
        """
        try:
            GoogleDriveService.get_file_metadata(drive_file_id)
            return True
        except (ValueError, RuntimeError):
            return False

    @staticmethod
    def download_file(drive_file_id: str) -> io.BytesIO:
        """
        Download the binary content of a Drive file into a BytesIO buffer.

        Args:
            drive_file_id: str — the Google Drive file ID.

        Returns:
            io.BytesIO — the file content positioned at byte 0.

        Raises:
            ValueError: if the file is not found (404).
            RuntimeError: on other API errors or auth failure.
        """
        service = _build_drive_service()

        try:
            request = service.files().get_media(fileId=drive_file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request, chunksize=8 * 1024 * 1024)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            buffer.seek(0)
            logger.info("Google Drive: download complete for file '%s'.", drive_file_id)
            return buffer

        except HttpError as exc:
            status_code = exc.resp.status if exc.resp else None
            if status_code == 404:
                raise ValueError(
                    f"Google Drive file '{drive_file_id}' not found or not accessible."
                ) from exc
            raise RuntimeError(
                f"Google Drive download failed (HTTP {status_code}). Please try again."
            ) from exc

        except Exception as exc:
            logger.error(
                "Google Drive: unexpected error downloading file '%s': %s",
                drive_file_id,
                exc,
            )
            raise RuntimeError(
                f"Google Drive download failed: {exc}"
            ) from exc
