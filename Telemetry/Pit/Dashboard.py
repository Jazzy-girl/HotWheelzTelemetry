from Telemetry.Pit.GraphData import *
from Telemetry.Pit.Graph import Graph
from Telemetry.packet import ParsedPacket, FaultSet

import tkinter as tk
from tkinter import font
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from random import randint
from PIL import Image, ImageTk

"""
Dashboard
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

FIELDS = [
    "Speed",
    "Pack Open Voltage",
    "Pack Summed Voltage",
    "Pack SOC",
    "Current ADC1",
    "High Temperature",
    "Low Temperature",
    "High Thermistor ID",
    "Low Thermistor ID",
    "Fan Speed",
    "Highest Cell",
    "Lowest Cell",
    "High Cell Voltage ID",
    "Low Cell Voltage ID",
    "12v Supply"
]
"""
All 15 fields that must be displayed.
"""

"""
Dashboard

Graphs...
    Speed over time- select area of track
    Cockpit temp / time
    Pack Open Voltage / time
    Current / time
    Highest temp / time

For the non-speed over time graphs:
    store the last # entries. Use a ring buffer (?) or a deque
"""
MAP_DIMENSIONS = (500,500)


class Dashboard:
    root = tk.Tk()
    root.title("Dashboard")
    background = "black"
    root.geometry("1200x800")
    root.state('zoomed')
    MAX_ELEMENTS = 30
    MAP_FILE = "Telemetry/Pit/trackMap.png"
    LARGE_FONT = font.Font(family='Georgia',size=24,weight='bold')
    SMALL_FONT = font.Font(family='Georgia',size=12)


    def _makeFrame(self, parent, side, bg=background, pack=True, borderwidth=7, relief=tk.SUNKEN, expand=True, fill=tk.BOTH):
        """
        Makes a frame. Will pack it to its parent if pack==True
        """
        frame = tk.Frame(parent, bg=bg, borderwidth=borderwidth, relief=relief) # pyright: ignore[reportArgumentType]
        if(pack):
            frame.pack(side=side, expand=expand, fill=fill) # pyright: ignore[reportArgumentType]
        return frame

    def _makeLabel(self, parent: tk.Frame, text: str, side: str | None, font=LARGE_FONT, pady=20, pack=True, grid=False, row = 0, col = 0, colspan=1):
        label = tk.Label(parent, text=text, font=font)
        if(pack):
            label.pack(side=side, pady=pady) # pyright: ignore[reportArgumentType]
        if(grid):
            label.grid(row=row, column=col, columnspan=colspan, sticky=tk.EW)
        return label

    def _makeButton(self, parent: tk.Frame, text: str, side=tk.LEFT, pack=True, fill=tk.BOTH, expand=True):
        button = tk.Button(master=parent,text=text)
        button.pack(side=side,fill=fill,expand=expand) # pyright: ignore[reportArgumentType]
        return button
    
    def _initLeftSide(self):
        """
        Left Side
        """
        # holds all frames on the left side (ie everything except graph and connectivity)
        self.left_frame = self._makeFrame(self.root, tk.LEFT)

        # holds all the data button selectors: Fields, Map, Faults
        self.select_frame = self._makeFrame(self.left_frame, tk.TOP, expand=False, fill=tk.BOTH)
        self.fields_button = self._makeButton(self.select_frame, "Fields")

        self.map_button = self._makeButton(self.select_frame, "Map")
        self.fault_button = self._makeButton(self.select_frame, "Faults")

        # holds all the data options: Fields, Map, Faults
        self.data_frame = self._makeFrame(self.left_frame, tk.BOTTOM)

        # Field Frame
        self.fields_frame = self._makeFrame(parent=self.data_frame,side=tk.BOTTOM, expand=True)
        self.canvas_fields_frame = tk.Canvas(self.fields_frame)
        self.canvas_fields_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.fields_frame, orient=tk.VERTICAL,
                                      command=self.canvas_fields_frame.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_fields_frame.configure(yscrollcommand=self.scrollbar.set)
        
        self.fields_grid = tk.Frame(self.canvas_fields_frame)
        self.canvas_window = self.canvas_fields_frame.create_window((0,0), window=self.fields_grid, anchor="nw" )

        self.fields_grid.bind("<Configure>", lambda e:
                              self.canvas_fields_frame.
                              configure(scrollregion=self.canvas_fields_frame.bbox("all")))
        
        self.canvas_fields_frame.bind("<Configure>", lambda e:
                                        self.canvas_fields_frame.itemconfig(self.canvas_window, width=e.width))
        
        for i in range(0,3):
            self.fields_grid.columnconfigure(i, weight=1)
        self.fields_grid.rowconfigure(0, weight=1)

        param_label = self._makeLabel(self.fields_grid, side=None, font=self.SMALL_FONT, text="Parameter", pack=False, grid=True)
        val_label = self._makeLabel(
            self.fields_grid, side=None, font=self.SMALL_FONT, text="Value", col=1, pack=False, grid=True)
        

    def _initRightSide(self):
        """
        Right Side
        """

        # holds all frames on right side
        self.right_frame = self._makeFrame(self.root, side=tk.RIGHT)

        # graph frame
        self.graph_frame = self._makeFrame(self.right_frame, tk.BOTTOM, "white")

        self.graph_label = tk.Label(self.graph_frame, text="GRAPH", bg="white", font=("Comic Sans MS", 16))
        self.graph_label.pack()
        # self.graph_frame, self.graph_label = self._box(self.graph_frame, "Graph Area", width = 1000, height = 600)

        self.parsedPackets: deque[ParsedPacket]
        self.parsedPackets = deque()

        self.graph_data = GraphDataCockpit(self.parsedPackets, self.MAX_ELEMENTS)
        self.graph = Graph(self.graph_data, self.graph_frame, self.root, self.MAX_ELEMENTS)

        # # map frame
        # self.map_frame = self._makeFrame(self.root, side=tk.RIGHT, bg="white", pack=False)
        # img = Image.open(self.MAP_FILE)
        # img_data = img.resize(MAP_DIMENSIONS) # frame dimensions
        # self.map_img = ImageTk.PhotoImage(img_data)

        # self.map_label = tk.Label(self.map_frame, image=self.map_img)

        # self.map_label.pack()
    def __init__(self) -> None:
        self._initLeftSide()
        self._initRightSide()
        

        
        
    
    def start(self):
        self.root.after(100, self._randGenParsed)
        self.root.after(1000, self.graph.start)
        
        self.root.mainloop()
    
    def _randGenParsed(self):
        parsed = ParsedPacket(randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              FaultSet(0),randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),randint(0,100),
                              randint(0,100),randint(0,100),randint(0,100))
        self.graph_data.addElement(parsed)
        print("rand gen parsed!")
        self.root.after(500, self._randGenParsed)
    
    
    # def _makeLabel(self, parent, text):
    #     label = tk.Label(parent, text=text, bg="white", font=("Comic Sans MS", 16))
    #     return label

    def _box(self, parent, title_text, width=150, height = 120):
        """
        Makes a box. Can determine width and height.
        """
        frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
        frame.grid_propagate(False)
        label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
        label.pack(pady=5)
        return frame, label

dashboard = Dashboard()
dashboard.start()

# def box(parent, title_text, width=150, height = 120):
#     frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
#     frame.grid_propagate(False)
#     label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
#     label.pack(pady=5)
#     return frame, label

# def create_plot(parent, title):
#     fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
#     ax.plot([0, 1, 2, 3], [random.randint(0, 10) for _ in range(4)])
#     ax.set_title(title)

#     canvas = FigureCanvasTkAgg(fig, master=parent)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#     return canvas

# #left
# left_frame = tk.Frame(root, bg=background, width = 300)
# left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# left_frame.pack_propagate(False)
# #use matplotlib to create graph corresponding to each box on the left side
# #6 by 2 grid of boxes on the left side
# boxes = []
# for i in range(6):
#     for j in range(2):
#         box_frame, box_label = box(left_frame, f"Box {i*2 + j + 1}")
#         box_frame.grid(row=i, column=j, padx=3, pady=3)
#         left_frame.grid_rowconfigure(i, weight=1)
#         left_frame.grid_columnconfigure(j, weight=1)
#         boxes.append((box_frame, box_label))

# #right
# main_panel = tk.Frame(root, bg=background)
# main_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
# graph_frame = tk.Frame(main_panel, bg="white", borderwidth=7, relief=tk.SUNKEN)
# gps_frame = tk.Frame(main_panel, bg="lightgrey", borderwidth=7, relief=tk.SUNKEN)
# graph_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
# gps_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

# graph_frame, graph_label = box(graph_frame, "Graph Area", width = 1000, height = 600)
# gps_frame, gps_label = box(gps_frame, "GPS Data Area", width = 1000, height = 600)



# root.mainloop()
   



