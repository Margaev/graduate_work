import os
import logging

from helpers.kafka import KafkaManager
from helpers.mongo import MongoManager

logging.basicConfig(level="WARNING")

HTTP_PACKETS_KAFKA_TOPIC = os.environ.get("HTTP_PACKETS_KAFKA_TOPIC", "http_topic")
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
HTTP_PACKETS_COLLECTION = os.environ.get("HTTP_PACKETS_COLLECTION", "http_packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

MALICIOUS_SCRIPT = "rm -rf /"

kafka_manager = KafkaManager(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    partition_number=PARTITION_NUMBER,
)

mongo_manager = MongoManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    database=DATABASE,
    collection=HTTP_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)


def scan_headers(headers: dict) -> bool:
    logging.warning(str(headers))
    logging.warning(MALICIOUS_SCRIPT in str(headers))
    return MALICIOUS_SCRIPT in str(headers)


def update_by_ip(timestamp: int, ip: str = None):
    mongo_manager.upsert(
        {"timestamp": timestamp},
        {"$inc": {f"{ip.replace('.', '_')}": 1}} if ip is not None else {"$inc": {f"total_count": 1}},
    )


def main():
    consumer = kafka_manager.get_consumer(topic=HTTP_PACKETS_KAFKA_TOPIC)

    for packet_message in consumer:
        packet = packet_message.value
        timestamp = packet["timestamp"] - packet["timestamp"] % 60

        update_by_ip(timestamp)

        malicious_traffic_found = scan_headers(packet["HTTP Request"])
        if malicious_traffic_found:
            update_by_ip(timestamp, packet["HTTP Request"]["Host"])


if __name__ == "__main__":
    main()
