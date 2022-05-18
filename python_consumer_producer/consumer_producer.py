import json
import os
import logging

from kafka import KafkaProducer, KafkaConsumer

from data_models.models import PacketModel
from helpers.mongo import MongoPacketFacade

logging.basicConfig(level="INFO")

INTERFACE_TO_SNIFF = os.environ.get("INTERFACE", "en0_topic")

bootstrap_servers = ['127.0.0.1:19092', '127.0.0.1:29092', '127.0.0.1:39092']

DATABASE = os.environ.get("DATABASE", "network_scanner")
COLLECTION = os.environ.get("DATABASE", "packets")
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")

consumer = KafkaConsumer(
    INTERFACE_TO_SNIFF,
    bootstrap_servers=bootstrap_servers,
)
# producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


if __name__ == '__main__':
    for msg in consumer:
        packet = PacketModel.parse_raw(msg.value)
        mongo_facade = MongoPacketFacade(
            database=DATABASE,
            collection=COLLECTION,
            username=USERNAME,
            password=PASSWORD,
        )
        mongo_facade.insert(packet)
