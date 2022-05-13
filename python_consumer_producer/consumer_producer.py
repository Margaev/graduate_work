import json
import os

from kafka import KafkaProducer, KafkaConsumer

from data_models.models import PacketModel

INTERFACE_TO_SNIFF = os.environ.get("INTERFACE", "en0_topic")

bootstrap_servers = ['127.0.0.1:19092', '127.0.0.1:29092', '127.0.0.1:39092']

consumer = KafkaConsumer(
    INTERFACE_TO_SNIFF,
    bootstrap_servers=bootstrap_servers,
)
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

for msg in consumer:
    packet = PacketModel.parse_raw(msg.value)
    print(json.dumps(packet.dict(), indent=4))
