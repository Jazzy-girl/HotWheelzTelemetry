import collections
import time
import threading
import sys
import base64
import os
import serial

import board
import busio
import digitalio


import adafruit_mcp2515
from adafruit_mcp2515.canio import Message
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

message = bytearray(22)
cs = digitalio.DigitalInOut(board.D25)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True # necessary?
can = adafruit_mcp2515.MCP2515(spi, cs, loopback=False, silent=False)

while not spi.try_lock():
    pass

    try:
        spi.configure(buardrate=5000000,phase=0,polarity=0)
        cs.value = False
        spi.write(bytes([0x01,0xFF]))
        cs.value = True
    finally:
        spi.unlock()