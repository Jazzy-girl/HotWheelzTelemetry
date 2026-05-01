import time
import base64

import board
import busio
import digitalio
import adafruit_rfm9x

from Telemetry.Car.GUI import CarSideGUI
from Telemetry.Car.Sensors.all import *
from Telemetry.packet import RawPacket, ParsedPacket

i2c = board.I2C()
spi0 = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi1 = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

gps = GPS()
bms = BMS(i2c, 0x52)
speed = SpeedWorker(board.D12)
thermistor = CockpitThermistor(spi1, board.D24)

lora_rst = digitalio.DigitalInOut(board.D5)
lora_cs = digitalio.DigitalInOut(board.D13)
lora = adafruit_rfm9x.RFM9x(spi0, lora_cs, lora_rst, 915.0)

log_file = open(time.strftime("logs/data_%Y%m%d_%H%M%S.csv", time.localtime()), "w+")
print(file=log_file, sep=",", *(ParsedPacket._fields + ("sent",))) # write all of the field names to the file, then "sent", all comma-separated

gui: CarSideGUI = CarSideGUI()

def update_data():
    gps.update()
    bms.update()
    packet = RawPacket.new().apply(gps, bms, speed, thermistor)
    data = packet.pack_bytes(True)
    lora.send(data)
    parsed = packet.parse()
    print(file=log_file, sep=",", *(parsed + (base64.b64encode(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64
    gui.update_fields(parsed.motor_speed, parsed.bms_soc, parsed.therm_temp, parsed.bms_faults)
    gui.root.after(100, update_data)

update_data()
gui.start()