import numpy as np
import json

random_mat = np.random.random_integers(0, 50, (15, 15))
mat = (random_mat+random_mat.T)//2
np.fill_diagonal(mat, 0)
print(mat)
with open('data/demand_matrix2.json', 'w') as file:
    json.dump(mat.tolist(), file)