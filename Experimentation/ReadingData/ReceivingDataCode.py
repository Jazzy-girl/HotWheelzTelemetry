import time
from bitstring import BitArray
import cantools
import random
import tkinter as tk
from tkinter import ttk
import PIL.Image, PIL.ImageTk  # For displaying images in Tkinter
import sys

import cv2
sys.path.append('/Users/divnamijic/Documents/HotWheelzCANbus-4/UI')
from Speedometer import Speedometer

# Load the CAN database
#DBC_FILE = '/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/DBC Data/LATEST_DBC.dbc'
#SIM_DATA_FILE = '/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'
#BG_IMAGE = "/Users/divnamijic/Documents/HotWheelzCANbus-4/Experimentation/ReadingData/Resources/images/bg.jpg"
DBC_FILE = 'Experimentation/DBC Data/LATEST_DBC.dbc'
SIM_DATA_FILE = 'Experimentation/ReadingData/TestData/CANData1/LATEST_DATA.txt'

BG_IMAGE = 'Experimentation/ReadingData/Resources/images/bg.jpg'
VALID_IDs = ['02B', '02C']

ID = 43  # Message 02B
db = cantools.database.load_file(DBC_FILE)

# Simulate CANbus messages (for testing)
def simulate_can_data():
    return {
        'arbitration_id': ID,
        'data': bytearray([random.randint(0, 255) for _ in range(8)])  # Simulated 8-byte CAN message
    }

# Create the main Tkinter window
def create_display_window():
    # the window
    root = tk.Tk()
    root.title("Car Monitoring System")
    root.geometry("800x480")  # Set the window size

    # # Load the background image
    # bg_image = PIL.Image.open(BG_IMAGE)
    # bg_image = bg_image.resize((800, 480))  # Resize to window size
    # bg_image_tk = PIL.ImageTk.PhotoImage(bg_image)

    # # Create a label to hold the background image and ensure it persists
    # bg_label = tk.Label(root, image=bg_image_tk)
    # bg_label.image = bg_image_tk  # Keep a reference to the image
    # bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Ensure it takes up the whole screen

    # # Create an instance of the Speedometer class
    # speedometer = Speedometer(root, width=800, height=480)
    # speedometer.update_speed()  # Example to animate

    # Backup Camera Display
    # the frame to hold the camera
    cam_frame = ttk.Frame(root)
    cam_frame.pack(pady=20)

    # the label to hold 
    cam_label = ttk.Label(cam_frame, text="Backup Camera", font=("Arial", 16))
    cam_label.pack()

    video_label = tk.Label(cam_frame)
    video_label.pack()

    # Define parameters to display (now aligned with the actual DBC signal names)
    parameters = ['PackSOC', 'PackCurrent', 'PackInstVoltage', 'HighTemp', 'LowTemp', '_12vSupply']
    fields = {}

    # Define faults and indices of faults in the Custom Flag
    faults = {'Low Cell Voltage Fault', 'Current Sensor Fault', 'Pack Voltage Sensor Fault', 'Thermistor Fault'}
    faultFields = {}
    customFlagIndices = {
        0: 'Low Cell Voltage Fault',
        1: 'Current Sensor Fault',
        2: 'Pack Voltage Sensor Fault',
        3: 'Thermistor Fault'
    }

    # Create UI elements for BMS data
    for param in parameters:
        frame = ttk.Frame(root)
        frame.place(y=60 + (parameters.index(param) * 40), relwidth=1)

        label = ttk.Label(frame, text=f"{param}:", font=("Arial", 14))
        label.pack(side="left", padx=5)

        data_label = ttk.Label(frame, text="0", font=("Arial", 14), width=15, anchor="e")
        data_label.pack(side="right", padx=5)

        fields[param] = data_label  # Store Label widget

    # Create Custom Flag Fields
    for fault in faults:
        frame = ttk.Frame(root)
        frame.place(y=60 + (len(parameters) * 40) + (list(faults).index(fault) * 40), relwidth=1)

        label = ttk.Label(frame, text=f"{fault}:", font=("Arial", 14))
        label.pack(side="left", padx=5)

        data_label = ttk.Label(frame, text="0", font=("Arial", 14), width=15, anchor="e")
        data_label.pack(side="right", padx=5)

        faultFields[fault] = data_label  # Store Label widget
    
    def update_camera():
        # Create a black image (480x640)
        frame = cv2.UMat(480, 640, cv2.CV_8UC3)  # Create a black image
        img = PIL.Image.fromarray(frame.get())  # Convert it to PIL image
        img_tk = PIL.ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image

        video_label.img_tk = img_tk  # Keep reference to avoid garbage collection
        video_label.config(image=img_tk)  # Update the label to show the image

        root.after(50, update_camera)  # Refresh every 50ms

    # Function to update display fields
    def update_display():
        message = simulate_can_data()
        try:
            decoded_msg = db.decode_message(message['arbitration_id'], message['data'])

            for param, label in fields.items():
                if param in decoded_msg:
                    value = decoded_msg[param]
                    label.config(text=f"{value}")
                    label.update_idletasks()

            if 'CustomFlag' in decoded_msg:
                bits = BitArray(decoded_msg['CustomFlag'].to_bytes()).bin
                for index in range(0, 4):
                    label = faultFields[customFlagIndices[index]]
                    value = "ERROR!" if bits[index] == '1' else ""
                    label.config(text=f"{value}")
                    label.update_idletasks()

        except Exception as e:
            print(f"Error decoding CAN message: {e}")

        root.after(2000, update_display)

    # Start updating UI elements
    update_display()
    update_camera()

    root.mainloop()

if __name__ == "__main__":
    create_display_window()
