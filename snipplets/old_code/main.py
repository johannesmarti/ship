import numpy as np
import json
import sys

from world import World
from goods import GoodsConfig

def main():

    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "config.json"

    input_stream = open(filename, "r")
    config = json.load(input_stream)
    input_stream.close()

    goods_config = GoodsConfig(config['tradable_goods'], config['untradable_goods'])

    world = World(goods_config, config['provinces'], config['utility_coefficients'], 2)
    print("There are", world.num_provinces, "locations:")
    for i in range(0, world.num_provinces):
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

