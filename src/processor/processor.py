import sys
import os
import logging
from typing import Tuple, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PIL import Image
from datetime import datetime
from torchvision import transforms

from processor.utils import (cosine_distance, 
                   LimitedDict, 
                   DailyIndex,
                   craft_payload
                   )
from configs.config import (EMBEDDING_THRESHOLD, 
                    MAX_EMBEDDING_TO_MATCH
                    )

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# Image preprocessing class
class ImagePreprocessor:
    """
    A class to handle image preprocessing for model inference.
    """

    def __init__(self):
        """
        Initializes the image preprocessing pipeline with resizing, 
        normalization, and conversion to tensor.
        """
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        logger.info("ImagePreprocessor initialized.")

    def preprocess(self, image: Image.Image) -> Any:
        """
        Preprocesses the given image.

        Args:
            image (Image.Image): The image to be preprocessed.

        Returns:
            Any: The preprocessed image tensor.
        """
        try:
            image_tensor = self.transform(image).unsqueeze(0)  # Add batch dimension
            # logger.debug("Image preprocessed successfully.")
            return image_tensor
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None


class Processor:
    """
    A class that processes frames from a video or camera feed, detecting faces,
    and extracting/associating embeddings.
    """

    def __init__(self, detector, analyzer):
        """
        Initializes the Processor with a face detector and analyzer.

        Args:
            detector: Face detection model.
            analyzer: Face analysis model.
        """
        self.detector = detector
        self.analyzer = analyzer
        self.embeddings = LimitedDict(max_size=MAX_EMBEDDING_TO_MATCH)
        self.daily_index = DailyIndex()
        logger.info("Processor initialized with detector and analyzer.")

    def process_frame(self, frame: Any) -> Tuple:
        """
        Processes a single frame, detects faces, generates embeddings, 
        and returns either matched visitor data or a new visitor entry.

        Args:
            frame (Any): The frame from the video stream or camera feed.

        Returns:
            Tuple: A tuple containing the bounding box of detected face(s) and the visitor's information.
        """
        try:
            nearest_person_bbox = self.detector.detect_faces(frame)
            today = datetime.now()
            output = False

            if nearest_person_bbox is not None:
                x1, y1, x2, y2 = map(int, nearest_person_bbox)
                cropped_face = frame[y1:y2, x1:x2]
                cropped_face_pil = Image.fromarray(cropped_face)

                age, gender = self.analyzer.get_age_gender(cropped_face_pil)
                embedding = self.analyzer.get_embedding(cropped_face_pil)

                matched = False
                for visitor_id, stored_embedding in self.embeddings.items():
                    if cosine_distance(embedding, stored_embedding) < EMBEDDING_THRESHOLD:
                        self.embeddings[visitor_id] = (stored_embedding + embedding) / 2
                        matched = True
                        output = craft_payload(visitor_id, age, gender, today)
                        # logger.info(f"Visitor matched: {visitor_id}")
                        break

                if not matched:
                    index = self.daily_index.get_index()
                    new_id = f"{today.strftime('%Y%m%d')}_{index}"
                    self.embeddings[new_id] = embedding
                    output = craft_payload(new_id, age, gender, today)
                    # logger.info(f"New visitor created: {new_id}")
            else:
                # logger.debug("No face detected in the frame.")
                pass

            return nearest_person_bbox, output
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return None, None