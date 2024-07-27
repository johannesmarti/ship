import json
import logging
import numpy as np
import sys
import itertools

import fast_labor_economy.labor_economy as ne
import market.base as mb
import market.eva as eva
import pretty_table as pt
from read_world import read_world


"""
class Coding:
    def __init__(self, );
        pass
    def encode
"""

#np.set_printoptions(precision=3,suppress=True,threshold=12)

#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

def base_data() -> any:
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
    epsilon = 0.001
    participants = list(economy.participants())

    scaling = mb.ScalingConfiguration(
        set_to_price=10,
        norm_listing=schema.listing_of_good_in_province("food", "Germany")
    )

    config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate=0.07,
             first_momentum_mixin = 0.07,
             keep_history = False
    )
    r = eva.make_market(participants, p0, config)
    p = r.price
    p = mb.apply_price_scaling(p, scaling)
    #pt.pretty_table([("price", p)])
    print(f"eva iterations: {r.iterations}")

    sold = r.supply.sold()
    bought = r.supply.bought()

    datalist = [1,2,3,1,2,2]
    response = {
        "schema": [
           { "name": "good",
             "indices": schema.local_schema().list_of_names() },
           { "name": "province",
             "indices": schema.province_schema().list_of_names() },
           { "name": "datatype",
             "indices": ["price", "sold", "bought"] }],
        "data": list(itertools.chain(iter(p), iter(sold), iter(bought)))
    }
    return response
