import numpy as np
import sys

from world import World

location_config = [
{'name':        "Switzerland",
 'population':  8,
 'resources':   [
                    [1,1,0],
                    [0,3,0]
                ],
 'tax_rate':    0.05,
 'trade_partners': ['Italy','France']},

{'name':        "Italy",
 'population':  40,
 'resources':   [
                    [4,1,0],
                    [0,2,0]
                ],
 'tax_rate':    0.08,
 'trade_partners': ['Switzerland']},
{'name':        "France",
 'population':  50,
 'resources':   [
                    [5,1,0],
                    [0,2,0]
                ],
 'tax_rate':    0.1,
 'trade_partners': ['Switzerland']}
]

utility_coefficients = np.array([2,1,1])

def main():
    world = World(location_config,utility_coefficients)
    print("There are", world.num_provinces(), "locations:")
    for i in range(0,world.num_provinces()):
        print(world.name_of_index(i))
    return 0

if __name__ == '__main__':
    sys.exit(main())

