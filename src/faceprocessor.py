import cv2
import time
import logging
from detector.detection import DeepFaceDetector
from analysis.analysis import Analyzer
from processor.processor import Processor

from configs.config import (
    PROCESS_INTERVAL_SEC,
    TRACKING_DURATION_SEC,
    CONFIDENCE_THRESHOLD,
    MIN_FACE_RATIO,
    DEFAULT_CAMERA_INDEX
)
from configs.utils import IDTracker

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class FaceProcessor:
    def __init__(
        self,
        process_interval_sec: int = PROCESS_INTERVAL_SEC,
        tracking_duration_sec: int = TRACKING_DURATION_SEC,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        min_face_ratio: float = MIN_FACE_RATIO,
        default_camera_index: int = DEFAULT_CAMERA_INDEX,
        identify_age: bool = False,
        identify_gender: bool = False
    ) -> None:
        """Initializes the FaceProcessor with detection, analysis, processing, tracking, and video capture."""
        try:
            self.process_interval_sec = process_interval_sec
            self.tracking_duration_sec = tracking_duration_sec
            self.confidence_threshold = confidence_threshold
            self.min_face_ratio = min_face_ratio
            self.default_camera_index = default_camera_index
            self.identify_age = identify_age
            self.identify_gender = identify_gender

            self._initialize_components()
            self._initialize_camera()

        except Exception as e:
            logging.error(f"Error initializing FaceProcessor: {e}", exc_info=True)

    def _initialize_components(self) -> None:
        """Initializes detector, analyzer, processor, and tracker components."""
        try:
            self.detector = DeepFaceDetector(
                confidence=self.confidence_threshold,
                min_face_ratio=self.min_face_ratio
            )
            self.analyzer = Analyzer(
                identify_age=self.identify_age,
                identify_gender=self.identify_gender
            )
            self.processor = Processor(self.detector, self.analyzer)
            self.tracker = IDTracker(self.tracking_duration_sec)
            self.last_save_time = time.time()
            logging.info("Components initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing components: {e}", exc_info=True)
            raise

    def _initialize_camera(self) -> None:
        """Initializes the video capture device."""
        try:
            self.cap = cv2.VideoCapture(self.default_camera_index)
            if self.cap.isOpened():
                logging.info("Camera has opened successfully.")
            else:
                logging.error("Could not open webcam.")
        except Exception as e:
            logging.error(f"Error initializing camera: {e}", exc_info=True)
            raise

    def __del__(self) -> None:
        """Ensures resources are released on object deletion."""
        try:
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
                logging.info("Camera released successfully.")
        except Exception as e:
            logging.error(f"Error releasing camera: {e}", exc_info=True)