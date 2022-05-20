import os
import logging

from helpers.kafka import KafkaManager
from helpers.mongo import MongoManager

logging.basicConfig(level="INFO")

RAW_PACKETS_KAFKA_TOPIC = os.environ.get("RAW_PACKETS_KAFKA_TOPIC", "en0_topic")
IP_PACKETS_KAFKA_TOPIC = os.environ.get("IP_PACKETS_KAFKA_TOPIC", "ip_topic")
TCP_PACKETS_KAFKA_TOPIC = os.environ.get("TCP_PACKETS_KAFKA_TOPIC", "tcp_topic")
DNS_PACKETS_KAFKA_TOPIC = os.environ.get("DNS_PACKETS_KAFKA_TOPIC", "dns_topic")
HTTP_PACKETS_KAFKA_TOPIC = os.environ.get("HTTP_PACKETS_KAFKA_TOPIC", "http_topic")
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

PROTOCOL_TOPIC_MAPPING = {
    "IP": IP_PACKETS_KAFKA_TOPIC,
    "TCP": TCP_PACKETS_KAFKA_TOPIC,
    "DNS": DNS_PACKETS_KAFKA_TOPIC,
    "HTTP Request": HTTP_PACKETS_KAFKA_TOPIC,
}

MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
RAW_PACKETS_COLLECTION = os.environ.get("DATABASE", "raw_packets")
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
    collection=RAW_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)


def send_for_transformation_to_kafka(packet: dict):
    logging.info(type(packet))
    logging.info(packet)
    for protocol, topic in PROTOCOL_TOPIC_MAPPING.items():
        if protocol in packet:
            kafka_manager.send_packet_to_kafka(
                packet=packet,
                topic=topic,
            )


def main():
    consumer = kafka_manager.get_consumer(topic=RAW_PACKETS_KAFKA_TOPIC)
    for packet_message in consumer:
        packet = packet_message.value
        send_for_transformation_to_kafka(packet)
        mongo_manager.insert(packet)


if __name__ == '__main__':
    main()
