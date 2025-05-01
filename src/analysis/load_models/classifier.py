import torch
import numpy as np
import torch.nn as nn
from torchvision import models

class ResNet50Classifier:
    """
    A ResNet50-based binary classification model wrapper for predicting labels from images.
    """

    def __init__(self, weight_path: str, device: str = None):
        """
        Initializes the classifier by building architecture and loading pre-trained weights.

        Args:
            weight_path (str): Path to the saved model weights (.pth file).
            device (str, optional): Device to run the model on ('cuda' or 'cpu'). Defaults to automatic selection.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()
        self._load_weights(weight_path)

    def _build_model(self) -> nn.Module:
        """
        Builds the ResNet50 model modified for binary classification.

        Returns:
            nn.Module: The modified ResNet50 model.
        """
        model = models.resnet50(pretrained=False)
        model.fc = nn.Sequential(
            nn.Linear(model.fc.in_features, 1),
            nn.Sigmoid()  # Sigmoid to output probability between 0 and 1
        )
        return model.to(self.device)

    def _load_weights(self, weight_path: str):
        """
        Loads model weights from the given path and adjusts key names if necessary.

        Args:
            weight_path (str): Path to the saved model weights (.pth file).
        """
        state_dict = torch.load(weight_path, map_location=self.device)

        # Adjust key names for models using Sequential
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = key.replace("fc", "fc.0")  # Adjust keys for Sequential layer
            new_state_dict[new_key] = value

        self.model.load_state_dict(new_state_dict, strict=False)
        self.model.eval()

    def predict(self, image_tensor: torch.Tensor) -> np.ndarray:
        """
        Predicts the probability for the input image tensor.

        Args:
            image_tensor (torch.Tensor): Input image tensor of shape (batch_size, 3, H, W).

        Returns:
            np.ndarray: Model prediction output as a NumPy array with probabilities.
        """
        image_tensor = image_tensor.to(self.device)
        with torch.no_grad():
            output = self.model(image_tensor)  # Output is already sigmoid-ed
        return output.cpu().numpy()