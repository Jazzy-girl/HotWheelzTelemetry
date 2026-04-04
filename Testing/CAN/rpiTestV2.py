from time import sleep
import board
import busio
import digitalio


import adafruit_mcp2515
from adafruit_mcp2515.canio import Message, RemoteTransmissionRequest

cs = digitalio.DigitalInOut(board.D25)
#spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

loopback = True
send = True

can = adafruit_mcp2515.MCP2515(spi, cs, crystal_freq=8000000, baudrate=250000, loopback=loopback, silent=loopback)

while True:
    if can.transmit_error_count > 0 or can.receive_error_count > 0:
        print(f"Errors: tx={can.transmit_error_count}, rx={can.receive_error_count}")
    print("state:", can.state)
    if send:
        message = Message(id=0x5, data=b"adafruit", extended=False)
        send_success = can.send(message)
        print("Send success:", send_success)
    with can.listen(timeout=1.0) as listener:
        message_count = listener.in_waiting()
        print(message_count, "messages available")
        for _i in range(message_count):
            msg = listener.receive()
            print("Message from ", hex(msg.id))
            if isinstance(msg, Message):
                print("message data:", msg.data)
            if isinstance(msg, RemoteTransmissionRequest):
                print("RTR length:", msg.length)
    sleep(1)
