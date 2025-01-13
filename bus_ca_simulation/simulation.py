from .bus_generator import generate_buses_on_space
from .passenger_generator import generate_passengers
from .platform_generator import generate_platforms
from .logger import save_state_data, save_to_csv, save_arcflows, get_max_arcflow
import datetime
import itertools
import statistics
from . import data_loader
from . import arc_manager

TIMEOUT = 43200

class Simulation:
    def __init__(self):
        # Load global data
        self.coordinates = data_loader.load_coordinates()
        self.network = data_loader.load_network()
        self.arc_positions = arc_manager.create_arcs()
        self.arc_coordinates = arc_manager.create_arc_coordinates()

        # Constants
        self.STATION_NUMBER = len(self.network)
        self.MAX_TIME_SIMULATED = 50000
        self.TRANSFER_TIME = 5 * 60
        self.platforms = []
        self.reset()

    def reset(self):
        # Initialize/reset variables
        self.bus_positions = []
        self.bus_occupancies = []
        self.bus_speeds = []
        self.route_slowest_arc = []
        self.route_bus_number = []
        self.arc_people_count = {(i, j): [] for i, l in enumerate(self.network) for j, _ in l}
        self.passengers_at_time = [0] * self.MAX_TIME_SIMULATED
        self.stations = [set() for _ in range(self.STATION_NUMBER)]

    def generate_entities(self, network_routes, network_stops, network_platforms, bus_numbers, capacities):
        self.platforms = generate_platforms(self.STATION_NUMBER, network_platforms)
        self.passengers = generate_passengers(network_routes, network_stops, self.stations, self.passengers_at_time)
        self.bus_routes = generate_buses_on_space(
            network_routes, network_stops, bus_numbers, capacities, self.arc_positions, self.platforms
        )
        self.passengers_pref_time = list(itertools.accumulate(self.passengers_at_time))
        self.bus_occupancies = [[] for _ in self.bus_routes]
        self.bus_speeds = [[] for _ in self.bus_routes]
        self.route_slowest_arc = [[] for _ in self.bus_routes]
        self.route_bus_number = [len(route) for route in self.bus_routes]

    def update_bus_status(self, bus_capacities, time, on_bus, t_time):
        current_positions = []
        for route_idx, route in enumerate(self.bus_routes):
            total_occupancy = 0
            total_speed = 0
            route_arcs = {}
            for bus_idx, bus in enumerate(route):
                total_occupancy += bus_capacities[route_idx] - bus.capacity
                total_speed += bus.get_last_avg_speed()
                alighted_passengers, transfered_passengers, new_passengers = bus.move(
                    self.arc_positions, self.stations, self.passengers, self.platforms, time
                )
                on_bus -= alighted_passengers
                t_time += self.TRANSFER_TIME * transfered_passengers
                on_bus += new_passengers
                current_arc = bus.get_arc()

                if current_arc in route_arcs:
                    xn, n = route_arcs[current_arc][0], route_arcs[current_arc][1]
                    route_arcs[current_arc][0] = xn + (bus.get_last_avg_speed() - xn) / n
                    route_arcs[current_arc][1] += 1
                else:
                    route_arcs[current_arc] = [bus.get_last_avg_speed(), 1]

                if bus.previous_state and bus.previous_state["arc"] != current_arc:
                    self.arc_people_count[current_arc].append((time, bus_capacities[route_idx] - bus.capacity))

                if bus.state == 'on_station':
                    current_positions.append(self.coordinates[bus.current_node])
                else:
                    pos = bus.get_arc_position()
                    lane = bus.lane
                    current_positions.append(self.arc_coordinates[current_arc][lane][pos])

            min_val = 1000
            min_arc = (0, 0)
            for arc, speed in route_arcs.items():
                if speed[0] < min_val:
                    min_val = speed[0]
                    min_arc = arc

            self.bus_occupancies[route_idx].append(
                total_occupancy / (bus_capacities[route_idx] * self.route_bus_number[route_idx])
            )
            self.bus_speeds[route_idx].append(total_speed / self.route_bus_number[route_idx])
            self.route_slowest_arc[route_idx].append((min_val, min_arc))

        self.bus_positions.append(current_positions)
        return on_bus, t_time

    def update_times(self, on_bus, time, n, w_time, inv_time):
        inactives = n - len(self.passengers)
        w_time += self.passengers_pref_time[time] - on_bus - inactives
        inv_time += on_bus
        return w_time, inv_time

    def run_simulation(self, network_routes, network_stops, network_platforms, bus_numbers, capacities, visualize=False, save_metrics=False):
        self.reset()
        self.generate_entities(network_routes, network_stops, network_platforms, bus_numbers, capacities)
        n = len(self.passengers)
        inv_time, t_time, w_time, on_bus = 0, 0, 0, 0
        time = 0

        while len(self.passengers) > 0:
            on_bus, t_time = self.update_bus_status(capacities, time, on_bus, t_time)
            w_time, inv_time = self.update_times(on_bus, time, n, w_time, inv_time)
            time += 1
            if time >= TIMEOUT:
                print("TIMEOUT")
                break
            if save_metrics:
                save_state_data(self.bus_routes, time, capacities)

        if save_metrics:
            save_to_csv()
            save_arcflows(self.arc_people_count, f"results/flow_data_{data_loader.INSTANCE_NAME}.csv", 24)

        if visualize:
            from .visualization import visualize_simulation
            visualize_simulation(
                self.bus_positions, self.bus_routes, self.coordinates, self.network, self.bus_occupancies,
                self.bus_speeds, self.route_slowest_arc, skip_frames=1
            )

    def evaluate(self, network_routes, network_stops, network_platforms, bus_numbers, capacities):
        self.reset()
        self.generate_entities(network_routes, network_stops, network_platforms, bus_numbers, capacities)
        n = len(self.passengers)
        inv_time, t_time, w_time, on_bus = 0, 0, 0, 0
        time = 0
        #print(len(self.passengers), time)
        while len(self.passengers) > 0:
            on_bus, t_time = self.update_bus_status(capacities, time, on_bus, t_time)
            w_time, inv_time = self.update_times(on_bus, time, n, w_time, inv_time)
            time += 1
            if time >= TIMEOUT:
                break
            #print(len(self.passengers))
        return (
            time < TIMEOUT,
            time, inv_time // 60, w_time // 60, t_time // 60,
            (inv_time + w_time + t_time) // 60, get_max_arcflow(self.arc_people_count, 24),
            [statistics.mean(o) for o in self.bus_occupancies]
        )
