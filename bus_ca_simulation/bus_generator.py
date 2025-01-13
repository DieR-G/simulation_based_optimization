from .bus_factory import BusFactory
import math
from .data_loader import load_network

network = load_network()

def generate_buses(routes, frequencies, capacity):
    buses = [[] for _ in range(len(routes))]
    for k in range(len(routes)):
        bus_factory = BusFactory(network, routes[k])
        bus_number = math.ceil(frequencies[k] * bus_factory.total_time / 30)
        time_delta = math.ceil(3600 / frequencies[k])
        start_time = 0
        for i in range(bus_number):
            new_bus = bus_factory.create_bus(str(k) + str(i),
                                             capacity, start_time)
            buses[k].append(new_bus)
            start_time += time_delta
    return buses

def generate_buses_test(routes):
    buses = [[]]
    bus_factory = BusFactory(network, routes[2], 2)
    buses[0].append(bus_factory.create_bus('1', 50, 479))
    buses[0].append(bus_factory.create_bus('2', 50, 478))
    buses[0].append(bus_factory.create_bus('3', 50, 477))
    buses[0].append(bus_factory.create_bus('4', 50, 476))
    buses[0].append(bus_factory.create_bus('5', 50, 475))
    buses[0].append(bus_factory.create_bus('6', 50, 474))
    return buses

def delay_bus(bus):
    bus.starting_time -= 1
    bus.starting_time %= 2*bus.total_time
    bus._set_position_at_time()

def free_platform_idx(platforms, node, route_idx, direction):
    idx = -1
    for t_idx, (can, route_set) in enumerate(platforms[node][direction]):
        if can and route_idx in route_set:
            return t_idx
    return idx

def generate_buses_on_space(routes, stops, bus_numbers, capacities, arcs, platforms):
    buses = [[] for _ in range(len(routes))]
    total_buses = 0
    for k in range(len(routes)):
        bus_factory = BusFactory(network, routes[k], stops[k], k)
        total_buses += bus_numbers[k]
        frequency = 30*60*bus_numbers[k]/bus_factory.total_time
        time_delta = math.ceil(3600 / frequency)
        start_time = 0
        for i in range(bus_numbers[k]):
            new_bus = bus_factory.create_bus(str(k) + str(i),
                                             capacities[k], start_time)
            current_arc = new_bus.get_arc()
            current_pos = new_bus.get_arc_position()
            lane = new_bus.lane
            delay = 0
            
            platform_direction = lambda x: 0 if x == 1 else 1

            platform_idx = lambda platforms, node, route_idx, direction: next((t_idx for t_idx, (can, route_set) in enumerate(platforms[node][direction]) if can and route_idx in route_set), -1)    
            bus_platform_idx = platform_idx(platforms, new_bus.current_node, new_bus.route_id, platform_direction(new_bus.direction))
            while(arcs[current_arc][lane][current_pos] != "" or (new_bus.state == 'on_station' and bus_platform_idx == -1)):
                delay += 1
                new_bus = bus_factory.create_bus(str(k) + str(i), capacities[k], start_time - delay)
                current_arc = new_bus.get_arc()
                current_pos = new_bus.get_arc_position()
                bus_platform_idx = platform_idx(platforms, new_bus.current_node, new_bus.route_id, platform_direction(new_bus.direction))
                        
            if new_bus.state == 'on_station':
                platforms[new_bus.current_node][platform_direction(new_bus.direction)][bus_platform_idx][0] = False
                new_bus.platform_idx = bus_platform_idx
                
            arcs[current_arc][lane][current_pos] = new_bus.id
            buses[k].append(new_bus)
            start_time += time_delta
        buses[k].sort(key = lambda b: b.position if b.direction > 0 else 2*b.total_time - b.position)
        
        for j in range(len(buses[k])):
            buses[k][j].bus_ahead = buses[k][(j+1)%len(buses[k])]
    #print(f"Total buses: {total_buses}")
    return buses