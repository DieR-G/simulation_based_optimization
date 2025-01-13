import bus_ca_simulation.simulation as simulation
import bus_ca_simulation.data_loader as data_loader
from heuristics import generate_initial_solution, distribute_doors, generate_direct_solution
import numpy as np
from solution import Solution
from operators import delete_random_stop, add_random_stop, add_route
import random
import copy
import pickle

def delete_random_node(solution):
    idx = random.randint(1, solution.route_number - 1)
    deleted, solution.routes[idx], solution.stops[idx] = delete_random_stop(solution.routes[idx], solution.stops[idx])
    solution.route_map[deleted] = list(filter(lambda x: x != idx, solution.route_map[deleted]))
    platform_number = 6
    if deleted == 0 or deleted == solution.stations_number - 1:
        platform_number = 20
    temp = distribute_doors(solution.route_map[deleted], solution.frequencies, platform_number)
    solution.platforms[deleted] = [val for val in temp]

def add_random_node(solution):
    idx = random.randint(1, solution.route_number - 1)
    added, solution.routes[idx], solution.stops[idx] = add_random_stop(solution.routes[idx], solution.stops[idx])
    solution.route_map[added].append(idx)
    platform_number = 6
    if added == 0 or added == solution.stations_number - 1:
        platform_number = 20
    temp = distribute_doors(solution.route_map[added], solution.frequencies, platform_number)
    solution.platforms[added] = [val for val in temp]

def reduce_random_route(solution):
    idx = random.randint(0, solution.route_number - 1)
    if solution.frequencies[idx] > 20:
        solution.frequencies[idx] -= 20

def increase_random_route(solution):
    idx = random.randint(0, solution.route_number - 1)
    solution.frequencies[idx] += 20

solutions = {}

initial_solution = Solution(*generate_direct_solution(300))
simu = simulation.Simulation()
current_occupancy = []
finished, simulation_time, _, _, _, initial_solution.total_time, _, _ = simu.evaluate(*initial_solution.get_vals())
print(simulation_time, initial_solution.total_time)
for i in range(10):
    simu = simulation.Simulation()
    current = copy.deepcopy(initial_solution)
    gaps = [0, 2, 3, 4, 5, 6, 7]
    add_route(current, gaps[i % len(gaps)], 60)
    finished, time, _, _, _, current.total_time, _, current_occupancy = simu.evaluate(*current.get_vals())
    print(current_occupancy)
    print(time, current.total_time, current.bus_number)
    if current.total_time < initial_solution.total_time:
        initial_solution = copy.deepcopy(current)

print(initial_solution.total_time)

best = initial_solution
    
solutions[best.bus_number] = copy.deepcopy(best)

for i in range(10):
    simu = simulation.Simulation()
    current = copy.deepcopy(best)
    for x in sorted(current_occupancy):
        idx = current_occupancy.index(x)
        if current.frequencies[idx] > 10:
            current.frequencies[idx] -= 10
            current.bus_number -= 10
            break
    finished, time, _, _, _, current.total_time, _, current_occupancy = simu.evaluate(*current.get_vals())
    print(time, current.total_time, current.bus_number)
    if current.total_time < best.total_time:
        best = copy.deepcopy(current)
    if (current.bus_number not in solutions) or (current.total_time < solutions[current.bus_number].total_time):
        solutions[current.bus_number] = copy.deepcopy(current)
    

operators = [delete_random_node, add_random_node, reduce_random_route, increase_random_route]

with open('initial_sol.pkl', 'wb') as file:
    pickle.dump(best, file)

print(f"Initial solution: value={best.total_time}, buses={best.bus_number}")

exit(0)

op = 0
iterations = 300
for i in range(iterations):
    simu = simulation.Simulation()
    current = copy.deepcopy(best)
    op += 1
    op %= 4
    operators[op](current)
    finished, time, _, _, _, total_time, _ = simu.evaluate(*current.get_vals())
    print(f"Iteration {i+1}: time={total_time}, buses={current.bus_number}")

    if finished:
        current.total_time = total_time
        if current.total_time < best.total_time:
            best = copy.deepcopy(current)
        if (current.bus_number not in solutions) or (total_time < solutions[current.bus_number].total_time):
            solutions[current.bus_number] = copy.deepcopy(current)

with open('solution.pkl', 'wb') as file:
    pickle.dump(solutions, file)

print(best.total_time)
print(solutions)

x = {}

with open('solution.pkl', 'rb') as file:
    x = pickle.load(file)

print(solutions)

# Display the best solutions for each number of buses
for bus_number, solution in sorted(solutions.items()):
    print(f"Buses: {bus_number}, Best Value: {solution.total_time}")
