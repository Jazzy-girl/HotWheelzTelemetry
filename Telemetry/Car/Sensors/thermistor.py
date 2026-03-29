import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as mcp
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class CockpitThermistor(SensorBase):
    def __init__(self, spi: busio.SPI, cs: board.pin.Pin):
        self.adc_cs = digitalio.DigitalInOut(cs)
        self.adc = mcp.MCP3008(spi, self.adc_cs)
    def reading(self) -> int:
        return self.adc.read(0)
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet._replace(temp=self.reading())
