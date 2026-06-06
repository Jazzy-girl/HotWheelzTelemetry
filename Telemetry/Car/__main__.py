import time
import base64

from Telemetry.Car.GUI import CarSideGUI
from Telemetry.packet import ParsedPacket
import Telemetry.serial_recv as serial

log_file = open(time.strftime("logs/data_%Y%m%d_%H%M%S.csv", time.localtime()), "w+")
print(file=log_file, sep=",", *(ParsedPacket._fields + ("sent",))) # write all of the field names to the file, then "sent", all comma-separated

gui: CarSideGUI = CarSideGUI()
usb_filepath = "/dev/ttyACM0"
interface: serial.BackendInterface = serial.BackendInterface(usb_filepath)

def update_data():
    message = interface.read()
    if isinstance(message, serial.PacketBackendMessage):
        packet = message.packet
        parsed = packet.parse()
        data = packet.pack_bytes(True)
        print(file=log_file, sep=",", *(parsed + (base64.b64encode(data).decode('ascii'),))) # write all of the tuple fields to the file, then the packet itself, encoded as base64
        gui.update_fields(parsed.motor_speed, parsed.bms_soc, parsed.therm_temp, parsed.bms_faults)
    gui.root.after(100, update_data)

update_data()
gui.start()