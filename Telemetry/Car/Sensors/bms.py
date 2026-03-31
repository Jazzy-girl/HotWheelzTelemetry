import board
import digitalio
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_mcp2515
from adafruit_mcp2515.canio import Message
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class BMS(SensorBase):
    """
    An interface for BMS data that handles reading from the I2C bus.
    """
    def __init__(self, scl: board.pin.Pin, sda: board.pin.Pin, peripheral: int):
        super().__init__()
        self.message = bytearray(24)
        peripheral = 0x52
        self.i2c = busio.I2C(scl, sda)
        while not i2c.try_lock():
            pass

        devices: int = i2c.scan()
        while len(devices) < 1:
            devices = i2c.scan()
        print('Found device with address: {}'.format(hex(devices[0])))
        if devices[0] != peripheral:
            print("Located device not the Feather")
        self.device = devices[0]
        
    
        
    def update(self):
    #    while msg := self.listener.receive():
    #        if isinstance(msg, Message):
    #            start = msg.id * 8
    #            end = start + len(msg.data)
    #            self.message[start:end] = msg.data
        id1, id2, id3, = 0, 0, 0
        while (not (id1 and id2 and id3)):
            result = bytearray(12)
            self.i2c.readfrom_into(self.device, result)
            id = result[0:3]
            start = id * 8
            end = start + len(result[4:])
            self.message[start:end] = result[4:]


        

        
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet.update_from_bms(self.message)