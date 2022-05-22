import os
import logging

from helpers.kafka import KafkaManager
from helpers.mongo import MongoManager

logging.basicConfig(level="WARNING")

TCP_PACKETS_KAFKA_TOPIC = os.environ.get("TCP_PACKETS_KAFKA_TOPIC", "tcp_topic")
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.environ.get("MONGO_PORT", "27017"))
DATABASE = os.environ.get("DATABASE", "network_scanner")
TCP_PACKETS_COLLECTION = os.environ.get("TCP_PACKETS_COLLECTION", "tcp_packets")
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
    collection=TCP_PACKETS_COLLECTION,
    username=USERNAME,
    password=PASSWORD,
)


def update_by_flag(timestamp: int, flag: str):
    mongo_manager.upsert(
        {"timestamp": timestamp},
        {"$inc": {f"{flag}_packets_count": 1}},
    )


def main():
    consumer = kafka_manager.get_consumer(topic=TCP_PACKETS_KAFKA_TOPIC)

    ips_with_last_flag_equals_to_syn = set()

    for packet_message in consumer:
        packet = packet_message.value
        src_ip = str(packet["IP"]["src"])
        dst_ip = str(packet["IP"]["dst"])
        src_port = str(packet["TCP"]["sport"])
        dst_port = str(packet["TCP"]["dport"])
        session_identification_tuple = (src_ip, src_port, dst_ip, dst_port)
        packet_flags = str(packet["TCP"]["flags"])
        timestamp = packet["timestamp"] - packet["timestamp"] % 60

        if packet_flags.lower() == "s":
            update_by_flag(timestamp, "syn")
            ips_with_last_flag_equals_to_syn.add(session_identification_tuple)
        elif packet_flags.lower() == "a" and session_identification_tuple in ips_with_last_flag_equals_to_syn:
            update_by_flag(timestamp, "ack")
            ips_with_last_flag_equals_to_syn.remove(session_identification_tuple)
        else:
            if src_ip in ips_with_last_flag_equals_to_syn:
                ips_with_last_flag_equals_to_syn.remove(session_identification_tuple)

        logging.warning(ips_with_last_flag_equals_to_syn)


if __name__ == "__main__":
    main()
