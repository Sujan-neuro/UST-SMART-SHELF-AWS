import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#  demo consumer to consume messages from Kafka topics
from confluent_kafka import Consumer, KafkaException
from configs .config import BOOTSTRAP_SERVERS

# Kafka Configuration
conf = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': f'Retail_Media_group',
    'auto.offset.reset': 'earliest',  # Start reading from the beginning if no committed offset
    'enable.auto.commit': True,  # Automatically commit offsets
    'session.timeout.ms': 90000,
    'heartbeat.interval.ms': 15000,
}

# Create Consumer
consumer = Consumer(conf)

# List of Topics to Subscribe
topics = ['lenovo_event', 'retailmedia', 'malaysia_event', 'footprints_lab', 'nrf_singapore', 'aws_lab_default']
consumer.subscribe(topics)

print(f"Subscribed to topics: {topics}")

try:
    while True:
        msg = consumer.poll(timeout=1.0)  # Poll for new messages

        if msg is None:
            continue  # No new messages
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                print(f"Reached end of partition: {msg.topic()}-{msg.partition()}")
            else:
                print(f"Kafka error: {msg.error()}")
            continue

        # Print the received message
        print(f"Received message: {msg.value().decode('utf-8')} from topic: {msg.topic()}")

except KeyboardInterrupt:
    print("Consumer interrupted by user")

finally:
    consumer.close()  # Ensure consumer is properly closed
