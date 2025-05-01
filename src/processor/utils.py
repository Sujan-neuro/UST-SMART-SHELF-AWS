import os
import sys
import logging
import datetime
from typing import Dict, Any
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from configs.config import (LOCATION_ID,
                            STORE_LOCATION
                            )

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cosine_distance(vec1: list, vec2: list) -> float:
    """
    Calculate the cosine distance between two vectors.

    Parameters:
        vec1 (list): The first vector.
        vec2 (list): The second vector.

    Returns:
        float: Cosine distance between vec1 and vec2, calculated as 1 - cosine_similarity.
    """
    try:
        # logging.info('Calculating cosine distance')
        return 1 - cosine_similarity([vec1], [vec2])[0][0]
    except Exception as e:
        logging.error(f'Error in cosine_distance function: {e}')
        raise


class LimitedDict(OrderedDict):
    """
    A dictionary with a limited size, removing the oldest item when the max size is exceeded.
    """
    def __init__(self, max_size: int = 500, *args, **kwargs):
        """
        Initialize the LimitedDict with a specified maximum size.

        Parameters:
            max_size (int): Maximum size of the dictionary before removing the oldest item.
        """
        try:
            logging.info(f'Initializing LimitedDict with max size {max_size}')
            self.max_size = max_size
            super().__init__(*args, **kwargs)
        except Exception as e:
            logging.error(f'Error in LimitedDict initialization: {e}')
            raise

    def __setitem__(self, key: str, value: any) -> None:
        """
        Override the __setitem__ method to ensure the dictionary size does not exceed max_size.

        Parameters:
            key (str): The key for the item.
            value (any): The value to be associated with the key.
        """
        try:
            if len(self) >= self.max_size:
                # logging.info('Maximum size reached, removing the oldest item.')
                self.popitem(last=False)  # Remove the oldest item (FIFO)
            super().__setitem__(key, value)
        except Exception as e:
            logging.error(f'Error in __setitem__ method of LimitedDict: {e}')
            raise


class DailyIndex:
    """
    A class to generate a daily index, resetting at the start of each new day.
    """
    def __init__(self):
        """
        Initialize DailyIndex with the current date and set the initial index to 0.
        """
        try:
            logging.info('Initializing DailyIndex')
            self.previous_date = datetime.date.today()
            self.index = 0  # Start index
        except Exception as e:
            logging.error(f'Error initializing DailyIndex: {e}')
            raise

    def get_index(self) -> int:
        """
        Get the daily index. Resets at the start of each new day.

        Returns:
            int: The current index for the day, starting from 1 each new day.
        """
        try:
            current_date = datetime.date.today()
            if self.previous_date != current_date:
                logging.info('New day detected, resetting index to 1.')
                self.index = 1
                self.previous_date = current_date
            else:
                self.index += 1
            return self.index
        except Exception as e:
            logging.error(f'Error in get_index method of DailyIndex: {e}')
            raise


def craft_payload(inp_id: str, inp_age: int, inp_gender: str, inp_today: datetime) -> Dict[str, Any]:
    """
    Build the visitor payload for downstream processing or API calls.

    Args:
        inp_id (str):          Unique visitor identifier.
        inp_age (int):         Visitor's age in years.
        inp_gender (str):      Visitor's gender label.
        inp_today (datetime):  Timestamp of the visit.

    Returns:
        Dict[str, Any]: A serializable payload containing
            visitor info, timestamp, and default metadata fields.
            If an error occurs, returns an empty dict.
    """
    try:
        payload: Dict[str, Any] = {
            "visitorId": inp_id,
            "age": inp_age,
            "gender": inp_gender,
            "locationId": LOCATION_ID,
            "visitDate": inp_today.strftime("%Y-%m-%d"),
            "visitTime": inp_today.strftime("%H:%M:%S"),
            "mood": "",
            "bodyType": "",
            "race": "",
            "primaryClothingColor": "",
            "secondaryClothingColor": "",
            "inStoreCoordinates": STORE_LOCATION,
            "eyesFocus": "",
            "type": "store"
        }
        # logger.debug(f"Crafted payload for visitor {inp_id}: {payload}")
        return payload

    except Exception:
        # Logs full traceback so you know exactly what went wrong
        logger.exception(
            f"Failed to craft payload for id={inp_id}, age={inp_age}, "
            f"gender={inp_gender}, date={inp_today.isoformat()}"
        )
        raise