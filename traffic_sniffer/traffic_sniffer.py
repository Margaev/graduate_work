import logging
import os

from scapy.all import sniff
from scapy.layers.http import HTTPRequest
from scapy.packet import Packet

from helpers.kafka import KafkaManager

logging.basicConfig(level="WARNING")

INTERFACE_TO_SNIFF = os.environ.get("INTERFACE", "en0")
KAFKA_TOPIC = f"{INTERFACE_TO_SNIFF}_topic"
PARTITION_NUMBER = os.environ.get("PARTITION_NUMBER", 10)
BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092").split(",")

kafka_manager = KafkaManager(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    partition_number=PARTITION_NUMBER,
)


def parse_packet(raw_packet: Packet):
    packet_dict = {
        "interface": INTERFACE_TO_SNIFF,
        "timestamp": raw_packet.time,
    }
    layer = None
    sublayer = None
    for line in raw_packet.show2(dump=True).split("\n"):
        if "###" in line:
            if "|###" in line and layer is not None:
                sublayer = line.strip("|#[] ")
                packet_dict[layer][sublayer] = {}
            else:
                layer = line.strip("#[] ")
                packet_dict[layer] = {}
        elif "=" in line:
            if "|" in line and sublayer is not None:
                key, val = line.strip("| ").split("=", 1)
                packet_dict[layer][sublayer][key.strip()] = val.strip("\" ")
            else:
                key, val = line.split("=", 1)
                val = val.strip("\" ")
                packet_dict[layer][key.strip()] = val
    return packet_dict


def callback(raw_packet: Packet):
    packet = parse_packet(raw_packet)
    logging.info(packet)
    if "IP" in packet:
        if packet["IP"]["src"] == "34.195.104.96" or packet["IP"]["dst"] == "34.195.104.96":
            logging.warning(packet)
    if HTTPRequest in raw_packet:
        logging.warning(raw_packet.show2())
    #     logging.warning(packet)

    kafka_manager.send_packet_to_kafka(
        packet=packet,
        topic=KAFKA_TOPIC,
    )


def main():
    sniff(
        iface=INTERFACE_TO_SNIFF,
        prn=callback,
        store=False,
    )


if __name__ == "__main__":
    main()
