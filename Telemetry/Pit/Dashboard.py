from Telemetry.Pit.GraphData import *
from Telemetry.Pit.Graph import Graph
from Telemetry.packet import ParsedPacket, FaultSet

import tkinter as tk
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from random import randint



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
class Dashboard:
    root = tk.Tk()
    root.title("Dashboard")
    background = "black"
    root.geometry("1200x800")
    root.state('zoomed')
    MAX_ELEMENTS = 30

    def _makeFrame(self, parent, bg, side):
        frame = tk.Frame(parent, bg=bg)
        frame.pack(side=side, expand=True, fill=tk.BOTH)
        return frame
    
    def __init__(self) -> None:
        self.main_panel = tk.Frame(self.root, bg=self.background)
        self.main_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.right_frame = self._makeFrame(self.main_panel, self.background, tk.RIGHT)

        # Field Frame
        self.field_frame = tk.Frame(self.main_panel, bg=self.background, width = 300)
        self.field_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.field_frame.pack_propagate(False)

        # make field labels
        self.field_label = self._makeLabel(self.field_frame, "Fields").grid
        self.field_value = self._makeLabel(self.field_frame, "Values")

        # graph frame
        self.graph_frame = tk.Frame(self.right_frame, bg="white", borderwidth=7, relief=tk.SUNKEN)
        self.graph_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.graph_label = tk.Label(self.graph_frame, text="GRAPH", bg="white", font=("Comic Sans MS", 16))
        self.graph_label.pack()
        # self.graph_frame, self.graph_label = self._box(self.graph_frame, "Graph Area", width = 1000, height = 600)

        self.parsedPackets: deque[ParsedPacket]
        self.parsedPackets = deque()

        self.graph_data = GraphDataCockpit(self.parsedPackets, self.MAX_ELEMENTS)
        self.graph = Graph(self.graph_data, self.graph_frame, self.root, self.MAX_ELEMENTS)

        # map frame
        self.map_frame = self._makeFrame(self.right_frame, "white", tk.BOTTOM)
        
        
    
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
    
    
    def _makeLabel(self, parent, text):
        label = tk.Label(parent, text=text, bg="white", font=("Comic Sans MS", 16))
        return label

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
   



