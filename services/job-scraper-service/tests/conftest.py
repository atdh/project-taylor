# services/job-scraper-service/tests/conftest.py
import sys
import os
import pprint

# Path to the service root directory (containing src and tests)
SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # .../job-scraper-service

# Path to the common_utils directory (relative to this conftest.py)
COMMON_UTILS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'common-utils')) # .../project-taylor/common-utils

# --- Add paths to sys.path ---

# Add Service Root first to allow tests to import 'src.*'
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)
    print(f"DEBUG [conftest.py]: Added SERVICE_ROOT to sys.path[0]: {SERVICE_ROOT}")

# Add common_utils directory specifically to allow imports like 'common_utils.*'
if COMMON_UTILS_DIR not in sys.path:
    # Insert after SERVICE_ROOT
    sys.path.insert(1, COMMON_UTILS_DIR)
    print(f"DEBUG [conftest.py]: Added COMMON_UTILS_DIR to sys.path[1]: {COMMON_UTILS_DIR}")

# --- Optional: Print sys.path for more debugging if needed ---
# print("DEBUG [conftest.py]: Final sys.path:")
# pprint.pprint(sys.path)