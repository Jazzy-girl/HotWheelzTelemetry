from Telemetry.Pit.GraphData import *
from Telemetry.Pit.Graph import Graph
from Telemetry.packet import ParsedPacket, FaultSet
import datetime
import tkinter as tk
from tkinter import font
from tkinter import messagebox
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from random import randint
from PIL import Image, ImageTk

"""
Pit side Dashboard app.

Current features:
    - All packet fields
    - Current faults
    - Map of Minnesota track that can track vehicle location
    - Graphs
        Cockpit temp / time
        Pack Open Voltage / time
        Current / time
        Highest temp / time

Authors:
Ryanne Wilson
Gem Martinage


Layout (Frames):

root
    left_frame: LEFT
        buttons_frame: TOP
            field_button: LEFT
            map_button: LEFT
            fault_button: LEFT
        data_frame: BOTTOM
            switch / one at a time [
                fields_frame:
                    canvas:
                        scrollbar
                        grid:
                            Parameter / Value / Unit
                            Speed     / xx    / mph
                            Pack Open Volt / xx  / yy
                map_frame:
                    map image
                faults_frame:
                    grid like fields but a little different
            ]
    right_frame: RIGHT
        connection_frame: TOP
        select_graph_frame: TOP
            cockpit_select: LEFT
            POV_select: LEFT
            current_select: LEFT
            highest_temp_select: LEFT
        graph_frame: BOTTOM

"""

from collections import deque

#TODO: Re: Units, Do we need "0.1 V" or did Data Collection already convert it into regular 1 V, etc?
SPD = "Speed"
POV = "Pack Open Voltage"
SUM = "Pack Summed Voltage"
SOC = "Pack SOC"
ADC = "Current ADC1"
HITEMP = "High Temperature"
LOTEMP = "Low Temperature"
HITHERM = "High Thermistor ID"
LOTHERM = "Low Thermistor ID"
FANSPEED = "Fan Speed"
HICELL = "Highest Cell"
LOCELL = "Lowest Cell"
HIVOLT = "High Cell Voltage ID"
LOVOLT = "Low Cell Voltage ID"
SUPPLY = "12v Supply"
FIELDS = [
    [SPD, "Mph"],
    [POV, "V"],
    [SUM,"V"],
    [SOC,"%"],
    [ADC,"???"],
    [HITEMP,"C"],
    [LOTEMP,"C"],
    [HITHERM,"N/A"],
    [LOTHERM,"N/A"],
    [FANSPEED," 0 - 6"],
    [HICELL,"V"],
    [LOCELL,"V"],
    [HIVOLT,"N/A"],
    [LOVOLT,"N/A"],
    [SUPPLY, "V"]
]
"""
Format: [term, units]
All 15 fields that must be displayed.
"""


"""
GRAPH TITLES
"""
COCKPITSEL = "Cockpit Temperature"
POVSEL = "Pack Open Voltage"
CURRENTSEL = "ADC Current"
HITEMPSEL = "Highest Temperature"



MAP_DIMENSIONS = (618,773)#(444,624)#(500,500)
CAR_DIMENSIONS = (10,10)


# SELECT CONSTANTS
SELECT_FIELDS = 0
SELECT_MAP = 1
SELECT_FAULTS = 2

# MAP FIELDS
"""
Notes on the map fields:
    The map image currently used is taken from Google maps and suffers from the issues that
    all 2D images of the globe do-- warping, stretching, imperfect projection of 3D object.

    The constants below, labeled OFFSET_, _SCALEm etc, are the result of various tests I (Ryanne)
    performed to determine which numbers would result in the most accurate tracking of the vehicle.

    A VERY IMPORTANT THING TO NOTE:
        The map is rotated 90 degrees, such that latitude and longitude on the map are swapped
        from the real latitude and longitude on the globe.
        (so on the map, x = lat, y = long)

"""
OFFSET_ACTUAL_LAT = (46.417919)
MIN_ACTUAL_LAT = (46.40682)

X_ANCHOR_1 = 357
X_ANCHOR_2 = 122
LAT_ANCHOR_1 = 46.413089
LAT_ANCHOR_2 = 46.416308

LAT_SCALE = (X_ANCHOR_2 - X_ANCHOR_1) / (LAT_ANCHOR_2 - LAT_ANCHOR_1)
LAT_OFFSET = X_ANCHOR_1 - LAT_SCALE * LAT_ANCHOR_1

GPS_SCALE = 10**6
WIDTH_ACTUAL_LAT = (OFFSET_ACTUAL_LAT - MIN_ACTUAL_LAT) * GPS_SCALE

OFFSET_ACTUAL_LONG = 94.266378
MAX_ACTUAL_LONG = 94.281506
HEIGHT_ACTUAL_LONG = (OFFSET_ACTUAL_LONG - MAX_ACTUAL_LONG) * GPS_SCALE

class Dashboard:
    root = tk.Tk()
    root.title("Dashboard")
    background = "black"
    root.geometry("1200x800")
    root.state('zoomed')
    MAX_ELEMENTS = 30
    MAP_FILE = "Telemetry/Pit/trackMap.png"
    CAR_FILE = "Telemetry/Pit/car.jpg"
    LARGE_FONT = font.Font(family='Georgia',size=24,weight='bold')
    SMALL_FONT = font.Font(family='Georgia',size=12)

    # dict for associating buttons with data frames so the screen updates when buttons are selected
    buttons_to_data_frames : dict[tk.Button, tk.Frame]

    buttons_to_data_frames = dict()

    # dict for associating data with labels so labels can update their data text
    data_to_labels : dict[str, tk.Label]
    data_to_labels = dict()

    # dict of all graph buttons, used for highlighting / greying out buttons when selected / unselected
    graph_buttons : list[tk.Button]
    graph_buttons = list()

    # DEBUG FIELD:
    # used as a 'time' representation, updated whenever a new packet is randomly generated
    timeForRandGen = 0

    # set of all active faults, used for display and tracking
    activeFaults: set[str]
    activeFaults = set()




    def _makeFrame(self, parent, side, bg=background, pack=True, borderwidth=7, relief=tk.SUNKEN, expand=True, fill=tk.BOTH):
        """
        Makes a frame. Will pack it to its parent if pack==True
        """
        frame = tk.Frame(parent, bg=bg, borderwidth=borderwidth, relief=relief) # pyright: ignore[reportArgumentType]
        if(pack):
            frame.pack(side=side, expand=expand, fill=fill) # pyright: ignore[reportArgumentType]
        return frame

    def _makeLabel(self, parent: tk.Frame, text: str, side: str | None, font=LARGE_FONT, pady=20, padx=1, pack=True, grid=False, row = 0, col = 0, colspan=1):
        label = tk.Label(parent, text=text, font=font)
        if(pack):
            label.pack(side=side, pady=pady) # pyright: ignore[reportArgumentType]
        if(grid):
            label.grid(row=row, column=col, columnspan=colspan, sticky=tk.NSEW, pady=pady, padx=padx)
        return label

    def _makeButton(self, parent: tk.Frame, text: str, side=tk.LEFT, useconfigure=True, pack=True, fill=tk.BOTH, expand=True):
        button = tk.Button(master=parent,text=text, height=2)
        if(useconfigure):
            button.configure(command=lambda: self.switchLeftViews(button=button))
        button.pack(side=side,fill=fill,expand=expand) # pyright: ignore[reportArgumentType]
        return button
    
    
    def switchLeftViews(self, button: tk.Button):
        """
        Switches which frame is being displayed in data_frame according to which button is pressed
        """

        frame_to_pack = self.buttons_to_data_frames[button]

        if frame_to_pack.winfo_ismapped(): # the frame already is selected
            return
        else:                              # the frame is not already selected
            # forget other frames
            # pack the correct frame
            # make the current button gray
            # make the other buttons white
            for iterate_button, iterate_frame in self.buttons_to_data_frames.items():
                if iterate_frame != frame_to_pack:
                    iterate_frame.forget()
                    iterate_button.configure(bg="white")
                else:
                    iterate_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
                    iterate_button.configure(bg="grey")

    def _initFaultFrame(self):
        self.faults_frame = self._makeFrame(parent=self.data_frame, side=tk.BOTTOM, expand=True, pack=False)
        self.canvas_faults_frame = tk.Canvas(self.faults_frame)
        self.canvas_faults_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # scrolling!
        self.faults_scrollbar = tk.Scrollbar(self.faults_frame, orient=tk.VERTICAL,
                                      command=self.canvas_faults_frame.yview)
        self.faults_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_faults_frame.configure(yscrollcommand=self.faults_scrollbar.set)

        self.faults_grid = self._makeFrame(self.canvas_faults_frame, side=None, bg="grey", pack=False, borderwidth=0)
        self.canvas_faults_window = self.canvas_faults_frame.create_window((0,0), window=self.faults_grid, anchor="nw" )

        self.faults_grid.bind("<Configure>", lambda e:
                              self.canvas_faults_frame.
                              configure(scrollregion=self.canvas_faults_frame.bbox("all")))
        
        self.canvas_faults_frame.bind("<Configure>", lambda e:
                                self.canvas_faults_frame.itemconfig(self.canvas_faults_window, 
                                width=e.width, height=e.height))
        
        # 2 columns
        numcols = 4
        for i in range(0,numcols):
            self.faults_grid.columnconfigure(i, weight=1)
        for i in range(0,len(FaultSet.FAULTS)+1): # +1 for the header
            self.faults_grid.rowconfigure(i, weight=1)
        
        # fault label spans 3 cols; the start time label spans 1
        fault_label = self._makeLabel(
            self.faults_grid, side=None, pady=1, font=self.SMALL_FONT, text="Fault", pack=False, grid=True, colspan=3)
        start_time_label = self._makeLabel(
            self.faults_grid, side=None, pady=1,font=self.SMALL_FONT, text="Start Time", col=3, pack=False, grid=True)
        
    def _addFaultToFaultFrame(self, faultName: str):
        """
        Adds a given fault to the fault frame and to the activeFaults list.
        Logs the name of the fault and the time it was received.
        """
        self.activeFaults.add(faultName)

        self.faultField = self._makeLabel(self.faults_grid, side=None, text=faultName, font=self.SMALL_FONT,
                                     row=len(self.activeFaults), col=0, colspan=3, pady=1, pack=False, grid=True)
        
        # get the current time
        currentTime = datetime.datetime.now()
        currentTime = currentTime.strftime("%H: %M")

        self.timeField = self._makeLabel(self.faults_grid, side=None, text=currentTime, font=self.SMALL_FONT,
                                     row=len(self.activeFaults), col=3, pady=1, pack=False, grid=True)

        popup = tk.Toplevel(self.root)
        popup.title("Fault Active")
        popupLabel = tk.Label(popup, text=f"{faultName} active at {currentTime}")
        popupLabel.pack()


        

    def _initFieldsFrame(self):
        # Field Frame
        self.fields_frame = self._makeFrame(parent=self.data_frame,side=tk.BOTTOM, expand=True)
        self.canvas_fields_frame = tk.Canvas(self.fields_frame)
        self.canvas_fields_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        # scrolling!
        self.scrollbar = tk.Scrollbar(self.fields_frame, orient=tk.VERTICAL,
                                      command=self.canvas_fields_frame.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_fields_frame.configure(yscrollcommand=self.scrollbar.set)
        
        self.fields_grid = self._makeFrame(self.canvas_fields_frame, side=None, bg="grey", pack=False, borderwidth=0)
        self.canvas_window = self.canvas_fields_frame.create_window((0,0), window=self.fields_grid, anchor="nw" )

        self.fields_grid.bind("<Configure>", lambda e:
                              self.canvas_fields_frame.
                              configure(scrollregion=self.canvas_fields_frame.bbox("all")))
        
        self.canvas_fields_frame.bind("<Configure>", lambda e:
                                        self.canvas_fields_frame.itemconfig(self.canvas_window, width=e.width, height=e.height))
        
        # 4 columns
        for i in range(0,4):
            self.fields_grid.columnconfigure(i, weight=1)
        for i in range(0,len(FIELDS)+1):
            self.fields_grid.rowconfigure(i, weight=1)

        # param label spans 2 cols; the other labels each span 1
        param_label = self._makeLabel(
            self.fields_grid, side=None, pady=1, font=self.SMALL_FONT, text="Parameter", pack=False, grid=True, colspan=2)
        val_label = self._makeLabel(
            self.fields_grid, side=None, pady=1,font=self.SMALL_FONT, text="Value", col=2, pack=False, grid=True)
        unit_label = self._makeLabel(
            self.fields_grid, side=None, pady=1,font=self.SMALL_FONT, text="Unit", col=3, pack=False, grid=True)

        # make actual fields: param, val, unit
        for i in range(0,len(FIELDS)):
            name = FIELDS[i][0]
            unit = FIELDS[i][1]


            # the name
            param_field = self._makeLabel(
                self.fields_grid, side=None, text=name, font=self.SMALL_FONT,
                row=i+1, col=0, colspan=2, pady=1, pack=False, grid=True
            )

            # the updating value-- self. b/c need a permanent reference? maybe?
            val_field = self._makeLabel(
                self.fields_grid, side=None, text="1234", font=self.SMALL_FONT,
                row=i+1, col=2, pady=1, pack=False, grid=True
            )

            # the unit
            unit_field = self._makeLabel(
                self.fields_grid, side=None, text=unit, font=self.SMALL_FONT,
                row=i+1, col=3, pady=1, pack=False, grid=True
            )

            self.data_to_labels[name] = val_field


    def _placeCar(self, actual_lat: float, actual_long: float):
        """
        Takes in latitude and longitude coords and projects the vehicle onto that location on the map.
        """
        height_px = MAP_DIMENSIONS[1]

        x = LAT_SCALE * actual_lat + LAT_OFFSET
        y = -1 * ((actual_long - OFFSET_ACTUAL_LONG)*(GPS_SCALE)) // (HEIGHT_ACTUAL_LONG / height_px)
        print(f"x: {x}\ty: {y}\n")
        self.car.place(x=x,y=y,anchor=tk.CENTER)

    def _move(self, event):
        """
        DEBUG FUNCTION:
        Click and the car is moved to actual_lat and actual_long coords.
        """

        # should be in upper left corner on the bend.
        actual_lat = 46.41787778
        actual_long = 94.27161944

        print(f"LONG: {actual_lat}\tLAT: {actual_long}\n")
        self._placeCar(actual_lat, actual_long)

    def _initMapFrame(self):
        self.map_frame = self._makeFrame(parent=self.data_frame, side=tk.BOTTOM, expand=True, pack=False)

        # map frame
        img = Image.open(self.MAP_FILE)
        img_data = img.resize(MAP_DIMENSIONS) # frame dimensions
        self.map_img = ImageTk.PhotoImage(img_data)

        self.map_label = tk.Label(self.map_frame, image=self.map_img,padx=0,pady=0)
        # DEBUG FUNCTION:
        # used to test if lat and long projctions are accurate.
        # self.map_label.bind("<Button-1>", self._move) # type: ignore
        width = MAP_DIMENSIONS[0]
        height = MAP_DIMENSIONS[1]
        
        image = Image.open(self.CAR_FILE)
        image_data = image.resize(CAR_DIMENSIONS)
        self.car_img = ImageTk.PhotoImage(image_data)

        self.car = tk.Label(self.map_frame, image=self.car_img)

        # place the car onto the map.
        x = width/2.0
        y = height/2.0
        self.car.place(x=0,y=0,anchor=tk.CENTER)

        self.map_label.place(x=0,y=0)
    


    def _initLeftSide(self):
        """
        Left Side
        """
        # holds all frames on the left side (ie everything except graph and connectivity)
        self.left_frame = self._makeFrame(self.root, tk.LEFT)

        # holds all the data button selectors: Fields, Map, Faults
        self.select_frame = self._makeFrame(self.left_frame, tk.TOP, expand=False, fill=tk.BOTH)

        self.fields_button = self._makeButton(self.select_frame, "Fields")
        self.fields_button.configure(bg="grey")
        self.map_button = self._makeButton(self.select_frame, "Map")
        self.fault_button = self._makeButton(self.select_frame, "Faults")


        # holds all the data options: Fields, Map, Faults
        self.data_frame = self._makeFrame(self.left_frame, tk.BOTTOM)
        self.data_frame.pack_propagate(False)

        self._initFieldsFrame()
        self._initMapFrame()
        self._initFaultFrame()

        self.buttons_to_data_frames[self.fields_button] = self.fields_frame
        self.buttons_to_data_frames[self.map_button] = self.map_frame
        self.buttons_to_data_frames[self.fault_button] = self.faults_frame

        

    def _initRightSide(self):
        """
        Right Side
        """

        # holds all frames on right side
        self.right_frame = self._makeFrame(self.root, side=tk.RIGHT)

        # select graph frame
        self.select_graph_frame = self._makeFrame(self.right_frame, tk.TOP, "white")

        # make buttons
        self.cockpit_sel = self._makeButton(self.select_graph_frame, "Cockpit Temp (C)", tk.LEFT, useconfigure=False)
        self.POV_sel = self._makeButton(self.select_graph_frame, "POV (V)", tk.LEFT, useconfigure=False)
        self.current_sel = self._makeButton(self.select_graph_frame, "Current (V)", tk.LEFT, useconfigure=False)
        self.highest_temp_sel = self._makeButton(self.select_graph_frame, "High Temp (V)", tk.LEFT, useconfigure=False)



        self.graph_buttons.append(self.cockpit_sel)
        self.graph_buttons.append(self.POV_sel)
        self.graph_buttons.append(self.current_sel)
        self.graph_buttons.append(self.highest_temp_sel)

        # start on cockpitsel
        self.cockpit_sel.config(bg="grey")

        # graph frame
        self.graph_frame = self._makeFrame(self.right_frame, tk.BOTTOM, "white")

        self.graph_label = tk.Label(self.graph_frame, text=COCKPITSEL, bg="white", font=("Comic Sans MS", 16))
        self.graph_label.pack()
        # self.graph_frame, self.graph_label = self._box(self.graph_frame, "Graph Area", width = 1000, height = 600)

        self.cockpit_sel.configure(command=lambda: self._switchGraphs(GraphDataCockpit(self.parsedPackets, self.MAX_ELEMENTS),self.cockpit_sel, COCKPITSEL, self.graph_label))
        self.POV_sel.configure(command=lambda: self._switchGraphs(GraphDataPOV(self.parsedPackets, self.MAX_ELEMENTS), self.POV_sel, POVSEL, self.graph_label))
        self.current_sel.configure(command=lambda: self._switchGraphs(GraphDataCurrent(self.parsedPackets, self.MAX_ELEMENTS), self.current_sel, CURRENTSEL, self.graph_label))
        self.highest_temp_sel.configure(command=lambda: self._switchGraphs(GraphDataHighest(self.parsedPackets, self.MAX_ELEMENTS), self.highest_temp_sel, HITEMPSEL, self.graph_label))

        self.parsedPackets: deque[ParsedPacket]
        self.parsedPackets = deque()

        self.graph_data = GraphDataCockpit(self.parsedPackets, self.MAX_ELEMENTS)
        self.graph = Graph(self.graph_data, self.graph_frame, self.root, self.MAX_ELEMENTS)

    def _switchGraphs(self, input: GraphDataInterface, button: tk.Button, title: str, titleLabel: tk.Label):
        """
        Switches which graph is being displayed in the graph_frame according to which button is pressed
        """
        # switch!
        self.graph.setInput(input)
        self.graph_data = input
        
        # grey and un-grey
        for x in self.graph_buttons:
            if button == x:
                x.config(bg="grey")
            else:
                x.config(bg="white")
        
        titleLabel.config(text=title)

    def __init__(self) -> None:
        self._initLeftSide()
        self._initRightSide()
        
    
    def start(self):
        # DEBUG: self.root.after(100, self._randGenParsed)
        self.root.after(1000, self.graph.start)
        
        self.root.mainloop()
    
    def _randGenParsed(self):
        self.timeForRandGen += 1
        faults = FaultSet(randint(0,21))
        packet = ParsedPacket(randint(0,100),self.timeForRandGen,randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              faults,randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100))
        self.addParsedPacket(packet=packet)
        # DEBUG: self.root.after(500, self._randGenParsed)
        
    
    def _updateFields(self, value, labelName):
        formatted_value = "{:.2f}".format(value)
        
        self.data_to_labels[labelName].config(text=formatted_value)

    def addParsedPacket(self, packet: ParsedPacket):
        """
        Public method to add parsed packets.
        Adds the packet to the graph and updates the fields and faults.
        """

        # Fields!
        self.graph_data.addElement(packet)
        self._updateFields(packet.motor_speed, SPD)
        self._updateFields(packet.bms_open_voltage, POV)
        self._updateFields(packet.bms_summed_voltage, SUM)
        self._updateFields(packet.bms_soc, SOC)
        self._updateFields(packet.bms_current, ADC)
        self._updateFields(packet.bms_high_temp, HITEMP)
        self._updateFields(packet.bms_low_temp, LOTEMP)
        self._updateFields(packet.bms_high_therm_id, HITHERM)
        self._updateFields(packet.bms_low_therm_id, LOTHERM)
        self._updateFields(packet.bms_fan_speed, FANSPEED)
        self._updateFields(packet.bms_high_cell_volt, HICELL)
        self._updateFields(packet.bms_low_cell_volt, LOCELL)
        self._updateFields(packet.bms_high_cell_id, HIVOLT)
        self._updateFields(packet.bms_low_cell_id, LOVOLT)
        self._updateFields(packet.bms_supply_12v, SUPPLY)

        # Faults!
        for fault in packet.bms_faults.list_faults():
            if fault not in self.activeFaults:
                self._addFaultToFaultFrame(fault)
        
        # GPS UPDATE!
        self._placeCar(packet.gps_lat, packet.gps_lon)


    def _box(self, parent, title_text, width=150, height = 120):
        """
        Makes a box. Can determine width and height.
        """
        frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
        frame.grid_propagate(False)
        label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
        label.pack(pady=5)
        return frame, label