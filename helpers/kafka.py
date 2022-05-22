import hashlib
import json
import logging

from kafka import KafkaConsumer, KafkaProducer

# logging.basicConfig(level="INFO")


class KafkaManager:
    def __init__(self, bootstrap_servers: list, partition_number: int):
        self.bootstrap_servers = bootstrap_servers
        self.partition_number = partition_number
        self._consumers = {}

    def get_consumer(self, topic: str):
        if topic not in self._consumers:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda msg: json.loads(msg.decode("ascii")),
            )
            self._consumers[topic] = consumer
        return self._consumers[topic]

    def _get_partition_by_ips(self, packet: dict) -> int:
        src_ip = packet.get("IP", {}).get("src", "")
        dst_ip = packet.get("IP", {}).get("dst", "")
        hex_hash = hashlib.md5(f"{sorted((src_ip, dst_ip))}".encode("UTF-8")).hexdigest()
        return int(hex_hash, 16) % self.partition_number

    @staticmethod
    def _on_send_success(record_metadata):
        logging.info(
            "The message was pushed successfully to kafka:\ntopic: %s\npartition: %s\noffset: %s",
            record_metadata.topic,
            record_metadata.partition,
            record_metadata.offset,
        )

    @staticmethod
    def _on_error_callback(exception: Exception):
        logging.error("An error occurred while pushing the message to kafka:", exc_info=exception)

    def send_packet_to_kafka(self, packet: dict, topic: str):
        producer = KafkaProducer(
            api_version=(2, 5, 0),
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda msg: json.dumps(msg).encode("ascii"),
            retries=5,
        )

        partition = self._get_partition_by_ips(packet)

        producer.send(
            topic=topic,
            value=packet,
            partition=partition,
        ).add_callback(self._on_send_success).add_errback(self._on_error_callback)

        producer.flush()
        producer.close(0.01)
