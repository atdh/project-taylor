# services/filter-service/tests/conftest.py
import sys
import os

# Path to the service root directory (containing src and tests)
SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Add paths to sys.path ---

# Add Service Root first to allow tests to import 'src.*'
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)
    # print(f"DEBUG [conftest.py]: Added SERVICE_ROOT to sys.path[0]: {SERVICE_ROOT}") # Optional debug

# --- REMOVED COMMON_UTILS_DIR Addition ---
# Relying on 'pip install -e ../../common_utils' making it available due to correct package structure

