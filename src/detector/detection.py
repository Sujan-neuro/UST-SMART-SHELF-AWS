import logging
import numpy as np
from typing import Optional, Tuple
from deepface import DeepFace

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class DeepFaceDetector:
    """
    Detects and extracts faces using DeepFace, with optional retry
    if strict detection fails.
    """

    def __init__(self, confidence: float = 0.8, min_face_ratio: float = 0.1):
        self.confidence = confidence
        self.min_face_ratio = min_face_ratio

    def _extract(self, frame: np.ndarray, enforce: bool) -> list:
        """
        Wrapper around DeepFace.extract_faces that passes through enforce_detection
        and raises DeepFaceError on failure.
        """
        return DeepFace.extract_faces(
            img_path = frame,
            detector_backend = "opencv",
            enforce_detection = enforce,
        )

    def detect_faces(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detects faces in a given frame.

        Args:
            frame (np.ndarray): BGR image.

        Returns:
            Optional[Tuple[int,int,int,int]]: (x1,y1,x2,y2) or None.
        """
        try:
            frame_h, frame_w = frame.shape[:2]
            frame_area = frame_h * frame_w

            # First attempt: strict detection
            try:
                detected = self._extract(frame, enforce=True)
            except ValueError as e:
                detected = self._extract(frame, enforce=False)

            if not detected:
                return None

            # Filter by confidence
            valid = [f for f in detected if f.get("confidence", 0) >= self.confidence]
            if not valid:
                return None

            # Pick the largest face
            face = max(valid, key=lambda f: f["facial_area"]["w"] * f["facial_area"]["h"])
            x1 = int(face["facial_area"]["x"])
            y1 = int(face["facial_area"]["y"])
            w  = int(face["facial_area"]["w"])
            h  = int(face["facial_area"]["h"])
            x2, y2 = x1 + w, y1 + h

            # Size check
            if (w * h) / frame_area < self.min_face_ratio:
                return None

            # logger.debug(f"Detected face at ({x1},{y1},{x2},{y2}) with confidence {face['confidence']:.2f}")
            return x1, y1, x2, y2

        except Exception:
            logger.exception("Unexpected error during face detection")
            return None