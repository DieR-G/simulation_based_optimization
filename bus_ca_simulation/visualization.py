import matplotlib.pyplot as plt
import matplotlib.animation as animation

def visualize_simulation(bus_positions, bus_routes, coordinates, network, occupancies, speeds, slowest_arcs, skip_frames=1):
    fig, ax = plt.subplots()
    min_x_val, max_x_val = min([c[0] for c in coordinates]), max([c[0] for c in coordinates])
    min_y_val, max_y_val = min([c[1] for c in coordinates]), max([c[1] for c in coordinates])
    ax.set_xlim(min_x_val - (max_x_val-min_x_val)/10, max_x_val + (max_x_val-min_x_val)/10)
    ax.set_ylim(min_y_val - (max_y_val-min_y_val)/10, max_y_val + (max_y_val-min_y_val)/10)

    # Plot network connections
    for i, connections in enumerate(network):
        for j, _ in connections:
            start = coordinates[i]
            end = coordinates[j]
            ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', lw=0.5)

    # Define custom colors for the routes
    custom_colors = ['blue', 'orange', 'magenta', 'purple']

    # Create bus markers for each route
    buses = []
    for route_index, route in enumerate(bus_routes):
        route_color = custom_colors[route_index % len(custom_colors)]
        route_buses = [ax.plot([], [], 'o', color=route_color, markersize=2)[0] for _ in route]
        buses.extend(route_buses)

    # Create station markers
    stations = ax.scatter([c[0] for c in coordinates], [c[1] for c in coordinates], 
                          marker='s', color='red', s=10, zorder=10)

    for i, (x, y) in enumerate(coordinates):
        ax.text(x, y, str(i), fontsize=8, ha='right', va='bottom')
    
    # Text annotations for occupancies and speeds
    occupancy_texts = []
    speed_texts = []
    time_texts = []
    slowest_texts = []
    for i in range(len(bus_routes)):
        occupancy_text = ax.text(0.02, 0.95 - i * 0.15, '', transform=ax.transAxes, fontsize=8, color=custom_colors[i % len(custom_colors)])
        occupancy_texts.append(occupancy_text)
        speed_text = ax.text(0.02, 0.90 - i * 0.15, '', transform=ax.transAxes, fontsize=8, color=custom_colors[i % len(custom_colors)])
        speed_texts.append(speed_text)
        slowest_text = ax.text(0.02, 0.85 - i*0.15, '', transform=ax.transAxes, fontsize=8, color=custom_colors[i % len(custom_colors)])
        slowest_texts.append(slowest_text)
        time_text = ax.text(0.8, i * 0.15, '', transform=ax.transAxes, fontsize=8, color='black')
        time_texts.append(time_text)
    def init():
        for bus in buses:
            bus.set_data([], [])
        for occupancy_text in occupancy_texts:
            occupancy_text.set_text('')
        for speed_text in speed_texts:
            speed_text.set_text('')
        for slowest_text in slowest_texts:
            slowest_text.set_text('')
        return buses + [stations] + occupancy_texts + speed_texts + slowest_texts

    def update(frame):
        positions = bus_positions[frame * skip_frames]
        for bus, pos in zip(buses, positions):
            bus.set_data([pos[0]], [pos[1]])

        # Update occupancy and speed texts
        for i, (occupancy_text, speed_text, slowest_text) in enumerate(zip(occupancy_texts, speed_texts, slowest_texts)):
            occupancy_text.set_text(f'Route {i+1} Occupancy: {round(100*occupancies[i][frame * skip_frames])}%')
            speed_text.set_text(f'Route {i+1} Avg Speed: {speeds[i][frame * skip_frames]:.2f} km/h')
            slowest_text.set_text(f'Route {i+1} Slowest Arc:{slowest_arcs[i][frame*skip_frames][1]} at {slowest_arcs[i][frame*skip_frames][0]} km/h')
        minutes, seconds = divmod(frame*skip_frames, 60)
        hours, minutes = divmod(minutes, 60)
        time_text.set_text(f'Time (hh:mm:ss): {int(hours):02}:{int(minutes):02}:{int(seconds):02}')
        # Redraw stations on top
        stations.set_offsets(coordinates)

        return buses + [stations] + occupancy_texts + speed_texts + slowest_texts + [time_text]

    ani = animation.FuncAnimation(
        fig, update, frames=range(0, len(bus_positions) // skip_frames), init_func=init,
        blit=True, interval=30, repeat=False
    )
    plt.show()