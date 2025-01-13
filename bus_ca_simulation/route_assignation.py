import json
from .data_loader import load_network

ZERO_TRANSFER_MAX = 1.5
ONE_TRANSFER_MAX = 1.1
TWO_TRANSFER_MAX = 1.1

network = load_network()

def is_zero_transfer(Ri, Rj):
    possible_routes = set(Ri).intersection(Rj)
    if not possible_routes:
        return False
    return True
    
def is_one_transfer(Ri, Rj, routes):
    for ri in Ri:
        for rj in Rj:
            if set(routes[ri]).intersection(routes[rj]):
                return True

    return False

def is_two_transfer(Ri, Rj, routes):
    aux_set = set(Ri).union(Rj)
    complement = [e for (e, _) in enumerate(routes) if e not in aux_set]
    for r3 in complement:
        for r1 in Ri:
            for r2 in Rj:
                if set(routes[r3]).intersection(routes[r1]) and set(routes[r3]).intersection(routes[r2]):
                    return True
    return False

def compute_time(i, j, r):
    if i == j:
        return 0
    start, end = sorted((r.index(i), r.index(j)))
    edges = [(network[r[m]], r[m + 1]) for m in range(start, end)]
    cost = sum(list(map(lambda p: next((c for a, c in p[0] if a == p[1]), (0, 0)), edges)))
    return cost

def compute_time_first_bus(i, j, r):
    start, end = r.index(i), r.index(j)
    if(start > end):
        return compute_time(r[-1], i, r)
    return compute_time(r[0], i, r)

def get_min_time(i, j, search_routes, routes):
    return min(map(lambda x: compute_time(i,j,routes[x]), search_routes))    

def get_min_first_route(i, j, search_routes, routes):
    return min(map(lambda x: compute_time_first_bus(i,j,routes[x]), search_routes))

def get_path(i, j, r):
    f_index, s_index = (r.index(i), r.index(j))
    start, end = sorted((f_index, s_index))
    pairs = [r[i] for i in range (start, end+1)]
    if f_index > s_index:
        pairs.reverse()
    return pairs

def get_transfers_routes(i, j, routes, stops):
    Ri = [e for (e, x) in enumerate(stops) if i in x]
    Rj = [e for (e, x) in enumerate(stops) if j in x]
    filtered_routes = []
    if is_zero_transfer(Ri, Rj):
        possible_routes = set(Ri).intersection(Rj)
        t_cij = get_min_time(i, j, possible_routes, routes)
        filtered_routes = list(filter(lambda x: compute_time(i, j, routes[x]) < t_cij*ONE_TRANSFER_MAX, possible_routes))
        filtered_routes = [[j] for _ in filtered_routes]
    elif is_one_transfer(Ri, Rj, routes):
        possible_routes = [(ri, rj) for ri in Ri for rj in Rj if set(routes[ri]).intersection(routes[rj])]
        possible_transfers = [(p[0], p[1], tf) for p in possible_routes for tf in set(routes[p[0]]).intersection(routes[p[1]])]

        min_time = min(
            compute_time(i, p[2], routes[p[0]]) + compute_time(p[2], j, routes[p[1]])
            for p in possible_transfers
        )

        filtered_routes = [
            p for p in possible_transfers
            if compute_time(i, p[2], routes[p[0]]) + compute_time(p[2], j, routes[p[1]]) <
            ONE_TRANSFER_MAX * min_time
        ]
        
        filtered_routes = [
            [j, p[2]]
            for p in filtered_routes]
    
    elif is_two_transfer(Ri, Rj, routes):
        aux_set = set(Ri).union(Rj)
        complement = [e for (e, _) in enumerate(routes) if e not in aux_set]

        possible_routes = [
            (r1, r2, r3) 
            for r1 in Ri 
            for r2 in Rj 
            for r3 in complement 
            if set(routes[r3]).intersection(routes[r1]) and set(routes[r3]).intersection(routes[r2])
        ]

        possible_transfers = [
            (r1, r2, r3, tf1, tf2) 
            for (r1, r2, r3) in possible_routes 
            for tf1 in set(routes[r3]).intersection(routes[r1]) 
            for tf2 in set(routes[r3]).intersection(routes[r2])
        ]

        min_time = min(
            compute_time(i, tf1, routes[r1]) + compute_time(tf1, tf2, routes[r3]) + 
            compute_time(tf2, j, routes[r2])
            for (r1, r2, r3, tf1, tf2) in possible_transfers
        )

        filtered_routes = [
            (r1, r2, r3, tf1, tf2) 
            for (r1, r2, r3, tf1, tf2) in possible_transfers 
            if compute_time(i, tf1, routes[r1]) + compute_time(tf1, tf2, routes[r3]) + 
            compute_time(tf2, j, routes[r2]) < TWO_TRANSFER_MAX * min_time
        ]

        filtered_routes = [
            [j, p[4], p[3]]
            for p in filtered_routes
        ]
    return filtered_routes #Gives the nodes in reverse

def get_travel_routes(routes, stops):
    travel = [[[] for _ in range(len(network))] for _ in range(len(network))]

    for i in range(len(network)):
        for j in range(len(network)):
            if i == j: continue
            travel[i][j] = get_transfers_routes(i, j, routes, stops)

    return travel

#print(get_first_travel_route(routes = [
#    [0, 1, 2, 5, 7, 9, 10, 12],
#    [4, 3, 5, 7, 14, 6],
#    [11, 3, 5, 14, 8],
#    [9, 13, 12]
#]))