from collections import deque
from typing import Any
from GraphData import GraphDataInterface
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
import tkinter as tk
class Graph:

    def __init__(self, input: GraphDataInterface, container) -> None:
        self.input = input
        self.line: Line2D
        self.container = container
        self.ax: Axes

    def update(self):
        self.ax.clear()
        self.ax.plot(self.input.getData())
        # self.line.set_ydata(list(self.input.getData()))
        # return self.line,

    def start(self):
        """Create the graph"""
        fig = Figure() #figsize (,) in inches; dpi dots/inch
        self.ax = fig.add_subplot()
        self.line, = self.ax.plot(self.input.getData())

        self.canvas = FigureCanvasTkAgg(fig, master=self.container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ani = FuncAnimation(fig, self.update, interval=50, blit=True)
        # plt.show()
        # ax.set_ylim(#,#)
    
    def setInput(self, input: GraphDataInterface):
        self.input = input
    



