from itertools import chain
import json
import logging
import numpy as np
import sys
from typing import Callable, Iterable
from functools import partial

import core.economy as economy
import core.schema as schema
from core.schema import GoodId, ProvinceId
import labor_economy.labor_economy as le
import market.base as mb
import market.eva as eva
import pretty_table as pt
import wage_economy.wage_economy as we

#np.set_printoptions(precision=3,suppress=True,threshold=12)

#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

def read_world(json_world: any) -> economy.EconomyConfig:
    json_provinces = json_world['provinces']
    province_names = list(map(lambda h : h['name'], json_provinces))
    province_schema = schema.ProvinceSchema(province_names)
    tradable_goods = json_world['tradable_goods']
    fixed_goods = json_world['fixed_goods']
    local_schema = schema.TradeGoodsSchema.from_lists(tradable_goods,
                                                      fixed_goods)
    global_utilities = json_world.get('global_utilities', {})
    trade_factor_dict = json_world['trade_factors']
    trade_factors = local_schema.dict_to_vector(trade_factor_dict)

    def read_province(json_province: any) -> economy.ProvinceConfig:
        population = json_province['population']
        local_utilities = json_province['utilities']
        utilities_dict = global_utilities | local_utilities
        utilities = local_schema.dict_to_vector(utilities_dict)

        factories = list(map(partial(read_factory, local_schema),
                             json_province['producers']))

        def get_province_id(name: str) -> ProvinceId:
            return province_schema.province_of_name(name)
        local_id = get_province_id(json_province['name'])
        other_ids = map(get_province_id, json_province['trade_partners'])
        merchants = list(set_up_trade(local_schema.trade_goods(),
                                      trade_factors, local_id, other_ids))

        config = economy.ProvinceConfig(population, utilities,
                                        factories, merchants)
        return config

    province_configs = list(map(read_province, json_provinces))
    econfig = economy.EconomyConfig(local_schema, province_schema,
                                    province_configs)
    return econfig

def read_factory(local_schema: economy.TradeGoodsSchema,
                 json_factory: any) -> economy.FactoryConfig:
    production_coefficients = local_schema.dict_to_vector(json_factory)
    return economy.FactoryConfig(production_coefficients)

def concat_map(func: Callable[[any], Iterable[any]], it: any) -> Iterable[any]:
    return chain.from_iterable(map(func, it))

def set_up_trade(trade_goods: Iterable[GoodId], trade_factors: np.ndarray,
                 home: ProvinceId, trade_partners: Iterable[ProvinceId]
                ) -> Iterable[economy.TradeConfig]:
    def set_up_merchants(foreign: ProvinceId) -> Iterable[economy.TradeConfig]:
        def for_good(good: GoodId) -> Iterable[economy.TradeConfig]:
            factor = trade_factors[good]
            return [economy.TradeConfig(good, home, foreign, factor),
                    economy.TradeConfig(good, foreign, home, factor)]
        return concat_map(for_good, trade_goods)
    return concat_map(set_up_merchants, trade_partners)


def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "world.json"

    with open(filename, "r") as input_stream:
        parsed_json = json.load(input_stream)

    economy_config = read_world(parsed_json)
    #economy = we.WageEconomy.from_config(economy_config)
    economy = le.LaborEconomy.from_config(economy_config)

    market_schema = economy.market_schema()
    pt.set_global_table_logging_from_schema(market_schema)
    p0 = np.full(market_schema.global_width(), 100.0)
    epsilon = 0.1
    participants = list(economy.participants())

    scaling = mb.ScalingConfiguration(set_to_price=10, norm_listing=market_schema.listing_of_good_in_province("food", "France"))

    config = eva.EvaConfiguration(
             epsilon=epsilon,
             rate=0.03,
             first_momentum_mixin = 0.025
    )
    p = eva.make_market(participants, p0, config)
    p = mb.apply_price_scaling(p, scaling)
    pt.pretty_table([("price", p)])
    print(f"eva iterations: {mb.get_iteration()}")
    mb.reset_iteration()

    return 0

if __name__ == '__main__':
    sys.exit(main())

