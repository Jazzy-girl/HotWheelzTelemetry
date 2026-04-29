import busio
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class BMS(SensorBase):
    """
    An interface for BMS data that handles reading from the I2C bus.
    """
    def __init__(self, i2c: busio.I2C, address: int):
        super().__init__()
        self.message = bytearray(25)
        self.i2c = i2c
        while not self.i2c.try_lock():
            pass
        self.address = address
    
    def update(self):
        self.i2c.readfrom_into(self.address, self.message)

    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet.update_from_bms(self.message[:24])
