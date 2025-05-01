import torch
import numpy as np
import torch.nn as nn
from torchvision import models


class ResNet50Regressor:
    """
    A ResNet50-based regression model wrapper for predicting continuous values from images.
    """

    def __init__(self, weight_path: str, device: str = None):
        """
        Initializes the model by building architecture and loading weights.

        Args:
            weight_path (str): Path to the saved model weights (.pth file).
            device (str, optional): Device to run the model on ('cuda' or 'cpu'). Defaults to automatic selection.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()
        self._load_weights(weight_path)

    def _build_model(self) -> nn.Module:
        """
        Builds the ResNet50 model modified for regression.

        Returns:
            nn.Module: The modified ResNet50 model.
        """
        model = models.resnet50(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 1)  # Replace final layer for regression output
        return model.to(self.device)

    def _load_weights(self, weight_path: str):
        """
        Loads model weights from a given path and handles key mismatches if needed.

        Args:
            weight_path (str): Path to the saved model weights (.pth file).
        """
        state_dict = torch.load(weight_path, map_location=self.device)
        
        # Adjust key names if necessary
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = key.replace("fc.0", "fc")  # Handle case where model was saved with Sequential
            new_state_dict[new_key] = value

        self.model.load_state_dict(new_state_dict)
        self.model.eval()

    def predict(self, image_tensor: torch.Tensor) -> np.ndarray:
        """
        Predicts the continuous output from a given input tensor.

        Args:
            image_tensor (torch.Tensor): Input image tensor of shape (batch_size, 3, H, W).

        Returns:
            np.ndarray: Model prediction output as a NumPy array.
        """
        image_tensor = image_tensor.to(self.device)
        with torch.no_grad():
            output = self.model(image_tensor)
        return output.cpu().numpy()