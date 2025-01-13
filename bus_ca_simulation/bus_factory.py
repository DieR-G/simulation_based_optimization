from .bus_class import Bus
from .route_assignation import compute_time

class BusFactory:
    def __init__(self, network, route, stops, route_id):
        self.network = network
        self.route = route
        self.stops = stops
        self.route_id = route_id
        self.total_time = compute_time(self.route[0], self.route[-1], self.route)

    def node_at_time(self):
        node_time_map = {}
        index_time_list = [0] * len(self.route)
        current_node = self.route[0]
        t = 0
        for idx, node in enumerate(self.route):
            t += next((c for a, c in self.network[node] if a == current_node), 0)
            node_time_map[t] = node
            index_time_list[idx] = t
            current_node = node
        return node_time_map, index_time_list

    def create_bus(self, id, capacity, starting_time):
        node_time_map, index_time_list = self.node_at_time()
        return Bus(id, self.route, self.stops, self.route_id, capacity, starting_time, self.total_time, node_time_map, index_time_list)
