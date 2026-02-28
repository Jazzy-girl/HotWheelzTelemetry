import board
import busio
import digitalio
import time
import base64

import adafruid_rfm9x

from Telemetry.Car.Sensors.all import *
from Telemetry.packet import RawPacket, ParsedPacket

spi0 = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi1 = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

gps = GPS()
bms = BMS(spi1, board.D25)
speed = SpeedWorker(board.D12)
thermistor = CockpitThermistor(spi1, board.D24)

lora_rst = digitalio.DigitalInOut(board.D5)
lora_cs = digitalio.DigitalInOut(board.D13)
lora = adafruit_rfm9x.RFM9x(spi0, lora_cs, lora_rst, 915.0)

with open(time.strftime("logs/data_%Y%m%d_%H%M%S.csv", time.localtime()), "w+") as f: # a log name might be like "logs/data_20260204_210517.csv"
    print(file=f, sep=",", *(ParsedPacket._fields + ("sent",))) # write all of the field names to the file, then "sent", all comma-separated
    while True:
        gps.update()
        packet = RawPacket.new().apply(gps, bms, speed, thermistor)
        data = packet.pack_bytes(True)
        lora.send(data)
        print(file=f, sep=",", *(packet.parse() + (base64.b64encode(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64
