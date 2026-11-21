"""Rescue Link — Root entry point for Streamlit Cloud deployment."""

import os
import sys
from pathlib import Path

# Add rescue_link_v2 to Python path and set as working directory
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "rescue_link_v2"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

os.chdir(APP_DIR)

# Launch main Streamlit application
import runpy
runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")
