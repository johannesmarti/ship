from functools import partial
from itertools import chain
import numpy as np
from typing import Any, Callable, Iterable

import core.economy as economy
import core.schema as schema
from core.schema import GoodId, ProvinceId

def read_world(json_world: Any) -> economy.EconomyConfig:
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

    def read_province(json_province: Any) -> economy.ProvinceConfig:
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
                 json_factory: Any) -> economy.FactoryConfig:
    production_coefficients = local_schema.dict_to_vector(json_factory)
    return economy.FactoryConfig(production_coefficients)

def concat_map(func: Callable[[Any], Iterable[Any]], it: Any) -> Iterable[Any]:
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

