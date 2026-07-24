"""
GrowCline Assessment Backend
Exposes main FastAPI app instance for imports.
"""

import sys
import os
import importlib.util

# Load FastAPI app instance from root app.py
if "__app_py__" in sys.modules:
    app = sys.modules["__app_py__"].app
else:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_py_path = os.path.join(root_dir, "app.py")
    if os.path.exists(app_py_path):
        spec = importlib.util.spec_from_file_location("__app_py__", app_py_path)
        app_mod = importlib.util.module_from_spec(spec)
        sys.modules["__app_py__"] = app_mod
        spec.loader.exec_module(app_mod)
        app = app_mod.app
    else:
        app = None