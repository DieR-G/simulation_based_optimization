from .route_assignation import get_travel_routes
from .data_loader import load_network
import json

network = load_network()

def floyd_warshall(n):
    mat = [[int(1e10) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        mat[i][i] = 0
        for j, c in network[i]:
            mat[i][j] = min(c, mat[i][j])
    for k in range(n):
        for i in range(n):
            for j in range(n):
                mat[i][j] = min(mat[i][j], mat[i][k] + mat[k][j])
    return mat

print(len(network))
distances = floyd_warshall(len(network))
with open('distance_mat.json', 'w') as file:
    json.dump(distances, file)
    