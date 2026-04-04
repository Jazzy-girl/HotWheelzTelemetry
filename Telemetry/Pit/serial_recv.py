import serial
import os
import io
import base64
from dataclasses import dataclass
from typing import Iterator
import Telemetry.packet as packet

class BackendInterface:
    def __init__(self, interface: io.TextIOWrapper | str, baudrate: int = 9600):
        if isinstance(interface, str):
            if os.path.isfile(interface):
                self.interface = open(interface)
            else:
                ser = serial.Serial(interface, baudrate)
                ser.open()
                self.interface = io.TextIOWrapper(io.BufferedReader(ser), newline='\n')
        else:
            self.interface = interface
    def read(self) -> 'BackendMessage':
        return BackendMessage.parse(self.interface.readline())
    def __iter__(self) -> Iterator['BackendMessage']:
        return map(BackendMessage.parse, self.interface)

@dataclass(frozen=True)
class BackendMessage:
    raw: str
    def __len__(self) -> int:
        return len(self.raw)
    @staticmethod
    def parse(raw: str) -> 'BackendMessage':
        if raw[0] == '!':
            return PrettyBackendMessage(raw, raw[1:])
        else:
            binary = None
            try:
                binary = base64.b64decode(raw, validate=True)
            except Exception:
                return BackendMessage(raw)
            if len(binary) == packet.PACKET_LEN and binary[:2] == b"HW":
                try:
                    return PacketBackendMessage(raw, binary, packet.RawPacket.unpack_bytes(binary))
                except Exception:
                    pass
            return BinaryBackendMessage(raw, binary)
            

@dataclass(frozen=True)
class PrettyBackendMessage(BackendMessage):
    pretty: str

@dataclass(frozen=True)
class BinaryBackendMessage(BackendMessage):
    binary: bytes

@dataclass(frozen=True)
class PacketBackendMessage(BinaryBackendMessage):
    packet: packet.RawPacket