"""
This is the main file to execute whatever code I am currently intersted
in. It is not actually any proper application.
"""

import json
import logging
import sys
from typing import Callable

import numpy as np

import wage_economy.wage_economy as we
import labor_economy.labor_economy as le
import new_labor_economy.labor_economy as ne
import market.base as mb
import market.eva as eva
import pretty_table as pt
from read_world import read_world

#np.set_printoptions(precision=3,suppress=True,threshold=12)

#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')


def grid_search(func: Callable[[float, float], int],
                x_values: np.ndarray,
                y_values: np.ndarray) -> np.ndarray:
    # Initialize the result array
    results = np.empty((len(x_values), len(y_values)), dtype=int)

    # Use nested loops to compute the function over the grid
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            results[i, j] = func(x, y)

    return results

def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "world.json"

    with open(filename, "r", encoding='utf8') as input_stream:
        parsed_json = json.load(input_stream)

    economy_config = read_world(parsed_json)
    #economy = we.WageEconomy.from_config(economy_config)
    #economy = le.LaborEconomy.from_config(economy_config)
    economy = ne.LaborEconomy.from_config(economy_config)

    market_schema = economy.market_schema()
    pt.set_global_table_logging_from_schema(market_schema)
    p0 = np.full(market_schema.global_width(), 100.0)
    epsilon = 0.001
    participants = list(economy.participants())

    #scaling = mb.ScalingConfiguration(
    #    set_to_price=10,
    #    norm_listing=market_schema.listing_of_good_in_province("food", "Germany"))

    #config = eva.EvaConfiguration(
    #         epsilon=epsilon,
    #         rate=0.07,
    #         first_momentum_mixin = 0.07
    #)
    #p = eva.make_market(participants, p0, config)
    #p = mb.apply_price_scaling(p, scaling)
    #pt.pretty_table([("price", p)])
    #print(f"eva iterations: {mb.get_iteration()}")
    #mb.reset_iteration()

    def evaluator(x: float, y: float) -> int:
        config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate=x,
             first_momentum_mixin = y
        )
        mb.reset_iteration()
        print(f"starting eva with rate={x}, first_momentum_mixin={y}")
        eva.make_market(participants, p0, config)
        num_iters = mb.get_iteration()
        print(f"eva iterations: {num_iters}")
        mb.reset_iteration()
        return num_iters

    x_points = np.arange(0.08, 0.11, 0.01)
    y_points = np.arange(0.05, 0.10, 0.01)
    result = grid_search(evaluator, x_points, y_points)
    print(result)

    return 0

if __name__ == '__main__':
    sys.exit(main())
