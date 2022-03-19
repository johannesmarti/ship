import numpy as np
import sys

from world import World

location_config = [
{'name':        "Switzerland",
 'population':  8,
 'production':  [
                    [2,1,0,0],
                    [0,-1,0,8],
                    [0,3,0,0],
                    [-1,-1,4,0]
                ],
 'tax_rate':    0.001,
 'balance':     10,
 'spending_rate': 1.01,
 'spending_distribution': [0,0,1],
 'trade_partners': ['Italy','France']},

{'name':        "Italy",
 'population':  40,
 'production':  [
                    [6,1,0,0],
                    [0,2,0,0],
                    [-1,-1,3,0]
                ],
 'tax_rate':    0.001,
 'balance':     200,
 'spending_rate': 0.91,
 'spending_distribution': [0,0,1],
 'trade_partners': ['Switzerland']},
{'name':        "France",
 'population':  50,
 'production':  [
                    [7,1,0,0],
                    [0,3,0,0],
                    [0,-1,0,5],
                    #[0,0,1,-2],
                    [-1,-1,4,0]
                ],
 'tax_rate':    0.0008,
 'balance':     80,
 'spending_rate': 1.10,
 'spending_distribution': [0,0,1],
 'trade_partners': ['Switzerland']}
]

utility_coefficients = np.array([2,1,1])

def main():
    world = World(location_config,utility_coefficients, 2, 2)
    print("There are", world.num_provinces(), "locations:")
    for i in range(0, world.num_provinces()):
        print(world.name_of_index(i))
        print(world.producers[i].production_matrix)

    res = world.find_equilibrium(alpha=1.1)
    print(res.values.error_vector)
    print(res.prices)
    print(res.values.allocations)
    print("iterations:", res.iterations)
    return 0

if __name__ == '__main__':
    sys.exit(main())

