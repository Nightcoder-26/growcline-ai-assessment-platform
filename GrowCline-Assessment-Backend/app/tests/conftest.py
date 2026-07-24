import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing any modules
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-purposes-minimum-length"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-purposes-minimum-length"

# Insert backend directory into sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import app.config.database
import app.config.settings

# Provide module aliases for legacy test imports if necessary
sys.modules["config"] = sys.modules["app.config"]
sys.modules["config.database"] = sys.modules["app.config.database"]
sys.modules["config.settings"] = sys.modules["app.config.settings"]


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture for test suite."""
    from app import app
    with TestClient(app) as test_client:
        yield test_client
