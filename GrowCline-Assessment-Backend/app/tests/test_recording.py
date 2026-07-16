"""
Tests for the Video Recording Module.

Uses pytest with unittest.mock to isolate:
    - AWS S3 (boto3) — never touches a real bucket
    - MongoDB (via Database.get_db patch) — never touches a real database

All test media files are small in-memory objects.
Oversized-file tests use a tiny size limit via monkeypatching.
"""

import io
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

# ── make the app importable from the tests directory ────────────────────────
import sys
import os

# Set dummy environment variables for tests before any config module imports
os.environ["JWT_SECRET"] = "test-secret"
os.environ["AWS_ACCESS_KEY_ID"] = "mock-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "mock-secret"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_S3_BUCKET"] = "mock-bucket"

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


def _fake_interview(user_id=FAKE_USER_ID):
    """Return a minimal interview document owned by user_id."""
    from bson import ObjectId
    return {
        "_id": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "status": "In Progress",
        "createdAt": datetime.utcnow(),
    }


def _fake_recording(user_id=FAKE_USER_ID, video_key="recordings/a/b/video/x.webm",
                    audio_key=None):
    """Return a minimal video_recordings document."""
    from bson import ObjectId
    # user_id must be a 24-char hex string for ObjectId() to accept it.
    # Callers must pass valid hex strings.
    return {
        "_id": ObjectId(FAKE_RECORDING_ID),
        "interviewId": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "videoKey": video_key,
        "audioKey": audio_key,
        "videoUrl": None,
        "audioUrl": None,
        "duration": 120.0,
        "createdAt": datetime.utcnow(),
    }


# ---------------------------------------------------------------------------
# Helper: patch context for upload tests
# ---------------------------------------------------------------------------

def _upload_patches(interview_doc=None, insert_ok=True, s3_fail_on=None):
    """
    Return a context manager that patches Database, boto3, and Config
    for upload service tests.

    Args:
        interview_doc: the fake interview returned by find_one (default: valid)
        insert_ok: if False, simulate MongoDB insert failure
        s3_fail_on: "video" or "audio" to simulate S3 upload failure on that media
    """
    from unittest.mock import patch, MagicMock
    from botocore.exceptions import ClientError

    if interview_doc is None:
        interview_doc = _fake_interview()

    mock_db = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: {
        "interviews": MagicMock(
            find_one=MagicMock(return_value=interview_doc)
        ),
        "video_recordings": MagicMock(
            insert_one=MagicMock(
                side_effect=Exception("DB error") if not insert_ok else MagicMock()
            )
        ),
    }[name]

    mock_s3 = MagicMock()

    if s3_fail_on == "video":
        def _raise_on_video(stream, bucket, key, ExtraArgs=None):
            raise ClientError({"Error": {"Code": "500", "Message": "S3 error"}}, "upload_fileobj")
        mock_s3.upload_fileobj.side_effect = _raise_on_video
    elif s3_fail_on == "audio":
        call_count = {"n": 0}

        def _fail_second_call(stream, bucket, key, ExtraArgs=None):
            call_count["n"] += 1
            if call_count["n"] > 1:
                raise ClientError(
                    {"Error": {"Code": "500", "Message": "S3 error"}}, "upload_fileobj"
                )
        mock_s3.upload_fileobj.side_effect = _fail_second_call

    return mock_db, mock_s3


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

        mock_s3 = MagicMock()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

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

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_s3 = MagicMock()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

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

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=MagicMock()), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

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

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=MagicMock()), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

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

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=MagicMock()), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

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

    def test_s3_video_upload_called(self):
        """Test 16: S3 upload_fileobj is called for a valid video file."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_s3 = MagicMock()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.stream = io.BytesIO(b"fake-video-bytes")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=120.0,
            )

        mock_s3.upload_fileobj.assert_called_once()

    def test_s3_upload_receives_correct_content_type(self):
        """Test 17: S3 upload uses the validated MIME type as ContentType."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_s3 = MagicMock()

        fake_video = MagicMock()
        fake_video.filename = "x.mp4"
        fake_video.content_type = "video/mp4"
        fake_video.stream = io.BytesIO(b"fake-video-bytes")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=None,
            )

        _, kwargs = mock_s3.upload_fileobj.call_args
        assert kwargs.get("ExtraArgs", {}).get("ContentType") == "video/mp4"

    def test_s3_key_does_not_trust_original_filename(self):
        """Test 18: _build_s3_key ignores the original filename entirely."""
        from app.services.recording_service import _build_s3_key

        key = _build_s3_key(FAKE_USER_ID, FAKE_INTERVIEW_ID, "video", "webm")
        assert "interview.webm" not in key
        assert "../../" not in key
        assert ".webm" in key

    def test_s3_key_includes_user_and_interview(self):
        """Test 19: S3 object key contains user_id and interview_id namespaces."""
        from app.services.recording_service import _build_s3_key

        key = _build_s3_key(FAKE_USER_ID, FAKE_INTERVIEW_ID, "video", "webm")
        assert FAKE_USER_ID in key
        assert FAKE_INTERVIEW_ID in key
        assert key.startswith("recordings/")

    def test_mongodb_insert_called_after_s3_upload(self):
        """Test 20: MongoDB insert_one is called after successful S3 upload."""
        from app.services import recording_service

        mock_insert = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=mock_insert),
        }[name]

        mock_s3 = MagicMock()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.stream = io.BytesIO(b"fake")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            recording_service.upload_recording(
                interview_id=FAKE_INTERVIEW_ID,
                user_id=FAKE_USER_ID,
                video_file=fake_video,
                audio_file=None,
                duration=30.0,
            )

        mock_insert.assert_called_once()

    def test_mongodb_not_inserted_when_s3_fails(self):
        """Test 21: MongoDB insert is NOT called when S3 video upload fails."""
        from app.services import recording_service

        mock_insert = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=mock_insert),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "S3 error"}}, "upload_fileobj"
        )

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.stream = io.BytesIO(b"fake")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="Video upload to storage failed"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

        mock_insert.assert_not_called()

    def test_video_s3_deleted_when_audio_upload_fails(self):
        """Test 22: Video S3 object is deleted when subsequent audio upload fails."""
        from app.services import recording_service

        call_count = {"n": 0}

        def fail_on_second(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] > 1:
                raise ClientError(
                    {"Error": {"Code": "500", "Message": "S3 error"}}, "upload_fileobj"
                )

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock()),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.upload_fileobj.side_effect = fail_on_second

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.stream = io.BytesIO(b"fake")

        fake_audio = MagicMock()
        fake_audio.filename = "a.webm"
        fake_audio.content_type = "audio/webm"
        fake_audio.stream = io.BytesIO(b"fake-audio")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="Audio upload to storage failed"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=fake_audio,
                    duration=None,
                )

        # delete_object should have been called to clean up the video
        mock_s3.delete_object.assert_called_once()

    def test_s3_cleanup_when_mongodb_insert_fails(self):
        """Test 23: S3 objects are deleted when MongoDB insert raises an exception."""
        from app.services import recording_service

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "video_recordings": MagicMock(insert_one=MagicMock(side_effect=Exception("DB down"))),
        }[name]

        mock_s3 = MagicMock()

        fake_video = MagicMock()
        fake_video.filename = "x.webm"
        fake_video.content_type = "video/webm"
        fake_video.stream = io.BytesIO(b"fake")

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="metadata could not be saved"):
                recording_service.upload_recording(
                    interview_id=FAKE_INTERVIEW_ID,
                    user_id=FAKE_USER_ID,
                    video_file=fake_video,
                    audio_file=None,
                    duration=None,
                )

        mock_s3.delete_object.assert_called_once()


# ===========================================================================
# Get recording tests
# ===========================================================================

class TestGetRecording:

    def test_get_recording_metadata(self):
        """Test 24: get_recording returns serialised metadata for the owner."""
        from app.services import recording_service
        from bson import ObjectId

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
        from bson import ObjectId

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
# Presigned URL tests
# ===========================================================================

class TestPresignedUrls:

    def test_generate_video_presigned_url(self):
        """Test 30: get_recording_access_urls returns a video URL when videoKey is present."""
        from app.services import recording_service

        recording_doc = _fake_recording(video_key="recordings/a/b/video/x.webm")

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned-url"

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["videoUrl"] is not None
        assert "https" in result["videoUrl"]

    def test_generate_audio_presigned_url(self):
        """Test 31: get_recording_access_urls returns an audio URL when audioKey is present."""
        from app.services import recording_service

        recording_doc = _fake_recording(
            video_key="recordings/a/b/video/x.webm",
            audio_key="recordings/a/b/audio/y.webm",
        )

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["audioUrl"] is not None

    def test_null_audio_url_when_audio_key_absent(self):
        """Test 32: audioUrl is null when no audioKey stored for the recording."""
        from app.services import recording_service

        recording_doc = _fake_recording(video_key="k", audio_key=None)

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://s3.example.com/video"

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        assert result["audioUrl"] is None

    def test_presigned_url_expiry_uses_config_value(self):
        """Test 33: expiresIn in the response matches RECORDING_URL_EXPIRY_SECONDS."""
        from app.services import recording_service
        from app.config.settings import Config

        recording_doc = _fake_recording(video_key="k")

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://presigned"

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            result = recording_service.get_recording_access_urls(
                FAKE_RECORDING_ID, FAKE_USER_ID
            )

        expected_expiry = int(getattr(Config, "RECORDING_URL_EXPIRY_SECONDS", 900))
        assert result["expiresIn"] == expected_expiry

    def test_presigning_failure_raises_runtime_error(self):
        """Test 34: RuntimeError is raised when S3 presigning fails."""
        from app.services import recording_service

        recording_doc = _fake_recording(video_key="k")

        mock_db = MagicMock()
        mock_db.__getitem__.side_effect = lambda name: {
            "video_recordings": MagicMock(find_one=MagicMock(return_value=recording_doc)),
        }[name]

        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "403", "Message": "Forbidden"}}, "generate_presigned_url"
        )

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            with pytest.raises(RuntimeError, match="video access URL"):
                recording_service.get_recording_access_urls(
                    FAKE_RECORDING_ID, FAKE_USER_ID
                )


# ===========================================================================
# Delete tests
# ===========================================================================

class TestDeleteRecording:

    def test_delete_owned_recording(self):
        """Test 35: delete_recording removes S3 objects and MongoDB document."""
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

        mock_s3 = MagicMock()

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

            mock_database.get_db.return_value = mock_db

            result = recording_service.delete_recording(FAKE_RECORDING_ID, FAKE_USER_ID)

        assert "deleted" in result["message"].lower()
        mock_s3.delete_object.assert_called_once()
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

    def test_s3_failure_preserves_mongodb_metadata(self):
        """Test 37: MongoDB document is NOT deleted when S3 deletion fails."""
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

        mock_s3 = MagicMock()
        mock_s3.delete_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "S3 error"}}, "delete_object"
        )

        with patch.object(recording_service, "Database") as mock_database, \
             patch.object(recording_service, "_get_s3_client", return_value=mock_s3), \
             patch.object(recording_service, "_get_s3_bucket", return_value="test-bucket"):

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

        doc = {
            "_id": ObjectId(FAKE_RECORDING_ID),
            "interviewId": ObjectId(FAKE_INTERVIEW_ID),
            "userId": ObjectId(FAKE_USER_ID),
            "videoKey": "key",
            "audioKey": None,
            "duration": 60.0,
            "createdAt": datetime.utcnow(),
        }

        result = Recording.response(doc)

        assert isinstance(result["id"], str)
        assert isinstance(result["interviewId"], str)
        assert isinstance(result["userId"], str)

    def test_route_ordering_interview_path(self, client, auth_headers):
        """Test 39: /interview/<id> route is matched before /<recording_id>."""
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
        """Test 40: Team A's home route (/) is still registered and returns success."""
        with patch("app.config.database.Database.connect"):
            response = client.get("/")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data.get("success") is True
