from pydantic import BaseModel


class PacketModel(BaseModel):
    interface: str
    networking_protocol: str = None
    src_ip: str = None
    dst_ip: str = None
    transport_protocol: str = None
    src_port: int = None
    dst_port: int = None
    timestamp: int = None
    seq: str = None
    ack: str = None
    application_protocol: str = None
