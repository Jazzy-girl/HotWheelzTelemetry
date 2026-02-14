"""
Authors: Ryanne Wilson

Car-side GUI, using Raspberry Pi.
Displays:
    - Backup camera
    - Speed
    - Cockpit temperature
    - Car battery
    - Faults (if active)
        - Low Cell Voltage
        - Current Sensor
        - Pack Voltage Sensor
        - Thermistor

Functionality:
    - User can touch the screen to minize/fullscreen the backup camera
"""
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from Pit.packet import ParsedPacket

root = tk.Tk()
root.title("Dashboard")
background = "black"
root.geometry("1200x800")
root.state('zoomed')

def box(parent, title_text, width=150, height = 120):
    frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
    frame.grid_propagate(False)
    label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
    label.pack(pady=5)
    return frame, label

def create_plot(parent, title):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    ax.plot([0, 1, 2, 3], [random.randint(0, 10) for _ in range(4)])
    ax.set_title(title)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas

#left
left_frame = tk.Frame(root, bg=background, width = 300)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
left_frame.pack_propagate(False)
#use matplotlib to create graph corresponding to each box on the left side
#6 by 2 grid of boxes on the left side
boxes = []
for i in range(6):
    for j in range(2):
        box_frame, box_label = box(left_frame, f"Box {i*2 + j + 1}")
        box_frame.grid(row=i, column=j, padx=3, pady=3)
        left_frame.grid_rowconfigure(i, weight=1)
        left_frame.grid_columnconfigure(j, weight=1)
        boxes.append((box_frame, box_label))

#right
main_panel = tk.Frame(root, bg=background)
main_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
graph_frame = tk.Frame(main_panel, bg="white", borderwidth=7, relief=tk.SUNKEN)
gps_frame = tk.Frame(main_panel, bg="lightgrey", borderwidth=7, relief=tk.SUNKEN)
graph_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
gps_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

graph_frame, graph_label = box(graph_frame, "Graph Area", width = 1000, height = 600)
gps_frame, gps_label = box(gps_frame, "GPS Data Area", width = 1000, height = 600)



root.mainloop()
   