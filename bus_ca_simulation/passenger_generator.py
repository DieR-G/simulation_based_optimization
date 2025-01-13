from .route_assignation import get_travel_routes
from .data_loader import load_demand_matrix
import math

demand_matrix = load_demand_matrix()

start_time_matrix = []

class Passenger:
    def __init__(self, id, arrival_time, travel_path, start_station, end_station):
        self.id = id
        self.active = True
        self.arrival_time = arrival_time
        self.path=travel_path
        self.path_pos = len(self.path) - 1
        self.current_bus="-1"
        self.start_station = start_station
        self.current_station= self.start_station
        self.end_station = end_station
    def __str__(self):
        str = f"Active: {self.active}\nArrival time: {self.arrival_time}\nStarting Node: {self.start_station}\nEnding Node: {self.end_station}\nNodes: {list(reversed(self.path))}"
        return str
    
    def __eq__(self, other):
        if not isinstance(other, Passenger):
            return NotImplemented
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)

def generate_passengers_test(routes, stops, stations_set, passengers_at_time):
    for i in range(len(demand_matrix)):
        for j in range(len(demand_matrix)):
            demand_matrix[i][j] = 0
    demand_matrix[40][17] = 33
    demand_matrix[17][38] = 33
    demand_matrix[38][28] = 33

    passenger_set = set()
    travels = get_travel_routes(routes, stops)
    pass_idx = 0
    for i in range(len(demand_matrix)):
        for j in range(len(demand_matrix)):
            if len(travels[i][j]) == 0:
                continue
            if demand_matrix[i][j] == 0:
                continue
            total_users = int(demand_matrix[i][j])
            arriving_time = 0
            for k in range(total_users):
                passengers_at_time[int(arriving_time)] += 1
                assert(int(arriving_time) < 3600)
                new_passenger = Passenger(pass_idx, int(arriving_time), travels[i][j][k%len(travels[i][j])], i, j)
                stations_set[i].add(new_passenger)
                passenger_set.add(new_passenger)
                pass_idx += 1
    
    return passenger_set

def generate_passengers(routes, stops, stations_set, passengers_at_time):
    passenger_set = set()
    travels = get_travel_routes(routes, stops)
    pass_idx = 0
    for i in range(len(demand_matrix)):
        for j in range(len(demand_matrix)):
            if len(travels[i][j]) == 0:
                continue
            if demand_matrix[i][j] == 0:
                continue
            total_users = int(demand_matrix[i][j])
            arriving_time = 0
            dt = 3600/demand_matrix[i][j]
            for k in range(total_users):
                passengers_at_time[int(arriving_time)] += 1
                assert(int(arriving_time) < 3600)
                new_passenger = Passenger(pass_idx, int(arriving_time), travels[i][j][k%len(travels[i][j])], i, j)
                stations_set[i].add(new_passenger)
                passenger_set.add(new_passenger)
                arriving_time += dt
                pass_idx += 1
    
    return passenger_set