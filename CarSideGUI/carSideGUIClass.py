"""
Author: Ryanne Wilson
carSideGUI

Auto-checks for backup camera.
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


# Pi Foundation Display - 7" Touchscreen Display
WIDTH, HEIGHT = 800,480
DIMENSIONS = '{}x{}'.format(WIDTH,HEIGHT)

# Background image for the GUI
BACKGROUND = 'CarSideGUI/bg.jpg'

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

PADDING = 20

class CarSideGUI:


    def __init__(self):
        """
        Sets up the GUI and then calls necessary loops.
        """
        print("INITED!")
        self.camera = None

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


        # """
        # Background image setup
        # """
        # self.bgImage = PIL.ImageTk.PhotoImage(PIL.Image.open(BACKGROUND))
        # self.imglabel = tk.Label(self.root,image=self.bgImage)
        # self.imglabel.img = self.bgImage # type: ignore
        # self.imglabel.place(relx=0.5,rely=0.5,anchor='center')

        self.fault_font = tkFont.Font(family="Arial",size=25)
        self.fault_label = tk.Label(text="WARNING: FAULT. PULL OVER ASAP!",font=self.fault_font,foreground='maroon1',background=BGCOLOR)

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
        # tkRaise?
        self.videoLabel = Label(self.camFrame,width=48,background=BGCOLOR)
        self.videoLabel.pack(expand=True)

        self.init_cam()
        self._update_camera()
        self.root.mainloop()
        
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
            
            self.currentCamImage.resize(self.ratio) # type: ignore
            self.dataFrame.pack(side=tk.RIGHT,expand=True,fill=tk.BOTH)
            self.videoLabel.img_tk = PIL.ImageTk.PhotoImage(self.currentCamImage) # type: ignore
            
            self.fault_label.place_forget()
            
        else:
            # fullscreen
            self.ratio = CAM_MAX_RATIO
            self.dataFrame.pack_forget()
            self.fault_label.place(x=100,y=10)
            self.fault_label.tkraise()
        
        

    def init_cam(self):
        """
        Initializes the camera
        """
        self.camera = None
        if Picamera2:
            try:
                self.camera = Picamera2()
                config = self.camera.create_preview_configuration(main={"size": CAM_MIN_RATIO})
                self.camera.configure(config)
                self.camera.start()
            except Exception as e:
                print(f"Camera error: {e}")
                self.camera = None
        
    def _update_camera(self):
        """
        Updates the camera
        """

        
        # if camera:
        try:
            # frame = camera.capture_array()
            # image = PIL.Image.fromarray(frame)
            FILE = "CarSideGUI/LastBanquetOfTheGirondins.jpg" # Example
            self.currentCamImage = PIL.Image.open(FILE)
            self.currentCamImage = self.currentCamImage.resize(self.ratio) # type: ignore
            img_tk = PIL.ImageTk.PhotoImage(self.currentCamImage)
            self.videoLabel.img_tk = img_tk # type: ignore
            self.videoLabel.config(image=img_tk)
        except Exception as e:
            print(f"Camera frame error: {e}")
        self.root.after(5,self._update_camera)


c = CarSideGUI()