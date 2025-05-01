import cv2
import logging
from typing import List

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def list_available_cameras(max_tested: int = 5) -> List[int]:
    """
    List available camera indices by attempting to open them.

    Args:
        max_tested (int): Maximum number of camera indices to test. Defaults to 5.

    Returns:
        List[int]: List of available camera indices.

    Raises:
        RuntimeError: If no available cameras are found.
    """
    available_cameras: List[int] = []
    try:
        for index in range(max_tested):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                logger.info(f"Camera found at index: {index}")
                cap.release()
            else:
                # logger.debug(f"No camera found at index: {index}")
                pass
    except Exception as e:
        logger.error(f"Error listing cameras: {e}")
        raise

    if not available_cameras:
        logger.error(f"No available cameras found.")
        raise

    return available_cameras