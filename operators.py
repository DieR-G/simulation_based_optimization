from heuristics import get_stations_mapper, distribute_doors, random_weighted_stops, create_gap_stops, demand_matrix
import random
from random import shuffle
from collections import deque

def get_i_mapper():
    mapper = get_stations_mapper()
    imapper = [0]*len(mapper)
    for i in mapper:
        imapper[mapper[i]] = i
    return imapper

def delete_random_stop(route_, stops_):
    imapper = get_i_mapper()
    to_delete = len(stops_)-1
    deleted_node = stops_[to_delete]
    route, stops = [], []
    for node in stops_:
        if deleted_node == node:
            continue
        stops.append(node)
    
    if to_delete == 0 or to_delete == len(stops_)-1:
        if to_delete == 0:
            #route = route_[1:]
            route = [i for i in route_ if imapper[i] >= imapper[stops[0]]]
        else:
            route = route_[:to_delete]
            route = [i for i in route_ if imapper[i] <= imapper[stops[-1]]]
    else:
        route = route_[:]
    return deleted_node, route, stops

def add_random_stop(route_, stops_):
    imapper = get_i_mapper()
    mapper = get_stations_mapper()
    base_nodes = [imapper[i] for i in route_]
    base_stops = [imapper[i] for i in stops_]
    remaining = list(set(range(len(imapper))) - set(base_stops))
    shuffle(remaining)
    if len(remaining) == 0:
        return
    to_add = random.randint(0, len(remaining) - 1)
    new_node = remaining[to_add]
    route, stops = [i for i in base_nodes], []
    for i in range(len(base_stops)-1):
        stops.append(base_stops[i])
        if base_stops[i] < new_node and new_node < base_stops[i+1]:
            stops.append(new_node)
            
    stops.append(base_stops[-1])
    if new_node > base_stops[-1]:
        for i in range(base_stops[-1], new_node + 1):
            route.append(i)
        base_stops.append(new_node)
    route = [mapper[i] for i in route]
    stops = [mapper[i] for i in stops]
    return mapper[new_node], route, stops

def reduce_frequency(frequencies, index):
    if frequencies[index] > 20:
        frequencies[index] -= 20

def increase_frequency(frequencies, index):
    frequencies[index] += 20
    

def add_route(solution, gap = 0, bus_number = 40, capacity = 250):
    n = len(demand_matrix)
    mapper = get_stations_mapper()
    new_route = list(range(n))
    imapper = get_i_mapper()
    if gap == 0:
        new_stops = random_weighted_stops()
    else:
        new_stops = create_gap_stops(gap)
    new_route = [mapper[i] for i in new_route]
    new_stops = [mapper[i] for i in new_stops]
    solution.routes.append(new_route)
    solution.stops.append(new_stops)
    solution.frequencies.append(bus_number)
    solution.capacities.append(capacity)
    solution.bus_number += bus_number
    solution.route_number += 1
    idx = len(solution.routes) - 1
    for s in new_stops:
        solution.route_map[s].append(idx)
        platform_number = 20 if imapper[s] == 0 or imapper[s] == n-1 else 6
        temp = distribute_doors(solution.route_map[s],solution.frequencies, platform_number)
        solution.platforms[s] = [val for val in temp]
        