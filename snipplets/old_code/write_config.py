import json
import sys

from goods import *

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

config = {
  'tradable_goods': tradable_goods,
  'untradable_goods': untradable_goods,
  'provinces': location_config,
  'utility_coefficients': utility_coefficients,
}

def dump_to_stream(stream):
    json.dump(config, stream, sort_keys=True, indent=2)
    stream.write('\n')

def main():
    dump_to_stream(sys.stdout)
    return 0

if __name__ == '__main__':
    sys.exit(main())
