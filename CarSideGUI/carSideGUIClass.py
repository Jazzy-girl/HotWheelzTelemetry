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

class CarSideGUI:


    def __init__(self):
        """
        Sets up the GUI and then calls necessary loops.
        """
        self.camera = None

        self.minimized: bool
        self.minimized = True

        self.root = tk.Tk()
        self.root.title("Dashboard")

        

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
        
        

    
    def loop(self):
        """
        The constant loop for checking things.
        """