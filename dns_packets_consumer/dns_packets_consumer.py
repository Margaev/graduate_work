import os
import logging

from helpers.kafka import KafkaManager
from helpers.mongo import MongoManager

logging.basicConfig(level="WARNING")

DNS_PACKETS_KAFKA_TOPIC = os.environ.get("DNS_PACKETS_KAFKA_TOPIC", "dns_topic")
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
DNS_PACKETS_COLLECTION = os.environ.get("DNS_PACKETS_COLLECTION", "dns_packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

AVERAGE_MAXIMUM_URL_LENGTH = 217
AVERAGE_MINIMUM_URL_LENGTH = 47

kafka_manager = KafkaManager(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    partition_number=PARTITION_NUMBER,
)

mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=DNS_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)


def update_by_size(timestamp: int, size: str = None):
    mongo_manager.upsert(
        {"timestamp": timestamp},
        {"$inc": {f"{size}_packets_count": 1}} if size is not None else {"$inc": {f"packets_count": 1}},
    )


def main():
    consumer = kafka_manager.get_consumer(topic=DNS_PACKETS_KAFKA_TOPIC)

    for packet_message in consumer:
        packet = packet_message.value
        timestamp = packet["timestamp"] - packet["timestamp"] % 60

        logging.warning(packet)
        if "DNS Question Record" in packet["DNS"]:
            update_by_size(timestamp)

            dns_question_len = len(str(packet["DNS"]["DNS Question Record"]))
            if dns_question_len > AVERAGE_MAXIMUM_URL_LENGTH:
                update_by_size(timestamp, "huge")
            elif dns_question_len < AVERAGE_MINIMUM_URL_LENGTH:
                update_by_size(timestamp, "small")


if __name__ == "__main__":
    main()
