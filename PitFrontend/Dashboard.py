import tkinter as tk
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time

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
Dashboard
"""
class Dashboard:
    root = tk.Tk()
    root.title("Dashboard")
    background = "black"
    root.geometry("1200x800")
    root.state('zoomed')

    def __init__(self) -> None:
        # Field Frame
        self.field_frame = tk.Frame(self.root, bg=self.background, width = 300)
        self.field_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.field_frame.pack_propagate(False)

        # make field labels
        self.field_label = self._makeLabel(self.field_frame, "Fields").grid
        self.field_value = self._makeLabel(self.field_frame, "Values")

    
    def _makeLabel(self, parent, text):
        label = tk.Label(parent, text=text, bg="white", font=("Comic Sans MS", 16))
        return label

    def _box(self, parent, title_text, width=150, height = 120):
        frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, width=width, height=height, borderwidth=5)
        frame.grid_propagate(False)
        label = tk.Label(frame, text=title_text, bg="white", font=("Comic Sans MS", 16))
        label.pack(pady=5)
        return frame, label

    def _create_plot(self, parent, title):
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.plot([0, 1, 2, 3], [random.randint(0, 10) for _ in range(4)])
        ax.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas





#use matplotlib to create graph corresponding to each box on the left side
#6 by 2 grid of boxes on the left side
boxes = []
for i in range(6):
    for j in range(2):
        box_frame, box_label = box(field_frame, f"Box {i*2 + j + 1}")
        box_frame.grid(row=i, column=j)
        # field_frame.grid_rowconfigure(i, weight=1)
        # field_frame.grid_columnconfigure(j, weight=1)
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
   

