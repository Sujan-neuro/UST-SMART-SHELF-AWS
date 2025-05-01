import logging
from typing import Union

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DestandardizeAge:
    """
    Class to destandardize a standardized age value based on predefined mean and standard deviation.
    """

    def __init__(self):
        """
        Initialize mean and standard deviation for destandardization.
        """
        self.mean_age: float = 31.11096921925228
        self.std_age: float = 17.220405909006107
        logger.info("DestandardizeAge initialized with mean_age=%.4f, std_age=%.4f", self.mean_age, self.std_age)

    def destandardize_age(self, standardized_age: Union[float, int]) -> float:
        """
        Destandardize a standardized age value.

        Args:
            standardized_age (float or int): Standardized age value to be destandardized.

        Returns:
            float: Actual (destandardized) age value.
        """
        try:
            actual_age = standardized_age * self.std_age + self.mean_age
            return actual_age
        except Exception as e:
            logger.error(f"Error destandardizing age: {e}")
            return