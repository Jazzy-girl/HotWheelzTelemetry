
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


def update_data():
    print("update called")
    message = serial.PacketBackendMessage.from_packet(random_packet()) if do_debug else interface.read()
    print(f"msg received: {message}")
    if isinstance(message, serial.PacketBackendMessage):
        packet = message.packet
        parsed = packet.parse()
        data = packet.pack_bytes(True)
        print(file=log_file, sep=",", *(parsed + (base64.b64encode(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64
        gui.addParsedPacket(parsed)
        print("packet received!")
    gui.root.after(500, update_data)

# thd = threading.Thread(daemon=True, target=update_data)

# thd.start()
update_data()
gui.start()
