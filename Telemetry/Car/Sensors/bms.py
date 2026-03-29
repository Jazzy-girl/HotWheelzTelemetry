import board
import digitalio
import busio
import adafruit_mcp2515
from adafruit_mcp2515.canio import Message
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class BMS(SensorBase):
    """
    An interface for BMS data that handles reading from CAN
    """
    def __init__(self, spi: busio.SPI, cs: board.pin.Pin):
        super().__init__()
        self.message = bytearray(22)
        self.can_cs = digitalio.DigitalInOut(cs)
        self.can = adafruit_mcp2515.MCP2515(spi, self.can_cs, loopback=False, silent=False)
        self.listener = self.can.listen()
    def update(self):
        while msg := self.listener.receive():
            if isinstance(msg, Message):
                start = msg.id * 8
                end = start + len(msg.data)
                self.message[start:end] = msg.data
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet.update_from_bms(self.message)