import json
import logging
from typing import Set

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class FootfallCounter:
    """
    Counts unique visitors based on visitorId from a JSON lines file.
    
    Attributes:
        file_path (str): Path to the input file containing visitor data.
    """

    def __init__(self, file_path: str):
        """
        Initialize the FootfallCounter.
        
        Args:
            file_path (str): Path to the JSONL file.
        """
        self.file_path = file_path

    def count_unique_visitors(self) -> int:
        """
        Counts the number of unique visitors.

        Returns:
            int: Total number of unique visitor IDs.
        """
        unique_visitors: Set[str] = set()
        
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    try:
                        data = json.loads(line.strip())
                        unique_visitors.add(data["visitorId"])
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON format in line: {line.strip()} | Error: {e}")
                    except KeyError:
                        logger.error(f"'visitorId' not found in line: {line.strip()}")
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
        except Exception as e:
            logger.error(f"Error reading file {self.file_path}: {e}")

        logger.info(f"Total unique visitors counted: {len(unique_visitors)}")
        return len(unique_visitors)
