from typing import List, Iterable, Callable
from itertools import chain
import math
import numpy as np

import consumer as c
import fast_labor_economy.producer as p
from core.participant import Participant
from core.schema import LaborTradeGoodsSchema, LaborMarketPriceSchema, ProvinceId
import core.economy as economy

def uncurry(function: Callable):
    return lambda args: function(*args)

class LaborEconomy(economy.Economy):
    """
    Implements the economy interface for algorithms in which labor is one of
    the goods that is priced by the market.
    """

    def __init__(self, market_schema: LaborMarketPriceSchema,
                       consumers: List[c.LaborerConsumer],
                       producers: p.Producers):
        self._market_schema = market_schema
        self._consumers = consumers
        self._producers = producers

    @classmethod
    def from_config(cls, config: economy.EconomyConfig):
        market_schema = LaborMarketPriceSchema(
            LaborTradeGoodsSchema(config.goods_schema),
            config.province_schema)

        def create_consumer(province: ProvinceId,
                            config: economy.ProvinceConfig) -> c.LaborerConsumer:
            return c.LaborerConsumer(config.utilities, config.population,
                                     market_schema.labor_placement_of_province(province))
        consumers = list(map(uncurry(create_consumer), enumerate(config.province_configs)))

        def production_rows_for_province(province: ProvinceId,
                                         province_config: economy.ProvinceConfig
                                        ) -> Iterable[np.ndarray]:
            sqrt_population = math.sqrt(province_config.population)
            def create_factory(factory_config: economy.FactoryConfig) -> np.ndarray:
                slice_of_province = market_schema.production_slice_in_province(province)
                row = np.zeros(market_schema.global_width())
                # need to scale the production coefficients such that factories
                # in big provinces can produce with the same efficiency per
                # worker as factories in small provinces. We can think of this
                # as meaning that big provinces have larger factories.
                coefficients = sqrt_population * factory_config.production_coefficients
                row[slice_of_province] = coefficients
                return row
            factoryiter = map(create_factory, province_config.factories)

            def create_trader(trade_config: economy.TradeConfig) -> np.ndarray:
                row = np.zeros(market_schema.global_width())
                from_listing = market_schema.good_in_province(trade_config.good,
                                                              trade_config.from_province)
                to_listing = market_schema.good_in_province(trade_config.good,
                                                            trade_config.to_province)
                trade_efficiency = sqrt_population * trade_config.trade_factor
                row[from_listing] = -trade_efficiency
                row[to_listing] = trade_efficiency
                return row
            traderiter = map(create_trader, province_config.merchants)
            return chain(factoryiter, traderiter)

        nested_producers = map(uncurry(production_rows_for_province),
                               enumerate(config.province_configs))
        production_iter = chain(*nested_producers)
        production_matrix = np.fromiter(production_iter,
                                        (float, market_schema.global_width()))

        def labor_indices_for_province(province: ProvinceId,
                                       province_config: economy.ProvinceConfig
                                      ) -> Iterable[int]:
            labor_index = market_schema.labor_placement_of_province(province).labor_index
            def create_factory(factory_config: economy.FactoryConfig) -> int:
                return labor_index
            factoryiter = map(create_factory, province_config.factories)

            def create_trader(trade_config: economy.TradeConfig) -> int:
                return labor_index
            traderiter = map(create_trader, province_config.merchants)
            return chain(factoryiter, traderiter)
        nested_indices = map(uncurry(labor_indices_for_province),
                             enumerate(config.province_configs))
        index_iter = chain(*nested_indices)
        labor_indices = np.fromiter(index_iter, int)

        producers = p.Producers(production_matrix, labor_indices)

        return cls(market_schema, consumers, producers)

    def population_in_province(self, province: ProvinceId) -> int:
        return self._consumers[province].population()

    def market_schema(self) -> LaborMarketPriceSchema:
        return self._market_schema

    def participants(self) -> Iterable[Participant]:
        return chain(self._consumers, [self._producers])
