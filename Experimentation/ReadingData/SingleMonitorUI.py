import time
from bitstring import BitArray
import cantools
import can
import cantools.database
import random
import tkinter as tk
from tkinter.ttk import *
import tkinter.font as tkFont
import PIL.Image, PIL.ImageTk
import sys
import math
import cantools
import can
from time import sleep
try:
    from picamera2 import Picamera2
except ImportError:
    print("Running on non-RPI system - camera not available.")
    Picamera2 = None
import serial

sys.path.append('/Users/divnamijic/Documents/HotWheelzCANbus-4/UI')
from Speedometer import Speedometer

# DBC_FILE = 'Experimentation/DBC Data/LATEST_DBC.dbc'
# SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
# BG_IMAGE = "Experimentation/ReadingData/Resources/images/bg.jpg"

DBC_FILE = '/home/pi/HotWheelz/HotWheelzCANbus/Experimentation/DBC Data/LATEST_DBC.dbc'
SIM_DATA_FILE = '/home/pi/HotWheelz/HotWheelzCANbus/Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
BG_IMAGE = "/home/pi/HotWheelz/HotWheelzCANbus/Experimentation/ReadingData/Resources/images/bg.jpg"

VALID_IDs = ['02B', '02C']

PARAMETERS = ['PackSOC', 'PackCurrent', 'PackInstVoltage', 'HighTemp', 'LowTemp', '_12vSupply']
FAULTS = ['Low Cell Voltage Fault', 'Current Sensor Fault', 'Pack Voltage Sensor Fault', 'Thermistor Fault']
DATA_LABELS = ['SOC', 'CURR', 'VOLT', '_12', 'HI', 'LO']
FAULT_LABELS = ['L. CELL', 'CURRENT', 'PACK', 'THERM']
CUSTOM_FLAG_INDICES = {
    0: 'Low Cell Voltage Fault',
    1: 'Current Sensor Fault',
    2: 'Pack Voltage Sensor Fault',
    3: 'Thermistor Fault'
}

CAMERA_RATIO = (480, 480)
ID = [43, 44]  # Message 02B, 02C
db = cantools.database.load_file(DBC_FILE)

# THIS IS TO CONNECT TO THE BMS DIRECTLY
ser = serial.Serial(
    port='COM4',
    baudrate=9600,
    timeout=1
)
ser.write(b'C\r')
ser.write(b'S6\r')
ser.write(b'O\r')
buffer = ""

def get_bms_data(buffer):
    messages = []
    i = 0
    while i < len(buffer):
        if buffer[i] != 't':
            i += 1
            continue
        if i + 5 >= len(buffer):
            break
        try:
            can_id = int(buffer[i+1:i+4], 16)
            dlc = int(buffer[i+4])
        except:
            i += 1
            continue

        msg_len = 1 + 3 + 1 + dlc * 2
        if i + msg_len > len(buffer):
            break

        msg = buffer[i:i+msg_len]
        messages.append(msg)
        i += msg_len

    return messages, buffer[i:]

def simulate_can_data():
    return {
        'arbitration_id': ID[random.randint(0, 1)],
        'data': bytearray([random.randint(0, 255) for _ in range(8)])
    }

def create_display_window():
    root = tk.Tk()
    root.title("Car Monitoring System")
    root.geometry("800x480")

    cam_frame = tk.Frame(root, background="black")
    cam_frame.pack(side=tk.LEFT, expand=True)

    video_label = Label(cam_frame, background="black")
    video_label.pack(expand=True)

    # Initialize the camera
    global camera
    camera = None
    if Picamera2:
        try:
            camera = Picamera2()
            config = camera.create_preview_configuration(main={"size": CAMERA_RATIO})
            camera.configure(config)
            camera.start()
        except Exception as e:
            print(f"Camera error: {e}")
            camera = None

    data_frame = tk.Frame(root, background="black")
    data_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    fields = {}
    faultFields = {}
    for i in range(len(DATA_LABELS)*2 + len(FAULT_LABELS)):
        data_frame.rowconfigure(i, weight=1)
    data_frame.columnconfigure(0, weight=1)
    data_frame.columnconfigure(3, weight=1)
    data_font = tkFont.Font(family="Arial", size=20)
    output_font = tkFont.Font(family="Arial", size=25)
    fault_font = tkFont.Font(family="Arial", size=20)

    Separator(data_frame, orient=tk.VERTICAL).grid(column=1, columnspan=2, row=0, rowspan=13, sticky='NS')
    Separator(data_frame, orient=tk.HORIZONTAL).grid(column=0, columnspan=4, row=2, rowspan=1, sticky='EW')
    Separator(data_frame, orient=tk.HORIZONTAL).grid(column=0, columnspan=4, row=5, rowspan=1, sticky='EW')
    Separator(data_frame, orient=tk.HORIZONTAL).grid(column=0, columnspan=4, row=8, rowspan=1, sticky='EW')
    Separator(data_frame, orient=tk.HORIZONTAL).grid(column=0, columnspan=4, row=10, rowspan=1, sticky='EW')

    for i in range(len(DATA_LABELS)):
        row = (i // 2) * 2
        if(i>1):
            row += 1
            if(i>3):
                row += 1
        # row = math.floor(((i/2) + (math.sqrt(i)/2)))
        col = (i % 2) * 3
        data_label = Label(data_frame, text=DATA_LABELS[i], font=data_font, background="black", foreground="white")
        data_label.grid(row=row, column=col, pady=(10,0))
        output_label = Label(data_frame, text="NULL", font=output_font, background="black", foreground="white")
        output_label.grid(row=row+1, column=col)
        fields[PARAMETERS[i]] = output_label

    for i in range(len(FAULT_LABELS)):
        row = ((i + len(DATA_LABELS)) // 2) * 2 + 3
        if(i>1):
            row+=1
        col = (i % 2) * 3
        fault_label = Label(data_frame, text=FAULT_LABELS[i], font=fault_font, background="black", foreground="white")
        fault_label.grid(row=row, column=col, pady=20)
        faultFields[FAULTS[i]] = fault_label

    def update_camera():
        if camera:
            try:
                frame = camera.capture_array()
                image = PIL.Image.fromarray(frame)
                image = image.resize(CAMERA_RATIO)
                img_tk = PIL.ImageTk.PhotoImage(image)
                video_label.img_tk = img_tk
                video_label.config(image=img_tk)
            except Exception as e:
                print(f"Camera frame error: {e}")
        root.after(5, update_camera)

    def update_display(buffer):
        chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        buffer += chunk
        msgs, buffer = get_bms_data(buffer)
        for msg in msgs:
            can_id = int(msg[1:4], 16)
            if(can_id not in ID):
                continue
            dlc = int(msg[4])
            data = bytes.fromhex(msg[5:5+dlc*2])
            decoded_msg = db.decode_message(can_id, data)
            try:
                # decoded_msg = db.decode_message(message['arbitration_id'], message['data'])
                for param, label in fields.items():
                    if param in decoded_msg:
                        value = decoded_msg[param]
                        label.configure(text=f"{value:.1f}")
                if 'CustomFlag' in decoded_msg:
                    bits = BitArray(decoded_msg['CustomFlag'].to_bytes()).bin
                    for index in range(0, 4):
                        label = faultFields[CUSTOM_FLAG_INDICES[index]]
                        label.config(foreground="white")
                        if bits[index] == '1':
                            label.config(foreground="red")
            except Exception as e:
                print(f"Error decoding CAN message: {e}")
        root.after(200, update_display, buffer)

    update_display(buffer)
    update_camera()
    root.mainloop()

if __name__ == "__main__":
    create_display_window()
