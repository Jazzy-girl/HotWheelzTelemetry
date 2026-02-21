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
# from Pit.packet import ParsedPacket
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
CAM_MIN_RATIO = (426, 240)
CAM_MAX_RATIO = (640,360)
BACKGROUND = 'CarSideGUI/bg.jpg'
WIDTH, HEIGHT = 800,480
DIMENSIONS = '{}x{}'.format(WIDTH,HEIGHT) # Pi Foudnation DIsplay - 7" Touchscreen Display for Raspberry Pi


minimize: bool
minimize = True

# root.state('zoomed')

# UNUSED
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
            config = camera.create_preview_configuration(main={"size": CAM_MIN_RATIO})
            camera.configure(config)
            camera.start()
        except Exception as e:
            print(f"Camera error: {e}")
            camera = None


def fullscreen(event, ratio, data_frame: tk.Frame,fault_label: tk.Label):
    """
    fullscreens / minimizes the backup camera
    """
    print("CLICK!")
    global minimize
    minimize = not minimize
    print(minimize)
    if(minimize==True):
        ratio[0] = CAM_MIN_RATIO
        data_frame.pack(side=tk.RIGHT,expand=True,fill=tk.Y)
        fault_label.place_forget()
    else:
        ratio[0] = CAM_MAX_RATIO
        data_frame.pack_forget()
        fault_label.place(x=100,y=10)

def fault(event, fault_label: tk.Label):
    """
    Makes fault warning appear / disappear
    """
    fault_label.place(x=100,y=10)
    print("FAULT!")



def update_display():
    """
    Gets ParsedPackets and updates the display as necessary.
    If faults occur, displays faults on top of other things
    """



def setup():
    root = tk.Tk()
    root.title("Dashboard")

    ratio = [CAM_MIN_RATIO]
    root.bind('<Button-1>',lambda event: fullscreen(event,ratio,data_frame,fault_label)) # On 
    root.bind('<Button-2>',lambda event: fault(event,fault_label)) # On 
    root.geometry(DIMENSIONS)

    """
    Data Labels
    """


    fault_font = tkFont.Font(family="Arial",size=25)
    fault_label = tk.Label(text="WARNING: FAULT. PULL OVER ASAP!",font=fault_font,fg='red')

    bgImage = PIL.ImageTk.PhotoImage(PIL.Image.open(BACKGROUND))
    imglabel = tk.Label(root,image=bgImage)
    imglabel.img = bgImage # type: ignore
    imglabel.place(relx=0.5,rely=0.5,anchor='center')

    data_frame = tk.Frame(root, background='')
    
    data_frame.pack(side=tk.RIGHT,expand=True)
    data_font = tkFont.Font(family="Arial",size=20)
    label_font = tkFont.Font(family="Arial",size=25)


    FIELDS = ['Speed','Power','Cockpit Temp']
    for i in range(len(FIELDS)):
        data_frame.rowconfigure(i,weight=1)

    NUMCOLS = 2
    for i in range(0,NUMCOLS):
        data_frame.columnconfigure(i,weight=1)
    
    for i in range(len(FIELDS)):
        row = i
        # if(i>1):
        #     row += 1
        #     if(i > 3):
        #         row += 1
        data_col = 0
        output_col = 1
        data_label = Label(data_frame,text=FIELDS[i],font=data_font)
        data_label.grid(row=row,column=data_col,pady=(0,0),padx=(0,0))
        output_label = Label(data_frame,text="25%",font=label_font,)
        output_label.grid(row=row,column=output_col)

    data_frame.tkraise()

    cam_frame = tk.Frame(root,background='')
    cam_frame.pack(side=tk.LEFT,expand=True)




    cam_frame.tkraise()

    video_label = Label(cam_frame,width=48)
    video_label.pack(expand=True)
    

    init_cam()

    def update_camera():
        # if camera:
        try:
            # frame = camera.capture_array()
            # image = PIL.Image.fromarray(frame)
            FILE = "CarSideGUI/LastBanquetOfTheGirondins.jpg" # Example
            image = PIL.Image.open(FILE)
            image = image.resize(ratio[0])
            img_tk = PIL.ImageTk.PhotoImage(image)
            video_label.img_tk = img_tk # type: ignore
            video_label.config(image=img_tk)
        except Exception as e:
            print(f"Camera frame error: {e}")
        root.after(10000,update_camera)

    update_camera()

def loop():
    




    

    



    root.mainloop()

setup()
