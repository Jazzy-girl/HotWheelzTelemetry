import collections
import time
import threading
import sys
import base64
import os

import board
import busio
import digitalio

import adafruit_rfm9x
import adafruit_gps
import adafruit_mcp2515
from adafruit_mcp2515.canio import Message
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn

sys.path.append(os.path.join(os.path.split(__file__)[0], "..", "Pit"))
import packet

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
spi0 = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi1 = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

adc_cs = digitalio.DigitalInOut(board.D24)

gps = adafruit_gps.GPS(uart, debug=False)
adc = mcp.MCP3008(spi1, adc_cs)

thermistor = AnalogIn(adc, mcp.P0)

gps.send_command(b"PMTK314,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0") # magic data goes brrrr
gps.send_command(b"PMTK220,500")

class SpeedWorker(threading.Thread):
    """
    A worker thread that handles polling for pulses from a digital input to get motor speed
    """
    def __init__(self):
        self.queue = collections.deque()
        self.daemon = True
        self.motor = digitalio.DigitalInOut(board.D12)
        self.motor.direction = digitalio.Direction.INPUT
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

class SenderWorker(threading.Thread):
    """
    A worker thread that handles sending messages over LoRa
    """
    def __init__(self):
        self.daemon = True
        self.to_send = None
        self.lora_rst = digitalio.DigitalInOut(board.D5)
        # self.lora_int = digitalio.DigitalInOut(board.D6)
        self.lora_cs = digitalio.DigitalInOut(board.D13)
        FREQUENCY = 915
        self.lora = adafruit_rfm9x.RFM9x(spi0, self.lora_cs, self.lora_rst, FREQUENCY)
        self.start()
    def run(self):
        while True:
            if self.to_send is None:
                time.sleep(0.001)
            else:
                data= self.to_send
                self.to_send = None # there's theoretically a race condition here where we lose a message as we're sending it but I don't care
                self.lora.send(data)

class CanBusWorker(threading.Thread):
    """
    A worker thread that handles polling the CAN bus
    """
    def __init__(self):
        self.daemon = True
        self.message = bytearray(13)
        self.can_cs = digitalio.DigitalInOut(board.D25)
        self.can = adafruit_mcp2515.MCP2515(spi1, self.can_cs, loopback=False, silent=False)
        self.start()
    def run(self):
        with self.can.listen() as listener:
            while True:
                msg = self.can.receive()
                if isinstance(msg, Message):
                    self.message = msg.data

speed = SpeedWorker()
sender = SenderWorker()
canbus = CanBusWorker()

with open(time.strftime("logs/data_%Y%m%d_%H%M%S.csv", time.localtime()), "w+") as f: # a log name might be like "logs/data_20260204_210517.csv"
    print(file=f, sep=",", *(packet.ParsedPacket._fields + ("sent",))) # write all of the field names to the file, then "sent", all comma-separated
    while True:
        gps.update()
        timestamp = time.monotonic_ns() // 1000
        lon = gps.longitude if gps.has_fix else 0
        lat = gps.latitude if gps.has_fix else 0
        temp = thermistor.value
        gps_speed = gps.speed_kmh if gps.has_fix and gps.speed_kmh is not None else 0
        motor_speed = speed.pulses()
        pack = packet.RawPacket.without_bms(timestamp, lon, lat, temp, gps_speed, motor_speed)
        pack = pack.update_from_bms(canbus.message)
        data = pack.pack_bytes(True)
        sender.to_send = data
        parsed = pack.parse()
        print(file=f, sep=",", *(parsed + (base64.encodebytes(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64