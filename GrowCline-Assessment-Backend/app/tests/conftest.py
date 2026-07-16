import os
import sys

# Set test environment variables before importing any modules
os.environ["JWT_SECRET"] = "test-secret"
os.environ["JWT_SECRET_KEY"] = "test-secret"

# Insert backend directory and app directory into sys.path to resolve imports correctly
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(backend_dir, "app")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Pre-import key config modules
import app.config.database
import app.config.settings

# Alias config modules to prevent double-importing/duplicate classes
sys.modules["config"] = sys.modules["app.config"]
sys.modules["config.database"] = sys.modules["app.config.database"]
sys.modules["config.settings"] = sys.modules["app.config.settings"]
