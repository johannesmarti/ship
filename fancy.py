import logging

import numpy as np

import core.economy as economy
import wage_economy.wage_economy as we
import labor_economy.labor_economy as le
import pretty_table as pt
import market.line_search as ls
import market.elastic as el
import market.eva as eva
import market.adam as adam
from market.base import *
from core.schema import *
from itertools import chain

np.set_printoptions(precision=8,suppress=True,threshold=12)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

local_schema = TradeGoodsSchema.from_lists(["food", "alcohol", "wood", "ore", "tools"],[])
province_schema = ProvinceSchema(["Switzerland", "Italy", "France","Germany","Austria","The Netherlands","England","Spain"])

switzerland = province_schema.province_of_name("Switzerland")
italy = province_schema.province_of_name("Italy")
france = province_schema.province_of_name("France")
germany = province_schema.province_of_name("Germany")
austria = province_schema.province_of_name("Austria")
netherlands = province_schema.province_of_name("The Netherlands")
england = province_schema.province_of_name("England")
spain = province_schema.province_of_name("Spain")

def concat_map(func, it):
    return chain.from_iterable(map(func, it))

#trade_factors = 4*np.array([3, 5, 2, 2, 4])
#trade_factors = 2*np.array([3, 5, 2, 2, 4])
#trade_factors = np.array([2.5, 4, 1.5, 2, 3.5])
trade_factors = np.array([3, 3, 1.5, 2, 3])

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
        np.array([2, 0.5, 1.2, 0, 0.7]),
        [
            economy.FactoryConfig(np.array([5, 0.5, 1.5, 0, 0])), # Cow farm
            economy.FactoryConfig(np.array([0, 0, -2, -1, 3])), # artisans
        ],
        list(set_up_merchants(switzerland, italy)) +
           list(set_up_merchants(switzerland, france)) +
           list(set_up_merchants(switzerland, germany)) +
           list(set_up_merchants(switzerland, austria))
    ),

    # Italy
    economy.ProvinceConfig(
        6000,
        np.array([2.05, 0.5, 0.8, 0, 0.5]),
        [
            economy.FactoryConfig(np.array([8, 0, 0, 0, 0])), # Po farm
            economy.FactoryConfig(np.array([0, 1.2, 0, 0, -0.1])), # wine
            economy.FactoryConfig(np.array([-1, 0, 4, 0, 0])), # wood cutter
            economy.FactoryConfig(np.array([0, 0, -1.9, -1.2, 1.8])), # smith
        ],
        list(set_up_merchants(italy, switzerland))
            + list(set_up_merchants(italy, france))
            + list(set_up_merchants(italy, austria))
    ),
    # France
    economy.ProvinceConfig(
        6500,
        np.array([2.02, 0.6, 1, 0.1, 0.5]),
        [
            economy.FactoryConfig(np.array([8, 0, 0, 0, 0])), # Franch farming
            economy.FactoryConfig(np.array([0, 1.2, 0, 0, -0.1])), # wine
            economy.FactoryConfig(np.array([0, 0, 5, 0, -0.3])), # wood cutter
            economy.FactoryConfig(np.array([0, 0, -0.5, 1.7, 0])), # French mine
            economy.FactoryConfig(np.array([0, 0, -1.9, -1.3, 1.9])), # smith
        ],
        list(set_up_merchants(france, switzerland))
            + list(set_up_merchants(france, italy))
            + list(set_up_merchants(france, germany))
            + list(set_up_merchants(france, netherlands))
            + list(set_up_merchants(france, england))
            + list(set_up_merchants(france, spain))
    ),
    # Germany
    economy.ProvinceConfig(
        8000,
        np.array([2.01, 0.7, 1, 0.0, 0.6]),
        [
            economy.FactoryConfig(np.array([6, 0, 1, 0, 0])), # farming
            economy.FactoryConfig(np.array([0, 1.1, 0, 0, -0.1])), # wine
            economy.FactoryConfig(np.array([0, 1.2, -0.5, 0, 0])), # beer
            economy.FactoryConfig(np.array([0, 0, 6, 0, -0.2])), # wood cutter
            economy.FactoryConfig(np.array([0, 0, -0.5, 1.6, 0])), # mine
            economy.FactoryConfig(np.array([0, 0, -2, -1.3, 2])), # smith
        ],
        list(set_up_merchants(germany, switzerland))
           + list(set_up_merchants(germany, france))
           + list(set_up_merchants(germany, austria))
           + list(set_up_merchants(germany, netherlands))
    ),
    # Austria
    economy.ProvinceConfig(
        700,
        np.array([2.01, 0.6, 1.1, 0.0, 0.5]),
        [
            economy.FactoryConfig(np.array([5, 0, 2, 0, 0])), # farming
            economy.FactoryConfig(np.array([-1, 1.3, 0, 0, 0])), # liquor
            economy.FactoryConfig(np.array([0, 0, -1.9, -1.3, 1.9])), # smith
        ],
        list(set_up_merchants(austria, switzerland))
           + list(set_up_merchants(austria, italy))
           + list(set_up_merchants(austria, germany))
    ),
    # Netherlands
    economy.ProvinceConfig(
        1700,
        np.array([1.99, 0.6, 1.3, 0.0, 0.55]),
        [
            economy.FactoryConfig(np.array([11, 0, 0, 0, 0])), # Wageningen
            economy.FactoryConfig(np.array([0, 0, -1.9, -1.3, 1.9])), # smith
        ],
        list(set_up_merchants(netherlands, france))
           + list(set_up_merchants(netherlands, germany))
           + list(set_up_merchants(netherlands, england))
    ),
    # England
    economy.ProvinceConfig(
        6600,
        np.array([1.97, 0.8, 1.1, 0, 0.49]),
        [
            economy.FactoryConfig(np.array([5.5, 0, 0.4, 0, 0])), # farming
            economy.FactoryConfig(np.array([0, 1.2, -0.4, 0, 0])), # beer
            economy.FactoryConfig(np.array([0, 0, 6.5, 0, -0.1])), # wood cutter
            economy.FactoryConfig(np.array([0, -0.1, -0.5, 1.9, 0])), # mine
            economy.FactoryConfig(np.array([0, 0, -2.0, -1.3, 1.9])), # smith
        ],
        list(set_up_merchants(england, italy))
           + list(set_up_merchants(england, france))
           + list(set_up_merchants(england, germany))
           + list(set_up_merchants(england, spain))
    ),
    # Spain
    economy.ProvinceConfig(
        4600,
        np.array([2.02, 0.5, 0.7, 0, 0.5]),
        [
            economy.FactoryConfig(np.array([6, 0, 0.5, 0, 0])), # farming
            economy.FactoryConfig(np.array([0, 1.1, 0, 0, -0.1])), # wine
            economy.FactoryConfig(np.array([0, 0, -1.5, -1.3, 1.7])), # smith
        ],
        list(set_up_merchants(spain, italy))
           + list(set_up_merchants(spain, france))
    ),
]

econfig = economy.EconomyConfig(local_schema, province_schema, province_configs)
econ = we.WageEconomy.from_config(econfig)
#econ = le.LaborEconomy.from_config(econfig)

market_schema = econ.price_schema()
p0 = np.full(market_schema.global_width(), 100.0)
epsilon = 0.1
participants = list(econ.participants())

pt.set_global_table_logging_configuration(pt.PrettyTableConfiguration(
    schema = market_schema,
    #list_of_indices = list(range(market_schema.global_width()))
    list_of_indices = list(market_schema.list_provinces_over_goods(
        None, None))
    #    ["food", "alcohol", "ore"],
    #    ["Switzerland", "Spain"]))
))

scaling = ScalingConfiguration(set_to_price=10, norm_listing=market_schema.listing_of_good_in_province("food", "Germany"))

def run_ls():
    config = ls.LineSearchConfiguration(
                epsilon=epsilon,
                initial_backoff = 0.005,
                backoff_decay = 0.1,
                necessary_improvement=1,
                necessary_improvement_decay = 0.95,
                price_scaling=scaling)
    p = ls.make_market(participants, p0, config)
    print(f"lis iterations: {get_iteration()}")
    pt.pretty_table([("price", p)])
    reset_iteration()

def run_el():
    config = el.ElasticMarketConfiguration(
                epsilon=epsilon,
                necessary_improvement = 1,
                necessary_improvement_decay = 0.87,
                initial_backoff = 0.008,
                backoff_decay = 0.1,
                elasticity_mixing = 0.05,
                inner_elasticity_mixing = 0.40,
                #price_scaling=scaling
                price_scaling=None
             )
    p = el.make_market(participants, p0, config)
    p = apply_price_scaling(p, scaling)
    pt.pretty_table([("price", p)])
    print(f"ads iterations: {get_iteration()}")
    reset_iteration()

def run_eva():
    config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate=0.03,
             first_momentum_mixin = 0.025
    )
    p = eva.make_market(participants, p0, config)
    p = apply_price_scaling(p, scaling)
    pt.pretty_table([("price", p)])
    print(f"eva iterations: {get_iteration()}")
    reset_iteration()

def run_adam():
    config = adam.AdamConfiguration(
                epsilon=epsilon,
                rate=0.00001,
                first_momentum_mixin = 0.02,
                second_momentum_mixin = 0.0001
             )
    p = adam.make_market(participants, p0, config)
    p = apply_price_scaling(p, scaling)
    pt.pretty_table([("price", p)])
    print(f"eva iterations: {get_iteration()}")
    reset_iteration()


run_eva()

