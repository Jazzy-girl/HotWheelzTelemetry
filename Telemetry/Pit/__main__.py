
import time
import base64
import os
from random import randint
import threading


# from Telemetry.Car.GUI import CarSideGUI
from Telemetry.Pit.Dashboard import Dashboard
from Telemetry.packet import ParsedPacket, RawPacket, FaultSet
import Telemetry.serial_recv as serial

log_dir = "logs"
# makes the log dir if it doesnt already exist
os.makedirs(log_dir, exist_ok=True)

log_file = open(time.strftime("logs/data_%Y%m%d_%H%M%S.csv", time.localtime()), "w+")
print(file=log_file, sep=",", *(ParsedPacket._fields + ("sent",))) # write all of the field names to the file, then "sent", all comma-separated

gui: Dashboard = Dashboard()
usb_filepath = "COM8"

do_debug = False
interface: serial.BackendInterface
if not do_debug:
    interface = serial.BackendInterface(usb_filepath)
# debug testing
print(f"debug is {do_debug}")


def random_packet():

    randPacket = RawPacket(randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),FaultSet(0),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100),randint(1,100))
    return randPacket

# ex1 = "SFcYaiytCAAAAAAAAAAAAd4BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
# ex2 = "SFy6Gl"
# ex3 = "SFcsi0"
# ex4 = "SF"
# ex5 = "SFcWax"
# msg = serial.BackendMessage.parse(ex1)
# if isinstance(msg, serial.PacketBackendMessage):
#     print(msg.packet.parse().therm_temp)
# print(serial.BackendMessage.parse(ex1))
# print(serial.BackendMessage.parse(ex2))
# print(serial.BackendMessage.parse(ex3))
# print(serial.BackendMessage.parse(ex4))
# print(serial.BackendMessage.parse(ex5))

PACKET: int = 0
BINARY = 0
BACK = 0

def update_data():
    global PACKET, BINARY, BACK
    print("update called")
    message = serial.PacketBackendMessage.from_packet(random_packet()) if do_debug else interface.read()
    print(f"msg received: {message}")
    if isinstance(message, serial.PacketBackendMessage):
        PACKET += 1
        packet = message.packet
        parsed = packet.parse()
        data = packet.pack_bytes(True)
        print(file=log_file, sep=",", *(parsed + (base64.b64encode(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64
        gui.addParsedPacket(parsed)
        print("packet received!")
        print(f"temp: {parsed.therm_temp}")
    elif isinstance(message, serial.BinaryBackendMessage):
        BINARY += 1
    else:
        BACK += 1
    total = BINARY + BACK + PACKET
    ratio = PACKET / total
    print(f"num packet: {PACKET} vs total: {total}")
    gui.root.after(500, update_data)

# thd = threading.Thread(daemon=True, target=update_data)

# thd.start()
update_data()
gui.start()
