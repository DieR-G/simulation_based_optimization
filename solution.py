import copy

class Solution:
    def __init__(self, routes, stops, frequencies, capacities, platforms, route_map):
        self.routes = copy.deepcopy(routes)
        self.stops = copy.deepcopy(stops)
        self.frequencies = copy.deepcopy(frequencies)
        self.capacities = copy.deepcopy(capacities)
        self.platforms = copy.deepcopy(platforms)
        self.route_map = copy.deepcopy(route_map)
        self.bus_number = sum(self.frequencies)
        self.route_number = len(self.routes)
        self.stations_number = len(self.platforms)
        self.total_time = int(1e18)
        self.value = int(1e18)
    
    def __deepcopy__(self, memo):
        # Create a deep copy of the instance
        copied_obj = Solution(
            copy.deepcopy(self.routes, memo),
            copy.deepcopy(self.stops, memo),
            copy.deepcopy(self.frequencies, memo),
            copy.deepcopy(self.capacities, memo),
            copy.deepcopy(self.platforms, memo),
            copy.deepcopy(self.route_map, memo)
        )
        # Copy additional attributes manually
        copied_obj.route_number = self.route_number
        copied_obj.stations_number = self.stations_number
        copied_obj.total_time = self.total_time
        copied_obj.value = copy.deepcopy(self.value, memo)
        return copied_obj

    def get_vals(self):
        return (self.routes, self.stops, self.platforms, self.frequencies, self.capacities)
