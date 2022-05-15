import hashlib
import logging
import os

from scapy.all import sniff
from scapy.packet import Packet
from kafka import KafkaProducer

from helpers.packet_parser import NetworkingProtocolParser, TransportProtocolParser, ApplicationProtocolParser
from data_models.models import PacketModel

logging.basicConfig(level="INFO")

INTERFACE_TO_SNIFF = os.environ.get("INTERFACE", "en0")
KAFKA_TOPIC = f"{INTERFACE_TO_SNIFF}_topic"
PARTITIONS_NUMBER = os.environ.get("PARTITIONS_NUMBER", 10)

bootstrap_servers = ['127.0.0.1:19092', '127.0.0.1:29092', '127.0.0.1:39092']


def parse_packet(raw_packet: Packet) -> PacketModel:
    flags = raw_packet.sprintf("%TCP.flags%")
    packet_data = {
        "interface": INTERFACE_TO_SNIFF,
        "flags": flags,
    }
    try:
        for ProtocolParser in [NetworkingProtocolParser, TransportProtocolParser, ApplicationProtocolParser]:
            packet_data.update(ProtocolParser().parse(raw_packet))
    except IndexError as error:
        logging.warning(
            "Error getting packet field:\n%s\npacket data:\n%s",
            error,
            raw_packet.show(),
        )
    return PacketModel(**packet_data)


def get_partition_by_ips(src_ip: str, dst_ip: str) -> int:
    hex_hash = hashlib.md5(f"{src_ip}-{dst_ip}".encode("UTF-8")).hexdigest()
    return int(hex_hash, 16) % PARTITIONS_NUMBER


def on_send_success(record_metadata):
    logging.info(
        "The message was pushed successfully to kafka:\ntopic: %s\npartition: %s\noffset: %s",
        record_metadata.topic,
        record_metadata.partition,
        record_metadata.offset,
    )


def on_error_callback(exception):
    logging.error("An error occurred while pushing the message to kafka:", exc_info=exception)


def send_packet_to_kafka(packet: PacketModel):
    producer = KafkaProducer(
        api_version=(2, 5, 0),
        bootstrap_servers=bootstrap_servers,
    )
    message = bytes(packet.json(), encoding='utf-8')
    partition = get_partition_by_ips(src_ip=packet.src_ip, dst_ip=packet.dst_ip)
    producer.send(
        topic=KAFKA_TOPIC,
        value=message,
        partition=partition,
    ).add_callback(on_send_success).add_errback(on_error_callback)
    producer.flush()
    producer.close(2)


def callback(raw_packet: Packet):
    packet = parse_packet(raw_packet)
    logging.info(packet)
    send_packet_to_kafka(packet)


if __name__ == '__main__':
    sniff(
        iface=INTERFACE_TO_SNIFF,
        store=False,
        prn=callback,
        count=1000,
    )
