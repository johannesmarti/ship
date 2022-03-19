import numpy as np
import sys

from world import World
from goods import GoodsConfig

tradable_goods = ['food', 'wood', 'weapons']
#untradable_goods = ['administration', 'military']
untradable_goods = []

goods_config = GoodsConfig(tradable_goods, untradable_goods)

spen_dist = {'weapons': 1}

location_config = [
{'name':        "Switzerland",
 'population':  8,
 'production':  [
    {'food': 2, 'wood': 1},
    {'wood': -1, 'gold': 8},
    {'wood': 3},
    {'food': -1, 'wood': -1, 'weapons': 4},
                ],
 'tax_rate':    0.001,
 'balance':     10,
 'spending_rate': 1.01,
 'spending_distribution': spen_dist,
 'trade_partners': ['Italy','France']},

{'name':        "Italy",
 'population':  40,
 'production':  [
    {'food': 6, 'wood': 1},
    {'wood': 2},
    {'food': -1, 'wood': -1, 'weapons': 3},
                ],
 'tax_rate':    0.001,
 'balance':     200,
 'spending_rate': 0.91,
 'spending_distribution': spen_dist,
 'trade_partners': ['Switzerland']},
{'name':        "France",
 'population':  50,
 'production':  [
    {'food': 7, 'wood': 1},
    {'wood': 3},
    {'wood': -1, 'gold': 5},
    {'food': -1, 'wood': -1, 'weapons': 4, 'gold': -0.2},
                ],
 'tax_rate':    0.0008,
 'balance':     80,
 'spending_rate': 1.10,
 'spending_distribution': spen_dist,
 'trade_partners': ['Switzerland']}
]

utility_coefficients = {'food': 2, 'wood': 1, 'weapons': 0.5}

def main():
    world = World(goods_config, location_config, utility_coefficients, 2)
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

