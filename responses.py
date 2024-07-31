import json
import logging
import numpy as np
import sys
import itertools
from typing import Iterable

import fast_labor_economy.labor_economy as ne
import market.base as mb
import market.eva as eva
import pretty_table as pt
from read_world import read_world


#np.set_printoptions(precision=3,suppress=True,threshold=12)

#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

def responses() -> any:
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "world.json"

    with open(filename, "r", encoding='utf8') as input_stream:
        parsed_json = json.load(input_stream)

    economy_config = read_world(parsed_json)
    economy = ne.LaborEconomy.from_config(economy_config)

    schema = economy.market_schema()
    pt.set_global_table_logging_from_schema(schema)

    p0 = np.full(schema.global_width(), 100.0)
    epsilon = 0.1
    participants = list(economy.participants())

    #scaling = mb.ScalingConfiguration(
    #    set_to_price=10,
    #    norm_listing=schema.listing_of_good_in_province("food", "Germany")
    #)

    duo_config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate = 0.01,
             first_momentum_mixin = 0.1,
             keep_history = True,
             max_iterations = 10000
    )
    config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate = 0.08,
             first_momentum_mixin = 0.09,
             keep_history = True,
             max_iterations = 1000
    )
    config = duo_config
    r = eva.make_market(participants, p0, config)

    def iter_for_iteration(iteration: eva.Iteration) -> Iterable[float]:
        return itertools.chain(iter(iteration.price),
                               iter(iteration.supply.error),
                               iter(iteration.supply.volume),
                               map(lambda m: 1000 * 1000 * m, iter(iteration.momentum)))
    nested_iterator = map(iter_for_iteration, r.history)
    history_iter = itertools.chain.from_iterable(nested_iterator)
    raw_data = list(history_iter)
    debug_response = {
        "schema": [
           { "name": "iteration",
             "indices": list(map(lambda i: i + 1, range(len(r.history)))) },
           { "name": "datatype",
             "indices": ["price", "error", "volume", "Mp"] },
           { "name": "province",
             "indices": schema.province_schema().list_of_names() },
           { "name": "good",
             "indices": schema.local_schema().list_of_names() } ],
        "raw_data": raw_data
    }

    p = r.price
    supply = r.supply
    #p = mb.apply_price_scaling(p, scaling)
    #pt.pretty_table([("price", p)])
    print(f"eva iterations: {r.iterations}")

    basic_response = {
        "schema": [
           { "name": "datatype",
             "indices": ["price", "sold", "bought"] },
           { "name": "province",
             "indices": schema.province_schema().list_of_names() },
           { "name": "good",
             "indices": schema.local_schema().list_of_names() } ],
        "raw_data": list(itertools.chain(iter(p), iter(supply.error),
                                                  iter(supply.volume)))
    }

    return (basic_response, debug_response)
