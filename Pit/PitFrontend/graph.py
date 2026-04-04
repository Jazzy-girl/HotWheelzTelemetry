"""
Graph file
Author: Ryanne Wilson
"""
import matplotlib.pyplot as plt
import numpy as np

def make_graph(title: str, ylabel: str, data: list):
    """
    Takes in a set of data like [ (x,y), (x,y) ...]

    """
    x = []
    y = []
    for coord in data:
        # coord = (x, y)
        x.append(coord[0])
        y.append(coord[1])
    
    x_points = np.array(x)
    y_points = np.array(y)

    plt.title(title)
    plt.xlabel("time")
    plt.ylabel(ylabel)
    plt.plot(x_points,y_points)
    plt.grid()
    plt.show()

coords = (
    (1,1),
    (2,2),
    (3,3),
    (5,5),
    (-3,2),
    (6,-1),
)

make_graph("title", "nums", coords)

