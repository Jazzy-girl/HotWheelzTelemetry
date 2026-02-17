"""
Authors: Ryanne Wilson

Car-side GUI, using Raspberry Pi.
Display: https://www.adafruit.com/product/2718
What is displayed:
    - Backup camera
    - Speed
    - Cockpit temperature
    - Car battery
    - 

Functionality:
    - User can touch the screen to minize/fullscreen the backup camera
"""
import tkinter as tk
import random
import time
import tkinter.font as tkFont
from Pit.packet import ParsedPacket
import PIL.Image, PIL.ImageTk
from tkinter.ttk import *
try:
    from picamera2 import Picamera2
except ImportError:
    print("Running on non-RPI system - camera not available.")
    Picamera2 = None

# 16:9 resolution
# Examples:
# 426 / 240
# 640 / 360
# 852 / 480 -- Will go off the screen
CAMERA_RATIO = (426, 240)

DIMENSIONS = '800x480' # Pi Foudnation DIsplay - 7" Touchscreen Display for Raspberry Pi

# root.state('zoomed')

def box(parent, title_text, width=150, height = 120):
    frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
    frame.grid_propagate(False)
    label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
    label.pack(pady=5)
    return frame, label


def init_cam():
    """
    Initializes the camera
    """
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



def setup():
    root = tk.Tk()
    root.title("Dashboard")
    background = "black"
    root.geometry(DIMENSIONS)
    cam_frame = tk.Frame(root, background=background)
    cam_frame.pack(side=tk.LEFT)

    video_label = Label(cam_frame,background=background,width=48)
    video_label.pack(expand=True)

    init_cam()

    def update_camera():
        # if camera:
        try:
            # frame = camera.capture_array()
            # image = PIL.Image.fromarray(frame)
            FILE = "CarSideGUI/LastBanquetOfTheGirondins.jpg" # Example
            image = PIL.Image.open(FILE)
            image = image.resize(CAMERA_RATIO)
            img_tk = PIL.ImageTk.PhotoImage(image)
            video_label.img_tk = img_tk # type: ignore
            video_label.config(image=img_tk)
        except Exception as e:
            print(f"Camera frame error: {e}")
        root.after(5,update_camera)

    update_camera()

    """
    Data Labels
    """
    data_frame = tk.Frame(root, background=background)
    data_frame.pack(side=tk.RIGHT,expand=True,fill=tk.BOTH)
    data_font = tkFont.Font(family="Arial",size=20)
    label_font = tkFont.Font(family="Arial",size=25)


    FIELDS = ['Speed','Power','Cockpit Temp']
    for i in range(len(FIELDS)*2):
        data_frame.rowconfigure(i,weight=1)
    data_frame.columnconfigure(0,weight=1)
    
    for i in range(len(FIELDS)):
        row = i
        # if(i>1):
        #     row += 1
        #     if(i > 3):
        #         row += 1
        data_col = 0
        output_col = 1
        data_label = Label(data_frame,text=FIELDS[i],font=data_font)
        data_label.grid(row=row,column=data_col,pady=(10,0),padx=(5,5))
        output_label = Label(data_frame,text="25%",font=label_font,)
        output_label.grid(row=row,column=output_col)


    #left
    # left_frame = tk.Frame(root, bg=background, width = 300)
    # left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # left_frame.pack_propagate(False)
    #use matplotlib to create graph corresponding to each box on the left side
    #6 by 2 grid of boxes on the left side
    # boxes = []
    # for i in range(6):
    #     for j in range(2):
    #         box_frame, box_label = box(left_frame, f"Box {i*2 + j + 1}")
    #         box_frame.grid(row=i, column=j, padx=3, pady=3)
    #         left_frame.grid_rowconfigure(i, weight=1)
    #         left_frame.grid_columnconfigure(j, weight=1)
    #         boxes.append((box_frame, box_label))

    #right
    # main_panel = tk.Frame(root, bg=background)
    # main_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
    # graph_frame = tk.Frame(main_panel, bg="white", borderwidth=7, relief=tk.SUNKEN)
    # gps_frame = tk.Frame(main_panel, bg="lightgrey", borderwidth=7, relief=tk.SUNKEN)
    # graph_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
    # gps_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

    # graph_frame, graph_label = box(graph_frame, "Graph Area", width = 1000, height = 600)
    # gps_frame, gps_label = box(gps_frame, "GPS Data Area", width = 1000, height = 600)

    root.mainloop()

setup()
