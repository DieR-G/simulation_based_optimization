import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import data_loader
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Load coordinates and network
coordinates = data_loader.load_coordinates()
network = data_loader.load_network()

# Create arcs from the network data
arcs = [(i, j) for i, l in enumerate(network) for j, _ in l]

# Create an undirected graph object
G = nx.Graph()

# Add nodes with positions
for i, coord in enumerate(coordinates):
    G.add_node(i, pos=coord)

# Add edges
G.add_edges_from(arcs)

# Get positions of nodes
pos = nx.get_node_attributes(G, 'pos')
csv_file_path = 'results/bus_data.csv'
df = pd.read_csv(csv_file_path)

# Group by 'time' and 'arc', then sum the 'passenger_count'
df['arc'] = df['arc'].apply(eval)  # Convert string representation of tuple to actual tuple
result = df.groupby(['time', 'arc'])['passenger_count'].sum().reset_index()

# Extract unique times for animation frames
times = sorted(result['time'].unique())

# Define the custom color map (light blue to red)
colors = [(0.678, 0.847, 0.902), (1, 0, 0)]  # Light blue to red
n_bins = 100  # Discretize the interpolation into bins
cmap_name = 'lightblue_red'
cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
norm = plt.Normalize(vmin=result['passenger_count'].min(), vmax=result['passenger_count'].max())

# Create the plot
fig, ax = plt.subplots(figsize=(10, 8))
nx.draw(G, pos, ax=ax, node_size=10, edge_color='gray', with_labels=False)

def update(num):
    ax.clear()
    nx.draw(G, pos, ax=ax, node_size=10, edge_color='gray', with_labels=False)

    time = times[num]
    subset = result[result['time'] == time]

    # Convert subset arcs to a set for faster lookup
    subset_arcs = {tuple(arc) for arc in subset['arc']}
    edge_colors = []

    for arc in arcs:
        if arc in subset_arcs:
            passenger_count = subset[subset['arc'] == arc]['passenger_count'].values[0]
        else:
            passenger_count = 0
        edge_colors.append(cmap(norm(passenger_count)))
    
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=arcs, edge_color=edge_colors, width=2.0)
    
    # Convert time to hh:mm:ss format
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'
    ax.set_title(f'Time: {time_str}')
    ax.set_axis_off()

# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Only needed for matplotlib < 3.1
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('Passenger Count')

ani = animation.FuncAnimation(fig, update, frames=len(times), interval=1, repeat=False)
plt.show()
