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
from Telemetry.packet import FaultSet
import PIL.Image, PIL.ImageTk
from tkinter.ttk import *
try:
    from picamera2 import Picamera2
except ImportError:
    print("Running on non-RPI system - camera not available.")
    Picamera2 = None


# Pi Foundation Display - 7" Touchscreen Display
WIDTH, HEIGHT = 800,480
DIMENSIONS = '{}x{}'.format(WIDTH,HEIGHT)

# Background image for the GUI
BACKGROUND = 'Telemetry/Car/GUI/bg.jpg'

# Minimized and Maximized aspect ratio for the camera.
CAM_MIN_RATIO = (426,240)
CAM_MAX_RATIO = (640,360)

# Fields to be displayed
FIELDS = ['Speed','Power','Cockpit Temp']

# Number of columns of data
NUMCOLS = 2

# background color
BGCOLOR = 'black'
FGCOLOR = 'white'
FAULTCOLOR = 'maroon1'

PADDING = 20

class CarSideGUI:


    def __init__(self, before_run = lambda _: None):
        """
        Sets up the GUI and then calls necessary loops.
        """
        self.camera = None

        self.faultActive: bool
        self.faultActive = False

        self.minimized: bool
        self.minimized = True

        self.root = tk.Tk()
        self.root.title("Dashboard")

        self.ratio = CAM_MIN_RATIO
        self.root.bind('<Button-1>',lambda event: self._fullscreen(event)) # On 

        self.root.geometry(DIMENSIONS)

        """
        Fault label. To be displayed only while a fault is occurring.
        """

        self.fault_font = tkFont.Font(family="Arial",size=25)
        self.faultLabel = tk.Label(text="WARNING: FAULT. PULL OVER ASAP!",font=self.fault_font,foreground=FAULTCOLOR,background=BGCOLOR)

        """
        Set up data frame + labels
        """
        self.dataFrame = tk.Frame(self.root, background=BGCOLOR)

        self.dataFrame.pack(side=tk.RIGHT,expand=True,fill=tk.BOTH)
        self.outputFont = tkFont.Font(family="Arial",size=25)
        self.labelFont = tkFont.Font(family="Arial",size=20)

        self.labelFrame = tk.Frame(self.dataFrame,background=BGCOLOR)
        self.outputFrame = tk.Frame(self.dataFrame,background=BGCOLOR)
        self.labelFrame.pack(side=tk.LEFT)
        self.outputFrame.pack(side=tk.RIGHT)

        for i in range(len(FIELDS)):
            self.dataFrame.rowconfigure(i,weight=1)
        
        for i in range(0,NUMCOLS):
            self.dataFrame.columnconfigure(i,weight=1)
        
        self.speedLabel, self.speedOutput = self._makeLabels(text=FIELDS[0],row=0)
        self.powerLabel, self.powerOutput = self._makeLabels(text=FIELDS[1],row=1)
        self.tempLabel, self.tempOutput = self._makeLabels(text=FIELDS[2],row=2)

        """
        Set up camera
        """
        self.camFrame = tk.Frame(self.root,background=BGCOLOR)
        self.camFrame.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        self.videoLabel = Label(self.camFrame,width=48,background=BGCOLOR)
        self.videoLabel.pack(expand=True)

        self.init_cam()
        
    def _makeLabels(self,text:str,row:int):
        """
        Helper function.
        Makes a data label and a corresponding output label.
        """
        data_label = Label(self.labelFrame,text=f'{text}:',font=self.labelFont,background=BGCOLOR,padding=PADDING,foreground=FGCOLOR)
        data_label.pack()
        output_label = Label(self.outputFrame,text="25%",font=self.outputFont,background=BGCOLOR,foreground=FGCOLOR,padding=PADDING)
        output_label.pack()
        return data_label,output_label
    
    def _fullscreen(self,event):
        """
        Detects a touch to fullscreen / minimize the backup camera.
        """
        print("CLICK!")
        self.minimized = not self.minimized
        print(self.minimized)
        if(self.minimized):
            # minimized
            
            self.ratio = CAM_MIN_RATIO
            if(self.camera):
                self.currentCamImage.resize(self.ratio) # type: ignore
                self.videoLabel.img_tk = PIL.ImageTk.PhotoImage(self.currentCamImage) # type: ignore
            self.dataFrame.pack(side=tk.RIGHT,expand=True,fill=tk.BOTH)
            
        else:
            # fullscreen
            self.ratio = CAM_MAX_RATIO
            self.dataFrame.pack_forget()
        
    def init_cam(self):
        """
        Initializes the camera
        """
        self.camera = None
        if Picamera2:
            if len(Picamera2.global_camera_info()) > 0:
                try:
                    self.camera = Picamera2()
                    config = self.camera.create_preview_configuration(main={"size": CAM_MIN_RATIO})
                    self.camera.configure(config)
                    self.camera.start()
                except Exception as e:
                    print(f"Camera error: {e}")
                    self.camera = None
            else:
                print("No cameras available")
        else:
            print("Picamera2 is unavailable")
        
    def _update_camera(self):
        """
        Updates the camera
        """
        
        if self.camera:
            try:
                frame = self.camera.capture_array()
                image = PIL.Image.fromarray(frame)
                self.currentCamImage = image.resize(self.ratio) # type: ignore
                img_tk = PIL.ImageTk.PhotoImage(self.currentCamImage)
                self.videoLabel.img_tk = img_tk # type: ignore
                self.videoLabel.config(image=img_tk)
            except Exception as e:
                print(f"Camera frame error: {e}")
        self.root.after(5,self._update_camera)
    
    def update_fields(self, motor_speed: float, bms_soc: float, therm_temp: float, bms_faults: FaultSet):
        """
        Input: ParsedPacket
        Updates the data fields and checks for faults.
        If a fault occurs

        speedOutput
        powerOutput
        tempOutput
        faultLabel
        """

        self.speedOutput = motor_speed
        self.powerOutput = bms_soc
        self.tempOutput = therm_temp

        if(bms_faults != 0):
            self.faultActive = True
            self.faultLabel.place(x=100,y=10)
            self.faultLabel.tkraise()
        elif(self.faultActive):
            self.faultActive = False
            self.faultLabel.place_forget()
    
    def start(self):
        self._update_camera()
        self.root.mainloop()