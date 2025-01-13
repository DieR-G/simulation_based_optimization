from .data_loader import load_routes, load_platforms

routes = load_routes()

def generate_platforms(stations_number, platforms_data):
    platforms = [[[],[]] for _ in range(stations_number)]
    for node, platform_list in enumerate(platforms_data):
        for list in platform_list:
            platforms[node][0].append([True, set(list)])
            platforms[node][1].append([True, set(list)])
    return platforms