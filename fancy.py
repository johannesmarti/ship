import logging

import numpy as np

import core.economy as economy
import wage_economy.wage_economy as we
import labor_economy.labor_economy as le
import pretty_table as pt
import market.line_search as ls
import market.adaptive as ad
from market.base import ScalingConfiguration,get_iteration,reset_iteration
from core.schema import *
from itertools import chain

np.set_printoptions(precision=8,suppress=True,threshold=12)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

local_schema = TradeGoodsSchema.from_lists(["food", "wood", "ore", "tools"],[])
province_schema = ProvinceSchema(["Switzerland", "Italy"])

switzerland = province_schema.province_of_name("Switzerland")
italy = province_schema.province_of_name("Italy")

def concat_map(func, it):
    return chain.from_iterable(map(func, it))

trade_factors = 3*np.array([3,4,2,1])
#trade_factors = 2*np.array([3,4,2,1])
#trade_factors = np.array([3,4,2,1])

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
        np.array([2, 1.2, 0, 0.7]),
        [
            economy.FactoryConfig(np.array([3.5, 1.8, 0, 0])), # Cow farm
            economy.FactoryConfig(np.array([0, -0.5, 1.4, 0])), # Swiss mine
            economy.FactoryConfig(np.array([0, -2, -1.4, 2])), # artisans
        ],
        list(set_up_merchants(switzerland, italy))
    ),

    # Italy
    economy.ProvinceConfig(
        6000,
        np.array([2.05, 1, 0, 0.5]),
        [
            economy.FactoryConfig(np.array([9, 0, 0, 0])), # Po farm
            economy.FactoryConfig(np.array([-1, 6, 0, 0])), # wood cutter
            economy.FactoryConfig(np.array([0, -1.5, -1, 1.6])), # smith
            economy.FactoryConfig(np.array([0, -0.5, 1.5, 0])), # Italian mine
        ],
        list(set_up_merchants(italy, switzerland))
    ),
]

econfig = economy.EconomyConfig(local_schema, province_schema, province_configs)
#econ = we.WageEconomy.from_config(econfig)
econ = le.LaborEconomy.from_config(econfig)

market_schema = econ.price_schema()
#p0 = np.array([70.0,100,60,200.0,15,70,110,60,200,11])
p0 = np.full(market_schema.global_width(), 100.0)
epsilon = 0.05
participants = list(econ.participants())

pt.set_global_table_logging_configuration(pt.PrettyTableConfiguration(
        schema = market_schema,
        list_of_indices = list(range(market_schema.global_width()))
))

scaling = ScalingConfiguration(set_to_price=100, norm_listing=market_schema.listing_of_good_in_province("labor", "Italy"))

def run_ls():
    config = ls.LineSearchConfiguration(
                t=0.2,
                backoff=0.2,
                necessary_improvement=0.9,
                price_scaling=scaling)
    p = ls.make_market(participants, p0, epsilon, config)
    print(f"lis iterations: {get_iteration()}")
    pt.pretty_table([("price", p)])
    reset_iteration()

def run_ad():
    config = ad.AdaptiveSearchConfiguration(
                    starting_t=0.2,
                    backoff=0.6,
                    max_t=10000,
                    min_t=0.0001,
                    min_change_factor=0.1,
                    max_change_factor=10,
                    necessary_improvement=1.00,
                    price_scaling=scaling
             )
    p = ad.make_market(participants, p0, epsilon, config)
    print(f"ads iterations: {get_iteration()}")
    pt.pretty_table([("price", p)])
    reset_iteration()


#run_ls()
#print()
run_ad()
