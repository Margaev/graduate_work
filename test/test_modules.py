from unittest.mock import MagicMock, patch, call

import pytest

from helpers.kafka import KafkaManager
from raw_packets_consumer.raw_packets_consumer import send_for_transformation_to_kafka
from traffic_sniffer.traffic_sniffer import parse_packet

NUM_OF_PARTITIONS = 10


@pytest.mark.parametrize(
    ("packet1", "packet2", "expected_same_partition"),
    (
        (
            {"IP": {"src": "192.168.0.1", "dst": "192.168.0.2"}},
            {"IP": {"src": "192.168.0.1", "dst": "192.168.0.2"}},
            True,
        ),
        (
            {"IP": {"src": "192.168.0.1", "dst": "192.168.0.2"}},
            {"IP": {"src": "192.168.0.2", "dst": "192.168.0.1"}},
            True,
        ),
        (
            {"IP": {"src": "192.168.0.1", "dst": "192.168.0.3"}},
            {"IP": {"src": "192.168.0.2", "dst": "192.168.0.1"}},
            False,
        ),
    )
)
def test_partitioning(packet1, packet2, expected_same_partition):
    kafka_manager = KafkaManager([], NUM_OF_PARTITIONS)
    partition1 = kafka_manager._get_partition_by_ips(packet1)
    partition2 = kafka_manager._get_partition_by_ips(packet2)
    is_partition_equal = partition1 == partition2
    assert is_partition_equal is expected_same_partition


@pytest.mark.parametrize(
    ("packet", "topics"),
    (
        ({"IP": {}}, ("ip_topic", )),
        ({"TCP": {}}, ("tcp_topic", )),
        ({"DNS": {}}, ("dns_topic", )),
        ({"HTTP Request": {}}, ("http_topic", )),
        ({"IP": {}, "TCP": {}}, ("ip_topic", "tcp_topic")),
    )
)
def test_packets_distribution(packet, topics):
    with patch('raw_packets_consumer.raw_packets_consumer.KafkaManager.send_packet_to_kafka') as mock:
        send_for_transformation_to_kafka(packet)

        calls = []
        for topic in topics:
            args = {"packet": packet, "topic": topic}
            calls.append(call(**args))

        mock.assert_has_calls(calls)


PACKET_STR = """
###[ IP ]### 
     src       = 192.168.0.1
     dst       = 192.168.0.2
###[ TCP ]### 
        sport     = 49684
        dport     = https
"""
PACKET = MagicMock()
PACKET.show2 = MagicMock()
PACKET.show2.return_value = PACKET_STR


@pytest.mark.parametrize(
    ("raw_packet", "expected_packet_data"),
    (
        (PACKET, {"IP": {"src": "192.168.0.1", "dst": "192.168.0.2"}, "TCP": {"sport": "49684", "dport": "https"}}),
    )
)
def test_packet_parsing(raw_packet, expected_packet_data):
    actual_packet_data = parse_packet(raw_packet)
    actual_packet_data.pop("interface")
    actual_packet_data.pop("timestamp")
    assert actual_packet_data == expected_packet_data
