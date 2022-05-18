import logging

from abc import ABC
from typing import Optional

from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet
from scapy.layers.dns import DNS


class BaseProtocolParser(ABC):
    protocols = []

    def _parse_packet_data(self, pkt: Packet, protocol: Packet) -> dict:
        raise NotImplemented

    def _get_protocol(self, pkt: Packet) -> Optional[Packet]:
        if len(self.protocols) == 0:
            logging.info("No protocols were stated in cls.protocols property...")
        for protocol in self.protocols:
            if protocol in pkt:
                return protocol
        return None

    def parse(self, pkt: Packet) -> dict:
        protocol = self._get_protocol(pkt)
        return self._parse_packet_data(pkt, protocol)


class NetworkingProtocolParser(BaseProtocolParser):
    protocols = [IP, IPv6]

    def _parse_packet_data(self, pkt: Packet, protocol: Packet):
        protocol_data = dict()

        if protocol is not None:
            protocol_data.update(
                {
                    "networking_protocol": protocol.__name__,
                    "src_ip": pkt[protocol].src,
                    "dst_ip": pkt[protocol].dst,
                }
            )
        return protocol_data


class TransportProtocolParser(BaseProtocolParser):
    protocols = [TCP, UDP]

    def _parse_packet_data(self, pkt: Packet, protocol: Packet):
        protocol_data = dict()
        if protocol is not None:
            protocol_data.update(
                {
                    "transport_protocol": protocol.__name__,
                    "src_port": pkt[protocol].sport,
                    "dst_port": pkt[protocol].dport,
                    "timestamp": pkt[protocol].time,
                }
            )
            if protocol == TCP:
                protocol_data.update(
                    {
                        "seq": pkt[protocol].seq,
                        "ack": pkt[protocol].ack,
                    }
                )
        return protocol_data


class ApplicationProtocolParser(BaseProtocolParser):
    protocols = [DNS]

    def _parse_packet_data(self, pkt: Packet, protocol: Packet):
        protocol_data = dict()
        if protocol is not None:
            protocol_data.update(
                {
                    "application_protocol": protocol.__name__
                }
            )
        return protocol_data
