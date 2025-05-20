import json
import logging
from kafka import KafkaProducer
from typing import List, Dict, Any
import os
import sys

# Adjust path to import custom configs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.config import BOOTSTRAP_SERVERS

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('kafka').setLevel(logging.WARNING)


def get_kafka_producer() -> KafkaProducer:
    """
    Creates and returns a Kafka producer instance with JSON serialization.
    Raises a concise error if Kafka brokers are unavailable.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        if isinstance(e, Exception) and 'NoBrokersAvailable' in str(e):
            logger.error("No Kafka brokers available.")
        else:
            logger.exception("Failed to create Kafka producer")  # Detailed traceback
        raise RuntimeError("Kafka connection failed") from None


def send_to_kafka(data: Dict[str, Any], topics: List[str]) -> None:
    """
    Sends JSON-serialized data to specified Kafka topics.

    Args:
        data (Dict[str, Any]): The JSON data to send.
        topics (List[str]): List of Kafka topic names.
    """
    try:
        producer = get_kafka_producer()
    except Exception:
        logger.error("Kafka producer not available. Aborting send operation.")
        return

    for topic in topics:
        try:
            producer.send(topic, value=data)
            logger.info(f"Produced data to topic: {topic}")
        except Exception:
            logger.exception(f"Failed to produce data to Kafka topic {topic}")

    try:
        producer.flush()
        logger.info("Kafka producer flushed successfully")
    except Exception:
        logger.exception("Failed to flush Kafka producer")
