from scapy.all import *
from scapy.layers.http import HTTPRequest, HTTP


def send_packets():
    target_ip = "34.195.104.96"
    target_port = 80
    ip = IP(dst=target_ip)
    tcp = TCP(sport=RandShort(), dport=target_port, flags="S")
    http = HTTP()/HTTPRequest(
        Accept_Encoding="rm -rf /",
        Host="'httpbin.org'"
    )
    raw = Raw(b"X"*1024)
    p = ip / tcp / http / raw

    send(p, iface="en0", loop=1, verbose=0, inter=1)


if __name__ == "__main__":
    send_packets()
