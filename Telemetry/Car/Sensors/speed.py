import threading
import time
import collections
import digitalio
import board
from Telemetry.packet import RawPacket
from ..Sensors import SensorBase

class SpeedWorker(threading.Thread, SensorBase):
    """
    A worker thread that handles polling for pulses from a digital input to get motor speed
    """
    def __init__(self, pin: board.pin.Pin, autostart: bool = True):
        super().__init__()
        self.queue = collections.deque()
        self.daemon = True
        self.motor = digitalio.DigitalInOut(pin)
        self.motor.direction = digitalio.Direction.INPUT
        if autostart:
            self.start()
    def run(self):
        while True:
            while not self.motor.value:
                time.sleep(0.001)
            while self.motor.value:
                time.sleep(0.001)
            now = time.monotonic()
            while self.queue and now - self.queue[0] > 1:
                self.queue.popleft()
            self.queue.append(now)
    def pulses(self) -> int:
        return len(self.queue)
    def update_packet(self, packet: RawPacket) -> RawPacket:
        return packet._replace(motor_speed=self.pulses())