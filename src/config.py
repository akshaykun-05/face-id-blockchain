"""Environment-backed configuration for Phase 1."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

FACE_MODEL_NAME = os.getenv("FACE_MODEL_NAME", "buffalo_l")
FACE_DETECTION_SIZE = int(os.getenv("FACE_DETECTION_SIZE", "640"))
FACE_DETECTION_THRESHOLD = float(os.getenv("FACE_DETECTION_THRESHOLD", "0.50"))
