import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import torch
import logging
import numpy as np
import torch.nn as nn
from PIL import Image
from typing import Tuple
from torchvision import models, transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

from analysis.utils import DestandardizeAge
from processor.processor import ImagePreprocessor
from analysis.load_models.regressor import ResNet50Regressor
from configs.config import GENDER_DETECTOR, AGE_DETECTOR_WEIGHTS


# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Analyzer:
    """
    Analyzer class to predict age, gender, and generate embeddings from images.
    """

    def __init__(self, identify_age: bool = False, identify_gender: bool = False):
        """
        Initialize the Analyzer class.

        Args:
            identify_age (bool, optional): Flag to enable age prediction. Defaults to False.
            identify_gender (bool, optional): Flag to enable gender prediction. Defaults to False.
        """
        self.identify_age = identify_age
        self.identify_gender = identify_gender

        if identify_age:
            try:
                self.preprocessor = ImagePreprocessor()
                self.age_model = ResNet50Regressor(AGE_DETECTOR_WEIGHTS)
                logger.info("Age detection model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load age detection model: {e}")
                raise 

        if identify_gender:
            try:
                self.gender_preprocessor = AutoImageProcessor.from_pretrained(GENDER_DETECTOR, use_fast=True)
                self.gender_model = AutoModelForImageClassification.from_pretrained(GENDER_DETECTOR)
                logger.info("Gender detection model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load gender detection model: {e}")
                raise

        try:
            resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
            self.embedding_model = nn.Sequential(*list(resnet.children())[:-1])  # Remove FC layer
            self.embedding_model.eval()
            logger.info("Embedding model initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise 

        self.destandardizer = DestandardizeAge()

    def get_age_gender(self, image: Image.Image) -> Tuple[int, str]:
        """
        Predict age and gender for a given image.

        Args:
            image (PIL.Image.Image): Input image.

        Returns:
            Tuple[int, str]: Predicted age and gender ('Male', 'Female', or 'Neutral').
        """
        age = 0  # Default age
        gender = 'Neutral'  # Default gender

        if self.identify_age:
            try:
                inputs = self.preprocessor.preprocess(image)
                age_output = self.age_model.predict(inputs)
                age = round(self.destandardizer.destandardize_age(age_output[0][0]))
                # logger.info(f"Predicted age: {age}")
            except Exception as e:
                logger.error(f"Error during age prediction, returning the default age: {e}")

        if self.identify_gender:
            try:
                inputs = self.gender_preprocessor(image, return_tensors="pt")
                gender_output = self.gender_model(**inputs)
                gender = ["Female", "Male"][gender_output.logits.argmax(1).item()]
                # logger.info(f"Predicted gender: {gender}")
            except Exception as e:
                logger.error(f"Error during gender prediction, returning the default gender: {e}")

        return age, gender

    def get_embedding(self, image: Image.Image) -> np.ndarray:
        """
        Generate embeddings for a given image.

        Args:
            image (PIL.Image.Image): Input image.

        Returns:
            np.ndarray: Extracted feature embedding as a 1D numpy array.
        """
        try:
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            preprocessed_image = transform(image).unsqueeze(0)
            with torch.no_grad():
                embedding = self.embedding_model(preprocessed_image).squeeze().numpy()
            # logger.info("Generated embedding successfully.")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise