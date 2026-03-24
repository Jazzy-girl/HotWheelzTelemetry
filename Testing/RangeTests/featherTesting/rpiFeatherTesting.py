
import collections
import time
import threading
import sys
import base64
import os
import serial
from time import sleep
import board
import busio
import digitalio


import adafruit_mcp2515
from adafruit_mcp2515.canio import Message, RemoteTransmissionRequest
import adafruit_mcp3xxx.mcp3008 as mcp
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)

message = bytearray(22)
cs = digitalio.DigitalInOut(board.D25)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True # necessary?

#int_pin = digitalio.DigitalInOut(board.D24)


can = adafruit_mcp2515.MCP2515(spi, cs, baudrate=125000, crystal_freq=8000000, loopback=False, silent=False)


while True:
    if not spi.try_lock():
        pass
    print("Bus state: ", can._bus_state)
    with can.listen(timeout=1.0) as listener:
        message = Message(id=0x123, data=b"adafruit", extended=False)
        send_success = can.send(message)
        print("Send success: ", send_success)
    print(can._read_register(0x0F))    
    msg = can.read_message()
    # print(can._filter)
    print(msg)
    if msg is not None:
        print(f"Message ID: {hex(msg.id)}")
        if isinstance(msg, Message):
            print("Message data: ", msg.data)

        # for _ in range(listener.in_waiting()):
        #    msg = listener.receive()
        #    print("Message from ", hex(msg.id))
        #    print(msg)
    print("TEC: ", can._read_register(0x1C))
    print("REC: ", can._read_register(0x1D))
    sleep(1)



"""
while not spi.try_lock():
   pass
    # print(spi.try_lock())

while(True):
    try:
        spi.configure(baudrate=250000,phase=0,polarity=0)
        cs.value = False
        spi.write(bytes([0x01,0xFF]))
        cs.value = True
        print("printed value!")
    finally:
        spi.unlock()
"""
