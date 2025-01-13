import numpy as np
from .data_loader import load_coordinates, load_network

coordinates = load_coordinates()
network = load_network()
x_values = [c[0] for c in coordinates]
y_values = [c[1] for c in coordinates]
range_vec = np.array([max(x_values) - min(x_values), max(y_values) - min(y_values)])

### visualization related things
def interpolate_coordinates(start, end, num_points, add=np.array([0,0])):
    lon_values = np.linspace(start[0], end[0], num_points + 1)
    lon_values += add[0]
    lat_values = np.linspace(start[1], end[1], num_points + 1)
    lat_values += add[1]
    return list(zip(lon_values, lat_values))

def create_arc_coordinates():
    arc_coordinates = {}
    for i, connections in enumerate(network):
        for j, weight in connections:
            dx = coordinates[j][0] - coordinates[i][0]
            dy = coordinates[j][1] - coordinates[i][1]
            vec = np.array([-dy, dx], dtype='float64')
            vec /= np.linalg.norm(vec)
            vec *= np.linalg.norm(range_vec)/500
            if (i,j) in arc_coordinates:
                vec *= -1
            arc_coordinates[(i,j)] = [interpolate_coordinates(coordinates[i], coordinates[j], weight, add=vec)]
            arc_coordinates[(i,j)].append(interpolate_coordinates(coordinates[i], coordinates[j], weight, add=2*vec))
    return arc_coordinates
######
# Lane 0
# Lane 1: overpass
def create_arcs():
    arc_positions = {
        (i, j): [[""]*weight, [""]*weight]
        for i, arc in enumerate(network)
        for j, weight in arc
    }
    return arc_positions