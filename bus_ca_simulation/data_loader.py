import json
from importlib.resources import files

INSTANCE_NAME = '403k_test_1'
INSTANCE_FOLDER = f'instance_{INSTANCE_NAME}'

# Define the instance files relative to the `data` folder
COORDINATES_FILE = f'{INSTANCE_FOLDER}/coordinates.json'
DEMAND_MATRIX_FILE = f'{INSTANCE_FOLDER}/demand_matrix.json'
NETWORK_FILE = f'{INSTANCE_FOLDER}/network.json'
ROUTES_FILE = f'{INSTANCE_FOLDER}/routes.json'
STOPS_FILE = f'{INSTANCE_FOLDER}/stops.json'
FREQUENCIES_FILE = f'{INSTANCE_FOLDER}/frequencies.json'
CAPACITIES_FILE = f'{INSTANCE_FOLDER}/capacities.json'
PLATFORMS_FILE = f'{INSTANCE_FOLDER}/platforms.json'

# Helper function to load JSON files
def load_path(file_name):
    # Locate the file within the `data` folder of the package
    data_file = files('bus_ca_simulation.data') / file_name
    with open(data_file, 'r') as file:
        return json.load(file)

# Loaders for specific files
def load_coordinates():
    return load_path(COORDINATES_FILE)

def load_demand_matrix():
    return load_path(DEMAND_MATRIX_FILE)

def load_network():
    return load_path(NETWORK_FILE)

def load_routes():
    return load_path(ROUTES_FILE)

def load_stops():
    return load_path(STOPS_FILE)

def load_frequencies():
    return load_path(FREQUENCIES_FILE)

def load_capacities():
    return load_path(CAPACITIES_FILE)

def load_platforms():
    return load_path(PLATFORMS_FILE)
