import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class CockpitThermistor(SensorBase):
    def __init__(self, spi: busio.SPI, cs: board.pin.Pin):
        self.adc_cs = digitalio.DigitalInOut(board.D24)
        self.adc = mcp.MCP3008(spi, self.adc_cs)
        self.thermistor = AnalogIn(self.adc, mcp.P0)
    def reading(self) -> int:
        return self.thermistor.value
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet._replace(temp=self.reading())
