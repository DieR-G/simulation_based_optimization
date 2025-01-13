import bus_ca_simulation.data_loader as data_loader
from functools import cmp_to_key
import numpy as np

demand_matrix = data_loader.load_demand_matrix()

def get_stations_mapper():
    coordinates = data_loader.load_coordinates()
    mapper = [i for i in range(len(coordinates))]
    mapper = sorted(mapper, key=cmp_to_key(lambda a, b: (coordinates[a][0] > coordinates[b][0]) - (coordinates[a][0] < coordinates[b][0])))
    return mapper
    

def relabel_graph():
    graph = data_loader.load_network()
    routes = data_loader.load_routes()
    stops = data_loader.load_stops()
    coordinates = data_loader.load_coordinates()
    #print(sorted(coordinates))
    relabeled_matrix = [[0 for _ in row] for row in demand_matrix]
    relabeled_graph = [[] for _ in range(len(graph))]
    relabeled_routes = [[0 for _ in route] for route in routes]
    relabeled_stops = [[0 for _ in stop] for stop in stops]
    coordinates = data_loader.load_coordinates()
    mapper = [i for i in range(len(graph))]
    mapper = sorted(mapper, key=cmp_to_key(lambda a, b: (coordinates[a][0] > coordinates[b][0]) - (coordinates[a][0] < coordinates[b][0])))
    inverse = [0] * len(mapper)
    for i, v in enumerate(mapper):
        inverse[v] = i
    for node, adj_list in enumerate(graph):
        new_node = inverse[node]
        for x, w in adj_list:
            relabeled_graph[new_node].append([inverse[x], w])
            
    for i in range(len(demand_matrix)):
        for j in range(len(demand_matrix)):
            relabeled_matrix[i][j] = demand_matrix[mapper[i]][mapper[j]]
            
    for i, route in enumerate(routes):
        for j, node in enumerate(route):
            relabeled_routes[i][j] = inverse[node]
            
    for i, stop in enumerate(stops):
        for j, node in enumerate(stop):
            relabeled_stops[i][j] = inverse[node]
    
    return relabeled_graph, relabeled_matrix, relabeled_routes, relabeled_stops
            

def create_gap_stops(gap):
    n = len(demand_matrix)
    route = [i*gap for i in range(0, (n-2)//gap + 1)]
    if route[-1] < n - 1:
        route.append(n - 1)
    return route

def random_weighted_stops():
    n = len(demand_matrix)
    _demand_matrix = np.array(demand_matrix)
    weighted_nodes = np.sum(_demand_matrix, axis=0)
    p = 1/np.max(weighted_nodes)
    route = [i for i in range(n) if np.random.rand() < weighted_nodes[i]*p]
    if route[0] > 0:
        route.insert(0, 0)
    if route[-1] < n-1:
        route.append(n-1)
    return route

def get_min_frequency(route, stops, capacity):
    n = len(route)
    arcs_forward, arcs_backward = [0] * n, [0] * n
    for i in stops:
        for j in stops:
            if(i == j):
                continue
            if i < j:
                arcs_forward[i] += demand_matrix[i][j]
                arcs_forward[j] -= demand_matrix[i][j]
            else:
                arcs_backward[n-i-1] += demand_matrix[i][j]
                arcs_backward[n-j-1] -= demand_matrix[i][j]
    for i in range(1, len(arcs_forward)):
        arcs_forward[i] += arcs_forward[i-1]
    for i in range(1, len(arcs_forward)):
        arcs_forward[i] += arcs_forward[i-1]
    return max(max(arcs_forward), max(arcs_backward)) // (7 * capacity)

def distribute_doors(routes, frequencies, total_doors):
    total_frequency = sum([frequencies[r] for r in routes])
    weights = [freq / total_frequency for freq in frequencies]

    num_routes = len(routes)
    allocation = [1] * num_routes
    remaining_doors = total_doors - num_routes

    if remaining_doors <= 0:
        result = [[route] for route, count in zip(routes, allocation) for _ in range(count)]
        # Not enough doors for extra allocation
        return result

    fractional_parts = []
    for i in range(num_routes):
        extra_doors = weights[i] * remaining_doors
        allocation[i] += int(extra_doors) 
        fractional_parts.append((extra_doors - int(extra_doors), i))

    remaining_doors -= sum(int(weights[i] * remaining_doors) for i in range(num_routes))
    fractional_parts.sort(reverse=True, key=lambda x: x[0]) 

    for _, i in fractional_parts[:remaining_doors]:
        allocation[i] += 1  # Assign remaining doors based on largest fractional parts
    result = [[route] for route, count in zip(routes, allocation) for _ in range(count)]
    return result

def generate_direct_solution(bus_number = 600):
    n = len(demand_matrix)
    routes, stops, frequencies, capacities, platforms = [], [], [], [], []
    platforms = [[] for _ in range(n)]
    routes.append(list(range(n)))
    stops.append(list(range(n)))
    frequencies.append(bus_number)
    capacities.append(160)
    mapper = get_stations_mapper()
    route_map = [[] for _ in range(n)]
    for i, stops_ in enumerate(stops):
        for stop in stops_:
            route_map[mapper[stop]].append(i)
    TERMINAL_PLATFORM_NUMBER = 20
    PLATFORM_NUMBER = 6
    temp = distribute_doors(route_map[mapper[0]], frequencies, TERMINAL_PLATFORM_NUMBER)
    platforms[mapper[0]] = [val for val in temp]
    for i in range(1, n-1):
        temp = distribute_doors(route_map[mapper[i]], frequencies, PLATFORM_NUMBER)
        platforms[mapper[i]] = [val for val in temp]
    temp = distribute_doors(route_map[mapper[n-1]], frequencies, TERMINAL_PLATFORM_NUMBER)
    platforms[mapper[n-1]] = [val for val in temp]
    routes = [[mapper[x] for x in r] for r in routes]
    stops = [[mapper[x] for x in s] for s in stops]
    return routes, stops, frequencies, capacities, platforms, route_map

def generate_initial_solution():
    n = len(demand_matrix)
    routes, stops, frequencies, capacities, platforms = [], [], [], [], []
    platforms = [[] for _ in range(n)]
    routes.append(list(range(n)))
    stops.append(list(range(n)))
    frequencies.append(300)
    capacities.append(160)
    mapper = get_stations_mapper()
    for i in range(2,7):
        routes.append(list(range(n)))
        stops.append(create_gap_stops(i))
        frequencies.append(50)
        capacities.append(250)
    for i in range(1):
        routes.append(list(range(n)))
        stops.append(random_weighted_stops())
        frequencies.append(50)
        capacities.append(250)
    route_map = [[] for _ in range(n)]
    for i, stops_ in enumerate(stops):
        for stop in stops_:
            route_map[mapper[stop]].append(i)
    TERMINAL_PLATFORM_NUMBER = 20
    PLATFORM_NUMBER = 6
    temp = distribute_doors(route_map[mapper[0]], frequencies, TERMINAL_PLATFORM_NUMBER)
    platforms[mapper[0]] = [val for val in temp]
    for i in range(1, n-1):
        temp = distribute_doors(route_map[mapper[i]], frequencies, PLATFORM_NUMBER)
        platforms[mapper[i]] = [val for val in temp]
    temp = distribute_doors(route_map[mapper[n-1]], frequencies, TERMINAL_PLATFORM_NUMBER)
    platforms[mapper[n-1]] = [val for val in temp]
    routes = [[mapper[x] for x in r] for r in routes]
    stops = [[mapper[x] for x in s] for s in stops]
    return routes, stops, frequencies, capacities, platforms, route_map
    

#g, m, r, s = relabel_graph()
#print(g)
#print(m)
#print(r)
#print(s)
#print(c)

#routes, stops, frequencies, capacities, platforms = generate_initial_solution()

#print(platforms)

#mapper = get_stations_mapper()
#for i in range(len(routes)):
#    routes[i] = list(map(lambda x: mapper[x], routes[i]))
#    stops[i] = list(map(lambda x: mapper[x], stops[i]))
#    print(routes[i])
#    print(stops[i])
#    print(frequencies[i])
#    print()