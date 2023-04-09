import logging

import numpy as np

import core.economy as economy
import wage_economy.wage_economy as we
import labor_market.labor_economy as le
from market.line_search import line_search_market, get_iteration, reset_iteration, LineSearchConfiguration, ScalingConfiguration
from core.schema import *
from itertools import chain

np.set_printoptions(precision=8,suppress=True,threshold=12)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

local_schema = TradeGoodsSchema.from_lists(["food", "wood", "ore", "tools"],[])
province_schema = ProvinceSchema(["Switzerland", "Italy"])

switzerland = province_schema.province_of_name("Switzerland")
italy = province_schema.province_of_name("Italy")

def concat_map(func, it):
    """Map a function over a list and concatenate the results."""
    return chain.from_iterable(map(func, it))

trade_factors = 2*np.array([3,4,2,1])

def set_up_merchants(home: int, foreign: int) -> Iterable[economy.TradeConfig]:
    def for_good(good: int) -> Iterable[economy.TradeConfig]:
        factor = trade_factors[good]
        return [economy.TradeConfig(good, home, foreign, factor),
                economy.TradeConfig(good, foreign, home, factor)]
    return concat_map(for_good, local_schema.trade_goods())

province_configs = [
    # Switzerland
    economy.ProvinceConfig(
        800,
        np.array([2, 1.2, 0, 1.1]),
        [
            economy.FactoryConfig(np.array([3.5, 1.8, 0, 0])), # Cow farm
            economy.FactoryConfig(np.array([0, -0.5, 1.7, 0])), # Swiss mine
            economy.FactoryConfig(np.array([0, -2, -1, 2])), # artisans
        ],
        list(set_up_merchants(switzerland, italy))
    ),

    # Italy
    economy.ProvinceConfig(
        6000,
        np.array([2.1, 1, 0, 1]),
        [
            economy.FactoryConfig(np.array([9, 0, 0, 0])), # Po farm
            economy.FactoryConfig(np.array([-1, 4, 0, 0])), # wood cutter
            economy.FactoryConfig(np.array([0, -1.5, -1.2, 1.8])), # smith
            economy.FactoryConfig(np.array([0, -0.5, 1.8, 0])), # Italian mine
        ],
        list(set_up_merchants(italy, switzerland))
    ),
]

econfig = economy.EconomyConfig(local_schema, province_schema, province_configs)
econ = we.WageEconomy.from_config(econfig)
#econ = le.LaborEconomy.from_config(econfig)

p0 = np.full(econ.price_width(), 10)
epsilon = 0.000001
participants = list(econ.participants())

def run_once(t : float):
    config = LineSearchConfiguration(t=t, beta=0.3, price_scaling=ScalingConfiguration(100))
    p = line_search_market(participants, p0, epsilon, config)
    print(f"iterations: {get_iteration()}    (t={t})")
    print(p)
    reset_iteration()

run_once(0.2)
