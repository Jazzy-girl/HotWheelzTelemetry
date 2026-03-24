import serial
import adafruit_gps
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class GPS(SensorBase):
    def __init__(self, port: str = "/dev/ttyS0", baudrate: int = 9600, timeout: int = 3000):
        self.uart = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.gps.send_command(b"PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # magic data from the tutorial
        self.gps.send_command(b"PMTK220,500")
    def update(self):
        self.gps.update()
    def update_packet(self, packet: RawPacket) -> RawPacket:
        if self.gps.has_fix:
            speed = 0 if self.gps.speed_kmh is None else self.gps.speed_kmh
            packet = packet._replace(gps_lon=self.gps.longitude, gps_late=self.gps.latitude, gps_speed=speed)
        return packet
