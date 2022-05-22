import os
import logging

from helpers.kafka import KafkaManager
from helpers.mongo import MongoManager

logging.basicConfig(level="WARNING")

IP_PACKETS_KAFKA_TOPIC = os.environ.get("IP_PACKETS_KAFKA_TOPIC", "ip_topic")
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
IP_PACKETS_COLLECTION = os.environ.get("IP_PACKETS_COLLECTION", "ip_packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

kafka_manager = KafkaManager(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    partition_number=PARTITION_NUMBER,
)

mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=IP_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)


def main():
    consumer = kafka_manager.get_consumer(topic=IP_PACKETS_KAFKA_TOPIC)
    for packet_message in consumer:
        packet = packet_message.value
        # increment packets count for packet arrival minute
        mongo_manager.upsert(
            {"timestamp": packet["timestamp"] - packet["timestamp"] % 60},
            {"$inc": {"packets_count": 1}},
        )


if __name__ == "__main__":
    main()
