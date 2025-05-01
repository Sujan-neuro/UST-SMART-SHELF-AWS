import json
import logging
from kafka import KafkaProducer
from typing import List, Dict, Any
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.config import BOOTSTRAP_SERVERS

# Setup logger
logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger('kafka').setLevel(logging.WARNING)

# Create a producer with JSON serializer
producer = KafkaProducer(
    bootstrap_servers= BOOTSTRAP_SERVERS,
    # api_version = (2, 8, 0),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


def send_to_kafka(data: Dict[str, Any], topics_list: List[str]) -> None:
    """
    Sends JSON-serialized data to specified Kafka topics.

    Args:
        data (Dict[str, Any]): The JSON data to send.
        topics_list (List[str]): List of topic names to send the data to.
    """
    for topic in topics_list:
        try:
            producer.send(topic, value=data)
            logger.info(f"Produced data to topic: {topic}")
        except Exception:
            # Logs the full stack trace for this specific topic
            logger.exception(f"Failed to produce data to Kafka topic {topic}")
    try:
        producer.flush()
    except Exception:
        logger.exception("Failed to flush Kafka producer")