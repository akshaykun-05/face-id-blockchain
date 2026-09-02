"""Phase 1: detect one face, encode it, and persist a commitment."""

import json
from pathlib import Path
from typing import Any

import cv2

from .face_detector import FaceDetector
from .face_encoder import FaceEncoder

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
FACE_CROP_PATH = OUTPUT_DIR / "detected_face.jpg"
RESULT_PATH = OUTPUT_DIR / "phase1_result.json"


class FaceNotFoundError(RuntimeError):
    """Raised when no face meets the configured detection threshold."""


def _crop_face(image: Any, face: Any) -> Any:
    height, width = image.shape[:2]
    x1, y1, x2, y2 = [int(round(value)) for value in face.bbox]
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    if x2 < x1 or y2 < y1:
        raise ValueError("Detected face bounding box is outside the image")
    return image[y1 : y2 + 1, x1 : x2 + 1]


def run_phase1(image_path: str) -> dict[str, object]:
    """Run Phase 1 and return the metadata written to the result JSON."""
    print("[1/4] Loading image...")
    image = FaceDetector.load_image(image_path)
    print("      OK Image loaded")

    print("[2/4] Detecting face...")
    detector = FaceDetector()
    face = detector.detect(image)
    if face is None:
        print("ERROR: No face detected above the configured confidence threshold.")
        raise FaceNotFoundError("No face detected")
    print("      OK Face detected")

    print("[3/4] Generating face embedding...")
    normalized_embedding = FaceEncoder.encode(face)
    embedding_dimensions = int(normalized_embedding.size)
    print(f"      OK Embedding generated ({embedding_dimensions} dimensions)")

    print("[4/4] Creating biometric commitment...")
    commitment = FaceEncoder.commitment(normalized_embedding)
    print("      OK Commitment generated")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    crop = _crop_face(image, face)
    if not cv2.imwrite(str(FACE_CROP_PATH), crop):
        raise OSError(f"Could not save face crop: {FACE_CROP_PATH}")

    result = {
        "phase": 1,
        "face_detected": True,
        "face_confidence": round(float(face.det_score), 4),
        "embedding_dimensions": embedding_dimensions,
        "face_embedding_commitment": commitment,
        "face_crop": "data/output/detected_face.jpg",
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("\n------------------------------------------------------------")
    print("PHASE 1 COMPLETE")
    print("------------------------------------------------------------")
    print(f"\nFace confidence : {result['face_confidence']}")
    print(f"Embedding size  : {embedding_dimensions}")
    print(f"Commitment      : {commitment}")
    print("Face crop saved : data/output/detected_face.jpg")
    print("Result saved    : data/output/phase1_result.json")
    print("\nNOTE: Raw face embedding remains off-chain.")
    return result
