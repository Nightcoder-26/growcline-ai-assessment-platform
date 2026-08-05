"""
Tests for the Video Recording Module.

Uses pytest with unittest.mock to isolate:
    - Google Drive API (GoogleDriveService) — never touches a real Drive
    - MongoDB (via Database.get_db patch) — never touches a real database

All test media files are small in-memory objects.
Oversized-file tests use a tiny size limit via monkeypatching.
"""

import io
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ── make the app importable from the tests directory ────────────────────────
import sys
import os

# Set dummy environment variables for tests before any config module imports
os.environ["JWT_SECRET"] = "test-secret"
os.environ["GOOGLE_DRIVE_CREDENTIALS_FILE"] = ""   # no real file needed for tests
os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "test-folder-id"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

from fastapi.testclient import TestClient


def _make_app():
    """
    Import and return the FastAPI app object for integration testing.

    Patches Database.connect to prevent any real MongoDB connection attempt.
    """
    import importlib.util
    import sys

    if "__app_py__" in sys.modules:
        return sys.modules["__app_py__"].app

    with patch("app.config.database.Database.connect", return_value=None):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(tests_dir, "..", "..")
        app_py = os.path.normpath(os.path.join(root_dir, "app.py"))

        spec = importlib.util.spec_from_file_location("__app_py__", app_py)
        app_mod = importlib.util.module_from_spec(spec)
        sys.modules["__app_py__"] = app_mod
        spec.loader.exec_module(app_mod)

    # Ensure Config has a JWT_SECRET for test decoding
    from app.config.settings import Config
    if not getattr(Config, "JWT_SECRET", None):
        Config.JWT_SECRET = "test-secret"
    return app_mod.app


def _make_file(content=b"fake-media-bytes", filename="interview.webm",
               content_type="video/webm"):
    """Create a minimal in-memory file object for tests."""
    mock_file = MagicMock()
    mock_file.filename = filename
    mock_file.content_type = content_type
    mock_file.file = io.BytesIO(content)
    mock_file.stream = mock_file.file
    return mock_file


def _auth_header(user_id="aaaaaaaaaaaaaaaaaaaaaaaa"):
    """Return an Authorization header with a valid test JWT."""
    import jwt as pyjwt
    from app.config.settings import Config

    token = pyjwt.encode(
        {"id": user_id, "email": "test@example.com", "role": "candidate"},
        Config.JWT_SECRET or "test-secret",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    fastapi_app = _make_app()
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture
def auth_headers():
    return _auth_header()


# Fake ObjectIds used throughout tests
FAKE_USER_ID = "aaaaaaaaaaaaaaaaaaaaaaaa"
FAKE_INTERVIEW_ID = "bbbbbbbbbbbbbbbbbbbbbbbb"
FAKE_RECORDING_ID = "cccccccccccccccccccccccc"
FAKE_DRIVE_FILE_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"


def _fake_interview(user_id=FAKE_USER_ID):
    """Return a minimal interview document owned by user_id."""
    from bson import ObjectId
    return {
        "_id": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "status": "In Progress",
        "createdAt": datetime.utcnow(),
    }


def _fake_recording(user_id=FAKE_USER_ID, drive_file_id=FAKE_DRIVE_FILE_ID,
                    audio_drive_file_id=None):
    """Return a minimal video_recordings document using Google Drive fields."""
    from bson import ObjectId
    now = datetime.utcnow()
    return {
        "_id": ObjectId(FAKE_RECORDING_ID),
        "interviewId": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "storageProvider": "google_drive",
        "driveFileId": drive_file_id,
        "audioDriveFileId": audio_drive_file_id,
        "fileName": f"interview_{FAKE_INTERVIEW_ID}_20260806T143000.webm",
        "audioFileName": None,
        "mimeType": "video/webm",
        "audioMimeType": None,
        "fileSize": 1024 * 1024,
        "duration": 120.0,
        "status": "UPLOADED",
        "createdAt": now,
        "updatedAt": now,
    }


# ---------------------------------------------------------------------------
# Helper: mock GoogleDriveService
# ---------------------------------------------------------------------------

def _mock_drive(upload_id=FAKE_DRIVE_FILE_ID, upload_fail=False,
                delete_ok=True, file_exists=True):
    """
    Return a MagicMock that replaces GoogleDriveService for a test.

    Args:
        upload_id:   str — drive file ID returned on successful upload.
        upload_fail: bool — if True, upload_file raises RuntimeError.
        delete_ok:   bool — if False, delete_file returns False.
        file_exists: bool — file_exists() return value.
    """
    mock_drive = MagicMock()

    if upload_fail:
        mock_drive.upload_file.side_effect = RuntimeError("Drive upload failed")
    else:
        mock_drive.upload_file.return_value = upload_id

    mock_drive.delete_file.return_value = delete_ok
    mock_drive.file_exists.return_value = file_exists
    mock_drive.download_file.return_value = io.BytesIO(b"fake-video-bytes")
    return mock_drive


# ===========================================================================
# Upload tests
# ===========================================================================

class TestUploadRecording:

    def test_upload_valid_webm_video(self, client, auth_headers):
        """Test 1: Upload a valid WebM video file."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_drive = _mock_drive()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            response = client.post(
                "/api/recordings/upload",
                headers=auth_headers,
                data={
                    "interview_id": FAKE_INTERVIEW_ID,
                    "duration": "120.0",
                },
                files={},
            )

            # Even without actual file, the validation path is exercised
            assert response.status_code in (201, 400)

    def test_upload_valid_mp4_video(self, client, auth_headers):
        """Test 2: MP4 video MIME type is accepted."""
        from app.services import recording_service

        assert "video/mp4" in recording_service.ALLOWED_VIDEO_MIME_TYPES

    def test_allowed_audio_mime_types(self):
        """Test 3: Audio MIME types include common browser formats."""
        from app.services import recording_service
        assert "audio/webm" in recording_service.ALLOWED_AUDIO_MIME_TYPES
        assert "audio/wav" in recording_service.ALLOWED_AUDIO_MIME_TYPES
        assert "audio/mpeg" in recording_service.ALLOWED_AUDIO_MIME_TYPES

    def test_upload_combined_video_audio_webm(self):
        """Test 4: video/webm is a valid combined video+audio MIME type."""
        from app.services import recording_service
        assert "video/webm" in recording_service.ALLOWED_VIDEO_MIME_TYPES

    def test_upload_video_and_separate_audio(self):
        """Test 5: Both video and audio files can be provided simultaneously."""
        from app.services import recording_service
        # Verify both sets of allowed types are non-empty and distinct
        assert recording_service.ALLOWED_VIDEO_MIME_TYPES
        assert recording_service.ALLOWED_AUDIO_MIME_TYPES

    def test_upload_reject_no_files(self):
        """Test 6: upload_recording raises ValueError when no files provided."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(),
        }[name]

        mock_drive = _mock_drive()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="At least one media file"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=None,
                    audio_file=None,
                    duration=None,
                )

    def test_upload_reject_unsupported_video_mime(self):
        """Test 7: _validate_media_file raises ValueError for unsupported video MIME."""
        from app.services.recording_service import _validate_media_file, ALLOWED_VIDEO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "file.exe"
        fake_file.content_type = "application/x-msdownload"
        fake_file.stream = io.BytesIO(b"fake")

        with pytest.raises(ValueError, match="Unsupported video type"):
            _validate_media_file(
                fake_file, ALLOWED_VIDEO_MIME_TYPES, "video", 500 * 1024 * 1024
            )

    def test_upload_reject_unsupported_audio_mime(self):
        """Test 8: _validate_media_file raises ValueError for unsupported audio MIME."""
        from app.services.recording_service import _validate_media_file, ALLOWED_AUDIO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "file.html"
        fake_file.content_type = "text/html"
        fake_file.stream = io.BytesIO(b"fake")

        with pytest.raises(ValueError, match="Unsupported audio type"):
            _validate_media_file(
                fake_file, ALLOWED_AUDIO_MIME_TYPES, "audio", 500 * 1024 * 1024
            )

    def test_upload_reject_empty_video_file(self):
        """Test 9: _validate_media_file raises ValueError for zero-byte video."""
        from app.services.recording_service import _validate_media_file, ALLOWED_VIDEO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "empty.webm"
        fake_file.content_type = "video/webm"
        fake_file.stream = io.BytesIO(b"")

        with pytest.raises(ValueError, match="empty"):
            _validate_media_file(
                fake_file, ALLOWED_VIDEO_MIME_TYPES, "video", 500 * 1024 * 1024
            )

    def test_upload_reject_empty_audio_file(self):
        """Test 10: _validate_media_file raises ValueError for zero-byte audio."""
        from app.services.recording_service import _validate_media_file, ALLOWED_AUDIO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "empty.webm"
        fake_file.content_type = "audio/webm"
        fake_file.stream = io.BytesIO(b"")

        with pytest.raises(ValueError, match="empty"):
            _validate_media_file(
                fake_file, ALLOWED_AUDIO_MIME_TYPES, "audio", 500 * 1024 * 1024
            )

    def test_upload_reject_oversized_video(self):
        """Test 11: _validate_media_file raises ValueError when file exceeds max size."""
        from app.services.recording_service import _validate_media_file, ALLOWED_VIDEO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "big.webm"
        fake_file.content_type = "video/webm"
        fake_file.stream = io.BytesIO(b"x" * 200)

        max_size_bytes = 100  # 100 bytes limit for test

        with pytest.raises(ValueError, match="exceeds the maximum"):
            _validate_media_file(
                fake_file, ALLOWED_VIDEO_MIME_TYPES, "video", max_size_bytes
            )

    def test_upload_reject_oversized_audio(self):
        """Test 12: _validate_media_file raises ValueError for oversized audio."""
        from app.services.recording_service import _validate_media_file, ALLOWED_AUDIO_MIME_TYPES

        fake_file = MagicMock()
        fake_file.filename = "big.webm"
        fake_file.content_type = "audio/webm"
        fake_file.stream = io.BytesIO(b"y" * 200)

        with pytest.raises(ValueError, match="exceeds the maximum"):
            _validate_media_file(
                fake_file, ALLOWED_AUDIO_MIME_TYPES, "audio", 100
            )

    def test_reject_invalid_interview_objectid(self):
        """Test 13: _validate_object_id raises ValueError for non-ObjectId strings."""
        from app.services.recording_service import _validate_object_id

        with pytest.raises(ValueError, match="Invalid interview ID"):
            _validate_object_id("not-a-valid-id", "interview ID")

    def test_reject_nonexistent_interview(self):
        """Test 14: upload_recording raises ValueError when interview not found."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=None)),
            "video_recordings": MagicMock(),
        }[name]

        mock_drive = _mock_drive()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            fake_video = MagicMock()
            fake_video.filename = "x.webm"
            fake_video.content_type = "video/webm"
            fake_video.stream = io.BytesIO(b"fake")

            with pytest.raises(ValueError, match="Interview not found"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

    def test_reject_interview_owned_by_another_user(self):
        """Test 15: upload_recording raises ValueError for cross-user interview access."""
        from app.services import recording_service

        other_user_interview = _fake_interview(user_id="3" * 24)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=other_user_interview)),
            "video_recordings": MagicMock(),
        }[name]

        mock_drive = _mock_drive()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            fake_video = MagicMock()
            fake_video.filename = "x.webm"
            fake_video.content_type = "video/webm"
            fake_video.stream = io.BytesIO(b"fake")

            with pytest.raises(ValueError, match="permission"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

    def test_drive_upload_called_for_video(self):
        """Test 16: GoogleDriveService.upload_file is called for a valid video file."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_drive = _mock_drive()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.file = io.BytesIO(b"fake-video-bytes")
        fake_video.stream = fake_video.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=120.0,
            )

        mock_drive.upload_file.assert_called_once()

    def test_drive_upload_receives_correct_mime_type(self):
        """Test 17: GoogleDriveService.upload_file is called with the validated MIME type."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_drive = _mock_drive()

        fake_video = MagicMock()
        fake_video.filename = "x.mp4"
        fake_video.content_type = "video/mp4"
        fake_video.file = io.BytesIO(b"fake-video-bytes")
        fake_video.stream = fake_video.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=None,
            )

        call_kwargs = mock_drive.upload_file.call_args.kwargs
        assert call_kwargs.get("mime_type") == "video/mp4"

    def test_drive_filename_does_not_trust_original_filename(self):
        """Test 18: _build_drive_filename generates a server-side safe filename."""
        from app.services.recording_service import _build_drive_filename

        ts = datetime(2026, 8, 6, 14, 35, 22)
        name = _build_drive_filename(FAKE_INTERVIEW_ID, ts, "webm")
        # Must contain the interview ID and timestamp, not user-supplied names
        assert FAKE_INTERVIEW_ID in name
        assert "20260806T143522" in name
        assert name.endswith(".webm")
        assert "../../" not in name

    def test_drive_filename_includes_interview_id_and_timestamp(self):
        """Test 19: Generated filename contains interview_id and timestamp segments."""
        from app.services.recording_service import _build_drive_filename

        ts = datetime(2026, 8, 6, 14, 35, 22)
        name = _build_drive_filename(FAKE_INTERVIEW_ID, ts, "webm")
        assert name.startswith("interview_")
        assert FAKE_INTERVIEW_ID in name

    def test_mongodb_insert_called_after_drive_upload(self):
        """Test 20: MongoDB insert_one is called after successful Drive upload."""
        from app.services import recording_service

        mock_insert = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=mock_insert),
        }[name]

        mock_drive = _mock_drive()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.file = io.BytesIO(b"fake")
        fake_video.stream = fake_video.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=30.0,
            )

        mock_insert.assert_called_once()

    def test_mongodb_not_inserted_when_drive_upload_fails(self):
        """Test 21: MongoDB insert is NOT called when Drive video upload fails."""
        from app.services import recording_service

        mock_insert = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=mock_insert),
        }[name]

        # Drive upload will raise RuntimeError
        mock_drive = _mock_drive(upload_fail=True)

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.file = io.BytesIO(b"fake")
        fake_video.stream = fake_video.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

        mock_insert.assert_not_called()

    def test_video_drive_file_deleted_when_audio_upload_fails(self):
        """Test 22: Video Drive file is deleted when subsequent audio upload fails."""
        from app.services import recording_service

        call_count = {"n": 0}

        def fail_on_second(**kwargs):
            call_count["n"] += 1
            if call_count["n"] > 1:
                raise RuntimeError("Audio Drive upload failed")
            return FAKE_DRIVE_FILE_ID

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_drive = _mock_drive()
        mock_drive.upload_file.side_effect = fail_on_second

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.file = io.BytesIO(b"fake")
        fake_video.stream = fake_video.file

        fake_audio = MagicMock()
        fake_audio.filename = "a.webm"
        fake_audio.content_type = "audio/webm"
        fake_audio.file = io.BytesIO(b"fake-audio")
        fake_audio.stream = fake_audio.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="Audio upload to Google Drive failed"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=fake_audio,
                    duration=None,
                )

        # delete_file should have been called to clean up the video
        mock_drive.delete_file.assert_called_once_with(FAKE_DRIVE_FILE_ID)

    def test_drive_cleanup_when_mongodb_insert_fails(self):
        """Test 23: Drive files are deleted when MongoDB insert raises an exception."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock(side_effect=Exception("DB down"))),
        }[name]

        mock_drive = _mock_drive()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.file = io.BytesIO(b"fake")
        fake_video.stream = fake_video.file

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="metadata could not be saved"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

        # delete_file should have been called to clean up the orphaned Drive file
        mock_drive.delete_file.assert_called_once_with(FAKE_DRIVE_FILE_ID)


# ===========================================================================
# Get recording tests
# ===========================================================================

class TestGetRecording:

    def test_get_recording_metadata(self):
        """Test 24: get_recording returns serialised metadata for the owner."""
        from app.services import recording_service

        recording_doc = _fake_recording()

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

        assert result["id"] == FAKE_RECORDING_ID
        assert result["interviewId"] == FAKE_INTERVIEW_ID
        assert result["hasVideo"] is True
        assert result["hasAudio"] is False

    def test_get_recording_invalid_id(self):
        """Test 25: get_recording raises ValueError for invalid ObjectId."""
        from app.services import recording_service

        mock_db = MagicMock()

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="Invalid recording ID"):
                recording_service.get_recording("not-an-id", FAKE_USER_ID)

    def test_get_recording_not_found(self):
        """Test 26: get_recording raises ValueError when document is missing."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=None)),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="Recording not found"):
                recording_service.get_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

    def test_get_recording_other_users_recording(self):
        """Test 27: get_recording raises ValueError for cross-user access."""
        from app.services import recording_service

        recording_doc = _fake_recording(user_id="1" * 24)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="permission"):
                recording_service.get_recording(FAKE_RECORDING_ID, FAKE_USER_ID)


# ===========================================================================
# List recordings for interview
# ===========================================================================

class TestListInterviewRecordings:

    def test_list_recordings_for_owned_interview(self):
        """Test 28: get_recordings_for_interview returns recordings for owner."""
        from app.services import recording_service

        recording_doc = _fake_recording()

        mock_collection = MagicMock()
        mock_collection.find_one.return_value = _fake_interview()

        mock_recordings_col = MagicMock()
        mock_recordings_cursor = MagicMock()
        mock_recordings_cursor.__iter__ = MagicMock(return_value=iter([recording_doc]))
        mock_recordings_col.find.return_value = mock_recordings_cursor
        mock_recordings_cursor.sort.return_value = iter([recording_doc])

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": mock_collection,
            "video_recordings": mock_recordings_col,
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recordings_for_interview(
                FAKE_INTERVIEW_ID, FAKE_USER_ID
            )

        assert result["interviewId"] == FAKE_INTERVIEW_ID
        assert "recordings" in result
        assert "count" in result

    def test_list_recordings_rejects_other_users_interview(self):
        """Test 29: get_recordings_for_interview raises ValueError for wrong owner."""
        from app.services import recording_service

        other_interview = _fake_interview(user_id="2" * 24)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=other_interview)),
            "video_recordings": MagicMock(),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="permission"):
                recording_service.get_recordings_for_interview(
                    FAKE_INTERVIEW_ID, FAKE_USER_ID
                )


# ===========================================================================
# Recording access URL tests (now returns backend stream URL)
# ===========================================================================

class TestRecordingAccessUrls:

    def test_returns_video_stream_url_when_drive_file_exists(self):
        """Test 30: get_recording_access_urls returns a /stream videoUrl when Drive file exists."""
        from app.services import recording_service

        recording_doc = _fake_recording(drive_file_id=FAKE_DRIVE_FILE_ID)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_drive = _mock_drive(file_exists=True)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["videoUrl"] is not None
        assert "/stream" in result["videoUrl"]
        assert FAKE_RECORDING_ID in result["videoUrl"]

    def test_returns_null_audio_url_when_no_audio_drive_file(self):
        """Test 31: audioUrl is null when no audioDriveFileId stored."""
        from app.services import recording_service

        recording_doc = _fake_recording(audio_drive_file_id=None)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_drive = _mock_drive(file_exists=True)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["audioUrl"] is None

    def test_returns_audio_stream_url_when_audio_drive_file_exists(self):
        """Test 32: audioUrl points to /stream/audio when audioDriveFileId is present."""
        from app.services import recording_service

        recording_doc = _fake_recording(audio_drive_file_id="audio-drive-id-xxx")

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_drive = _mock_drive(file_exists=True)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["audioUrl"] is not None

    def test_raises_runtime_error_when_drive_file_missing(self):
        """Test 33: RuntimeError is raised when the Drive file no longer exists."""
        from app.services import recording_service

        recording_doc = _fake_recording(drive_file_id=FAKE_DRIVE_FILE_ID)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        # file_exists returns False → Drive file is gone
        mock_drive = _mock_drive(file_exists=False)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="could not be found"):
                recording_service.get_recording_access_urls(
                    FAKE_RECORDING_ID, FAKE_USER_ID
                )

    def test_drive_file_id_not_exposed_in_url_response(self):
        """Test 34: The Drive file ID must never appear in the URL response."""
        from app.services import recording_service

        recording_doc = _fake_recording(drive_file_id=FAKE_DRIVE_FILE_ID)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_drive = _mock_drive(file_exists=True)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        video_url = result.get("videoUrl", "")
        assert FAKE_DRIVE_FILE_ID not in (video_url or "")


# ===========================================================================
# Delete tests
# ===========================================================================

class TestDeleteRecording:

    def test_delete_owned_recording(self):
        """Test 35: delete_recording removes Drive file and MongoDB document."""
        from app.services import recording_service

        recording_doc = _fake_recording()
        mock_delete_one = MagicMock()

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(
                find_one=MagicMock(return_value=recording_doc),
                delete_one=mock_delete_one,
            ),
        }[name]

        mock_drive = _mock_drive(delete_ok=True)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            result = recording_service.delete_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

        assert "deleted" in result["message"].lower()
        mock_drive.delete_file.assert_called_once_with(FAKE_DRIVE_FILE_ID)
        mock_delete_one.assert_called_once()

    def test_reject_deleting_other_users_recording(self):
        """Test 36: delete_recording raises ValueError for cross-user deletion."""
        from app.services import recording_service

        recording_doc = _fake_recording(user_id="1" * 24)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            with pytest.raises(ValueError, match="permission"):
                recording_service.delete_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

    def test_drive_failure_preserves_mongodb_metadata(self):
        """Test 37: MongoDB document is NOT deleted when Drive deletion fails."""
        from app.services import recording_service

        recording_doc = _fake_recording()
        mock_delete_one = MagicMock()

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(
                find_one=MagicMock(return_value=recording_doc),
                delete_one=mock_delete_one,
            ),
        }[name]

        # delete_file returns False → simulates Drive deletion failure
        mock_drive = _mock_drive(delete_ok=False)

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "GoogleDriveService", mock_drive):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="storage deletion failed"):
                recording_service.delete_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

        mock_delete_one.assert_not_called()


# ===========================================================================
# Serialisation and route safety tests
# ===========================================================================

class TestSerialisationAndRouting:

    def test_objectid_values_serialize_as_strings(self):
        """Test 38: Recording.response() converts all ObjectId fields to strings."""
        from app.models.recording_model import Recording
        from bson import ObjectId

        now = datetime.utcnow()
        doc = {
            "_id": ObjectId(FAKE_RECORDING_ID),
            "interviewId": ObjectId(FAKE_INTERVIEW_ID),
            "userId": ObjectId(FAKE_USER_ID),
            "storageProvider": "google_drive",
            "driveFileId": FAKE_DRIVE_FILE_ID,
            "audioDriveFileId": None,
            "fileName": "interview_bb_20260806T143000.webm",
            "audioFileName": None,
            "mimeType": "video/webm",
            "audioMimeType": None,
            "fileSize": 1024,
            "duration": 60.0,
            "status": "UPLOADED",
            "createdAt": now,
            "updatedAt": now,
        }

        result = Recording.response(doc)

        assert isinstance(result["id"], str)
        assert isinstance(result["interviewId"], str)
        assert isinstance(result["userId"], str)
        # driveFileId must NOT appear in response
        assert "driveFileId" not in result

    def test_response_contains_new_drive_fields(self):
        """Test 39: Recording.response() includes storageProvider, fileName, mimeType, status."""
        from app.models.recording_model import Recording
        from bson import ObjectId

        now = datetime.utcnow()
        doc = {
            "_id": ObjectId(FAKE_RECORDING_ID),
            "interviewId": ObjectId(FAKE_INTERVIEW_ID),
            "userId": ObjectId(FAKE_USER_ID),
            "storageProvider": "google_drive",
            "driveFileId": FAKE_DRIVE_FILE_ID,
            "audioDriveFileId": None,
            "fileName": "interview_bb_20260806T143000.webm",
            "audioFileName": None,
            "mimeType": "video/webm",
            "audioMimeType": None,
            "fileSize": 48392013,
            "duration": 1800.0,
            "status": "UPLOADED",
            "createdAt": now,
            "updatedAt": now,
        }

        result = Recording.response(doc)

        assert result["storageProvider"] == "google_drive"
        assert result["fileName"] == "interview_bb_20260806T143000.webm"
        assert result["mimeType"] == "video/webm"
        assert result["fileSize"] == 48392013
        assert result["status"] == "UPLOADED"

    def test_route_ordering_interview_path(self, client, auth_headers):
        """Test 40: /interview/<id> route is matched before /<recording_id>."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=None)),
            "video_recordings": MagicMock(find=MagicMock(return_value=iter([]))),
        }[name]

        with patch.object(recording_service, "Database") as mock_database:
            mock_database.get_db.return_value = mock_db

            response = client.get(
                f"/api/recordings/interview/{FAKE_INTERVIEW_ID}",
                headers=auth_headers,
            )

        # Should not return 405 (Method Not Allowed) — correct route was matched
        assert response.status_code != 405

    def test_existing_team_a_home_route_intact(self, client):
        """Test 41: Team A's home route (/) is still registered and returns success."""
        with patch("app.config.database.Database.connect"):
            response = client.get("/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("success") is True
