import numpy as np
import sys

from world import World

location_config = [
{'name':        "Switzerland",
 'population':  8,
 'production':  [
                    [1,1,0,0],
                    [0,-1,0,0.5],
                    [0,3,0,0],
                    [-1,-1,5,0]
                ],
 'tax_rate':    0.05,
 'trade_partners': ['Italy','France']},

{'name':        "Italy",
 'population':  40,
 'production':  [
                    [4,1,0,0],
                    [0,2,0,0],
                    [-1,-1,3,0]
                ],
 'tax_rate':    0.08,
 'trade_partners': ['Switzerland']},
{'name':        "France",
 'population':  50,
 'production':  [
                    [5,1,0,0],
                    [0,2,0,0],
                    [-1,-1,3,0]
                ],
 'tax_rate':    0.1,
 'trade_partners': ['Switzerland']}
]

utility_coefficients = np.array([2,1,1])

def main():
    world = World(location_config,utility_coefficients, 2)
    print("There are", world.num_provinces(), "locations:")
    for i in range(0,world.num_provinces()):
        print(world.name_of_index(i))

    print(world.producers[0].production_matrix)
    return 0

if __name__ == '__main__':
    sys.exit(main())

