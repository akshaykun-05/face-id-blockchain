"""Face detection using InsightFace and CPU inference."""

from pathlib import Path
from typing import Any

import cv2
from insightface.app import FaceAnalysis

from .config import (
    FACE_DETECTION_SIZE,
    FACE_DETECTION_THRESHOLD,
    FACE_MODEL_NAME,
)


class FaceDetector:
    """Load an image and select the highest-confidence detected face."""

    def __init__(
        self,
        model_name: str = FACE_MODEL_NAME,
        detection_size: int = FACE_DETECTION_SIZE,
        detection_threshold: float = FACE_DETECTION_THRESHOLD,
    ) -> None:
        self.detection_threshold = detection_threshold
        self._analysis = FaceAnalysis(
            name=model_name,
            providers=["CPUExecutionProvider"],
        )
        self._analysis.prepare(
            ctx_id=0,
            det_size=(detection_size, detection_size),
            det_thresh=detection_threshold,
        )

    @staticmethod
    def load_image(image_path: str) -> Any:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Input image does not exist: {image_path}")

        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"OpenCV could not read the input image: {image_path}")
        return image

    def detect(self, image: Any) -> Any:
        faces = self._analysis.get(image)
        valid_faces = [
            face
            for face in faces
            if float(getattr(face, "det_score", 0.0)) >= self.detection_threshold
        ]
        if not valid_faces:
            return None
        return max(valid_faces, key=lambda face: float(face.det_score))

    def detect_from_path(self, image_path: str) -> tuple[Any, Any]:
        image = self.load_image(image_path)
        return image, self.detect(image)
