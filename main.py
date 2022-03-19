import numpy as np
import sys

from world import World

location_config = [
{'name':        "Switzerland",
 'population':  8,
 'production':  [
                    [1,1,0,0],
                    [0,-1,0,8],
                    [0,3,0,0],
                    [-1,-1,4,0]
                ],
 'tax_rate':    0.001,
 'trade_partners': ['Italy','France']},

{'name':        "Italy",
 'population':  40,
 'production':  [
                    [4,1,0,0],
                    [0,2,0,0],
                    [-1,-1,3,0]
                ],
 'tax_rate':    0.0005,
 'trade_partners': ['Switzerland']},
{'name':        "France",
 'population':  50,
 'production':  [
                    [5,1,0,0],
                    [0,3,0,0],
                    [0,-1,0,3],
                    #[0,0,1,-2],
                    [-1,-1,4,0]
                ],
 'tax_rate':    0.001,
 'trade_partners': ['Switzerland']}
]

utility_coefficients = np.array([2,1,1])

def main():
    world = World(location_config,utility_coefficients, 2, 2)
    print("There are", world.num_provinces(), "locations:")
    for i in range(0,world.num_provinces()):
        print(world.name_of_index(i))
        print(world.producers[i].production_matrix)

    res = world.find_equilibrium(alpha=2)
    print(res.values.error_vector)
    print(res.prices)
    print(res.values.allocations)

    return 0

if __name__ == '__main__':
    sys.exit(main())

