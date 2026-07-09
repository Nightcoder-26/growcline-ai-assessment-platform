"""
Unit and integration tests for live proctoring and monitoring features.

Uses pytest with unittest.mock to isolate:
    - MongoDB (via Database.get_db patch) — never touches a real database
"""

import sys
import os
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set dummy environment variables for tests before any config module imports
os.environ["JWT_SECRET"] = "test-secret"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bson import ObjectId

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

def _make_app():
    """
    Import and return the FastAPI app object for integration testing.
    Patches Database.connect to prevent any real MongoDB connection attempt.
    """
    import importlib.util
    import sys

    # Clear cached modules related to the app to ensure they are reloaded with new contents
    for key in list(sys.modules.keys()):
        if key.startswith("app.") or key == "app" or key == "__app_py__" or key == "__flask_app__":
            sys.modules.pop(key, None)

    with patch("app.config.database.Database.connect", return_value=None):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(tests_dir, "..", "..")
        app_py = os.path.normpath(os.path.join(root_dir, "app.py"))

        spec = importlib.util.spec_from_file_location("__app_py__", app_py)
        app_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_mod)

    # Ensure Config has a JWT_SECRET for test decoding
    from app.config.settings import Config
    if not getattr(Config, "JWT_SECRET", None):
        Config.JWT_SECRET = "test-secret"
    return app_mod.app


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


# Global mock database reference for the currently executing test
_current_mock_db = None

@pytest.fixture(autouse=True)
def mock_db_global():
    """
    Autouse fixture that patches Database.get_db globally.
    Prevents actual MongoDB connections and ensures any import path
    (app.config.database or config.database) gets the same mock DB.
    """
    global _current_mock_db
    _current_mock_db = MagicMock()

    def get_active_mock():
        return _current_mock_db

    with patch("app.config.database.Database.get_db", side_effect=get_active_mock), \
         patch("config.database.Database.get_db", side_effect=get_active_mock, create=True):
        yield _current_mock_db

    _current_mock_db = None


FAKE_USER_ID = "aaaaaaaaaaaaaaaaaaaaaaaa"
FAKE_INTERVIEW_ID = "bbbbbbbbbbbbbbbbbbbbbbbb"
FAKE_EVENT_ID = "cccccccccccccccccccccccc"


def _fake_interview(user_id=FAKE_USER_ID, status="In Progress"):
    """Return a minimal interview document owned by user_id."""
    return {
        "_id": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "status": status,
        "createdAt": datetime.utcnow(),
    }


def _fake_proctoring_log(event_type="TAB_SWITCH", severity="MEDIUM", user_id=FAKE_USER_ID, client_ts=None):
    """Return a minimal proctoring_logs document."""
    return {
        "_id": ObjectId(FAKE_EVENT_ID),
        "interviewId": ObjectId(FAKE_INTERVIEW_ID),
        "userId": ObjectId(user_id),
        "eventType": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow(),
        "clientTimestamp": client_ts,
    }


# ===========================================================================
# Live Proctoring Single Event Creation Tests
# ===========================================================================

class TestCreateProctoringEvent:

    def test_create_valid_tab_switch_event(self, client, auth_headers):
        """Test 1: Create valid TAB_SWITCH event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["eventType"] == "TAB_SWITCH"
        assert data["data"]["severity"] == "MEDIUM"

    def test_create_valid_window_minimized_event(self, client, auth_headers):
        """Test 2: Create valid WINDOW_MINIMIZED event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "WINDOW_MINIMIZED"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "MEDIUM"

    def test_create_valid_multiple_faces_event(self, client, auth_headers):
        """Test 3: Create valid MULTIPLE_FACES event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "MULTIPLE_FACES"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "HIGH"

    def test_create_valid_background_voice_event(self, client, auth_headers):
        """Test 4: Create valid BACKGROUND_VOICE event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "BACKGROUND_VOICE"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "HIGH"

    def test_create_proctoring_started_event(self, client, auth_headers):
        """Test 5: Create PROCTORING_STARTED event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "PROCTORING_STARTED"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "INFO"

    def test_create_proctoring_stopped_event(self, client, auth_headers):
        """Test 6: Create PROCTORING_STOPPED event."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "PROCTORING_STOPPED"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "INFO"

    def test_severity_is_derived_serverside(self, client, auth_headers):
        """Test 7: Client cannot control severity; it is derived server-side."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "MULTIPLE_FACES",
                "severity": "LOW"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["severity"] == "HIGH"

    def test_invalid_event_type_rejected(self, client, auth_headers):
        """Test 8: Invalid event type is rejected with a 400."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "USING_MOBILE_PHONE"
            }
        )

        assert response.status_code == 400
        assert "Unsupported event type" in response.json()["message"]

    def test_invalid_interview_objectid_rejected(self, client, auth_headers):
        """Test 9: Invalid interview ObjectId string is rejected."""
        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": "not-an-object-id",
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 400
        assert "Invalid interview ID" in response.json()["message"]

    def test_nonexistent_interview_rejected(self, client, auth_headers):
        """Test 10: Nonexistent interview is rejected with a 404."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=None)),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 404
        assert "Interview not found" in response.json()["message"]

    def test_other_users_interview_rejected(self, client, auth_headers):
        """Test 11: Accessing another user's interview returns 403."""
        global _current_mock_db
        other_user_interview = _fake_interview(user_id="1" * 24)
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=other_user_interview)),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 403
        assert "permission" in response.json()["message"]

    def test_completed_interview_rejected(self, client, auth_headers):
        """Test 12: Cannot log events for a completed or cancelled interview."""
        global _current_mock_db
        completed_interview = _fake_interview(status="Completed")
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=completed_interview)),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 400
        assert "Cannot accept proctoring events" in response.json()["message"]

    def test_client_cannot_inject_userid(self, client, auth_headers):
        """Test 13: Request schema does not accept userId as trusted ownership data."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH",
                "userId": "1" * 24
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["userId"] == FAKE_USER_ID

    def test_canonical_timestamp_generated_by_server(self, client, auth_headers):
        """Test 14: Canonical timestamp is generated by the server."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 201
        assert "timestamp" in response.json()["data"]

    def test_invalid_client_timestamp_rejected(self, client, auth_headers):
        """Test 15: Future client timestamp beyond 5-minute tolerance is rejected."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(),
        }[name]

        future_time = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH",
                "client_timestamp": future_time
            }
        )

        assert response.status_code == 400
        assert "timestamp cannot be in the future" in response.json()["message"]

    def test_event_metadata_controlled_or_absent(self, client, auth_headers):
        """Test 16: Arbitrary metadata fields are ignored or omitted to prevent arbitrary injection."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH",
                "extra_hacky_field": "dangerous"
            }
        )

        assert response.status_code == 201
        assert "extra_hacky_field" not in response.json()["data"]

    def test_duplicate_noisy_event_suppressed(self, client, auth_headers):
        """Test 17: Cooldown of 2 seconds works (returns latest duplicate log instead of double inserting)."""
        global _current_mock_db
        recent_log = _fake_proctoring_log(event_type="TAB_SWITCH")
        recent_log["timestamp"] = datetime.utcnow() - timedelta(seconds=1)

        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=recent_log),
                insert_one=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 201
        assert response.json()["data"]["id"] == str(recent_log["_id"])
        _current_mock_db["proctoring_logs"].insert_one.assert_not_called()

    def test_event_outside_cooldown_stored(self):
        """Test 18: Different event types or event outside cooldown gets inserted."""
        from app.services import proctoring_service

        global _current_mock_db
        old_log = _fake_proctoring_log(event_type="TAB_SWITCH")
        old_log["timestamp"] = datetime.utcnow() - timedelta(seconds=5)

        mock_logs = MagicMock(
            find_one=MagicMock(return_value=old_log),
            insert_one=MagicMock()
        )
        db_cols = {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": mock_logs,
        }
        _current_mock_db.__getitem__.side_effect = lambda name: db_cols[name]

        result = proctoring_service.create_proctoring_event(
            FAKE_INTERVIEW_ID, FAKE_USER_ID, "TAB_SWITCH"
        )

        assert result["id"] != str(old_log["_id"])
        mock_logs.insert_one.assert_called_once()

    def test_different_event_types_not_deduplicated(self):
        """Test 19: Distinct event types logged within 2 seconds are not suppressed."""
        from app.services import proctoring_service

        global _current_mock_db
        mock_logs = MagicMock(
            find_one=MagicMock(return_value=None),
            insert_one=MagicMock()
        )
        db_cols = {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": mock_logs,
        }
        _current_mock_db.__getitem__.side_effect = lambda name: db_cols[name]

        result = proctoring_service.create_proctoring_event(
            FAKE_INTERVIEW_ID, FAKE_USER_ID, "WINDOW_BLUR"
        )

        assert result is not None
        mock_logs.insert_one.assert_called_once()

    def test_mongodb_insert_failure_returns_safe_error(self, client, auth_headers):
        """Test 20: Database write failure returns 500 without leaking stack traces."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_one=MagicMock(side_effect=RuntimeError("MongoDB is down"))
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "event_type": "TAB_SWITCH"
            }
        )

        assert response.status_code == 500
        assert "An unexpected error occurred" in response.json()["message"]


# ===========================================================================
# Batch Event Ingestion Tests
# ===========================================================================

class TestBatchIngestion:

    def test_batch_endpoint_accepts_valid_events(self, client, auth_headers):
        """Test 21: Batch endpoint accepts multiple valid events."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(
                find_one=MagicMock(return_value=None),
                insert_many=MagicMock()
            ),
        }[name]

        response = client.post(
            "/api/proctoring/events/batch",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "events": [
                    {"event_type": "TAB_SWITCH"},
                    {"event_type": "WINDOW_MINIMIZED"}
                ]
            }
        )

        assert response.status_code == 201
        assert response.json()["success"] is True
        assert len(response.json()["data"]) == 2

    def test_empty_batch_rejected(self, client, auth_headers):
        """Test 22: Empty batch is rejected with a 400."""
        response = client.post(
            "/api/proctoring/events/batch",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "events": []
            }
        )

        assert response.status_code == 400
        assert "Batch cannot be empty" in response.json()["message"]

    def test_oversized_batch_rejected(self, client, auth_headers):
        """Test 23: Batch size exceeding the limit (50) is rejected."""
        bad_events = [{"event_type": "TAB_SWITCH"}] * 51

        response = client.post(
            "/api/proctoring/events/batch",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "events": bad_events
            }
        )

        assert response.status_code == 400
        assert "exceeds the maximum" in response.json()["message"]

    def test_batch_containing_invalid_event_fully_rejected(self, client, auth_headers):
        """Test 24: Batch containing any invalid event is fully rejected before database write."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(insert_many=MagicMock()),
        }[name]

        response = client.post(
            "/api/proctoring/events/batch",
            headers=auth_headers,
            json={
                "interview_id": FAKE_INTERVIEW_ID,
                "events": [
                    {"event_type": "TAB_SWITCH"},
                    {"event_type": "INVALID_EVENT_HACK"}
                ]
            }
        )

        assert response.status_code == 400
        assert "Unsupported event type" in response.json()["message"]
        _current_mock_db["proctoring_logs"].insert_many.assert_not_called()


# ===========================================================================
# Event Listing and Pagination Tests
# ===========================================================================

class TestGetProctoringEvents:

    def test_get_interview_events_returns_list(self, client, auth_headers):
        """Test 25: Retrieve paged list of events for the interview owner."""
        global _current_mock_db
        mock_logs_col = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = [
            _fake_proctoring_log(event_type="TAB_SWITCH"),
            _fake_proctoring_log(event_type="WINDOW_MINIMIZED"),
        ]
        mock_logs_col.find.return_value = mock_cursor

        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": mock_logs_col,
        }[name]

        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/events?limit=10&skip=0",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["events"]) == 2

    def test_pagination_defaults_applied(self):
        """Test 26: Paging defaults are correctly passed when query params are omitted."""
        from app.services import proctoring_service

        global _current_mock_db
        mock_logs_col = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        mock_logs_col.find.return_value = mock_cursor

        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": mock_logs_col,
        }[name]

        proctoring_service.get_proctoring_events(FAKE_INTERVIEW_ID, FAKE_USER_ID)

        mock_cursor.skip.assert_called_with(0)
        mock_cursor.limit.assert_called_with(50)

    def test_pagination_limit_maximum_enforced(self, client, auth_headers):
        """Test 27: Enforces maximum limit of 100 on pagination."""
        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/events?limit=150",
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_negative_skip_rejected(self, client, auth_headers):
        """Test 28: Negative skip values are rejected."""
        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/events?skip=-5",
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_other_user_cannot_read_events(self, client, auth_headers):
        """Test 29: Other candidates cannot access events they don't own."""
        global _current_mock_db
        other_user_interview = _fake_interview(user_id="1" * 24)
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=other_user_interview)),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/events",
            headers=auth_headers,
        )

        assert response.status_code == 403


# ===========================================================================
# Proctoring Summary and Aggregate Statistics Tests
# ===========================================================================

class TestProctoringSummary:

    def test_proctoring_summary_returns_totals_and_aggregates(self, client, auth_headers):
        """Test 30: Summary returns event statistics grouping by type and severity."""
        global _current_mock_db
        mock_agg_output = [{
            "stats": [{
                "totalEvents": 3,
                "firstEventAt": datetime(2026, 7, 8, 10, 0, 0),
                "lastEventAt": datetime(2026, 7, 8, 10, 5, 0),
            }],
            "byType": [
                {"_id": "TAB_SWITCH", "count": 2},
                {"_id": "MULTIPLE_FACES", "count": 1},
            ],
            "bySeverity": [
                {"_id": "MEDIUM", "count": 2},
                {"_id": "HIGH", "count": 1},
            ]
        }]

        mock_logs_col = MagicMock()
        mock_logs_col.aggregate.return_value = mock_agg_output

        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": mock_logs_col,
        }[name]

        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["totalEvents"] == 3
        assert data["data"]["eventCounts"]["TAB_SWITCH"] == 2
        assert data["data"]["eventCounts"]["MULTIPLE_FACES"] == 1
        assert data["data"]["severityCounts"]["MEDIUM"] == 2
        assert data["data"]["severityCounts"]["HIGH"] == 1
        assert "firstEventAt" in data["data"]
        assert "lastEventAt" in data["data"]

    def test_summary_no_cheating_risk_score(self, client, auth_headers):
        """Test 31: Summary is strictly event-based and must not contain cheating scores or risk levels."""
        global _current_mock_db
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=_fake_interview())),
            "proctoring_logs": MagicMock(aggregate=MagicMock(return_value=[])),
        }[name]

        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/summary",
            headers=auth_headers,
        )

        assert response.status_code == 200
        summary_data = response.json()["data"]
        for key in ["riskScore", "cheatingScore", "riskLevel", "cheatingProbability", "integrityScore"]:
            assert key not in summary_data

    def test_other_user_cannot_retrieve_summary(self, client, auth_headers):
        """Test 32: Other candidates cannot access the summary of an interview they do not own."""
        global _current_mock_db
        other_user_interview = _fake_interview(user_id="2" * 24)
        _current_mock_db.__getitem__.side_effect = lambda name: {
            "interviews": MagicMock(find_one=MagicMock(return_value=other_user_interview)),
            "proctoring_logs": MagicMock(),
        }[name]

        response = client.get(
            f"/api/proctoring/interview/{FAKE_INTERVIEW_ID}/summary",
            headers=auth_headers,
        )

        assert response.status_code == 403


# ===========================================================================
# Router Configuration and System Integration Tests
# ===========================================================================

class TestRouterAndImports:

    def test_router_is_apirouter(self):
        """Test 33: Proctoring router is an instance of FastAPI APIRouter."""
        from app.routes.proctoring_routes import router
        from fastapi import APIRouter
        assert isinstance(router, APIRouter)

    def test_router_registered_in_fastapi(self, client):
        """Test 34: Proctoring endpoints are registered correctly in the FastAPI app."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "GrowCline Backend is Running 🚀"

        routes = []
        for r in client.app.routes:
            if hasattr(r, "path"):
                routes.append(r.path)
            elif type(r).__name__ == "_IncludedRouter":
                for cand in r.effective_candidates():
                    if hasattr(cand, "path"):
                        routes.append(cand.path)

        assert "/api/proctoring/events" in routes
        assert "/api/proctoring/events/batch" in routes
        assert "/api/proctoring/interview/{interview_id}/events" in routes
        assert "/api/proctoring/interview/{interview_id}/summary" in routes

    def test_no_flask_imports_in_source(self):
        """Test 35: Proctoring source files do not import from Flask or utilize Flask patterns."""
        source_paths = [
            "app/routes/proctoring_routes.py",
            "app/controllers/proctoring_controller.py",
            "app/services/proctoring_service.py",
            "app/models/proctoring_model.py"
        ]

        for rel_path in source_paths:
            path = os.path.join(os.path.dirname(__file__), "..", "..", rel_path)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "flask" not in content.lower()
                    assert "blueprint" not in content.lower()
                    assert "jsonify" not in content.lower()

    def test_no_opencv_or_mediapipe_imports(self):
        """Test 36: Proctoring backend does not import heavy CV libraries (OpenCV, MediaPipe, TF)."""
        source_paths = [
            "app/routes/proctoring_routes.py",
            "app/controllers/proctoring_controller.py",
            "app/services/proctoring_service.py",
            "app/models/proctoring_model.py"
        ]

        forbidden = ["cv2", "mediapipe", "tensorflow", "torch", "ultralytics", "librosa", "numpy"]

        for rel_path in source_paths:
            path = os.path.join(os.path.dirname(__file__), "..", "..", rel_path)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for lib in forbidden:
                        assert lib not in content.lower()

    def test_no_cheating_detection_called(self):
        """Test 37: Live Proctoring events logging does not call or calculate cheating scores."""
        source_paths = [
            "app/services/proctoring_service.py"
        ]

        for rel_path in source_paths:
            path = os.path.join(os.path.dirname(__file__), "..", "..", rel_path)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "cheating_detection_service" not in content
                    assert "calculate_cheating" not in content
                    assert "cheating_report" not in content
