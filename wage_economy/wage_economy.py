from typing import Iterable, Callable
from itertools import chain
import numpy as np

import consumer as c
import wage_economy.balanced_producer as p
import wage_economy.village as v
from core.participant import Participant
from core.schema import MarketPriceSchema, ProvinceId
import core.economy as economy

def uncurry(function: Callable):
    return lambda args: function(*args)

class WageEconomy(economy.Economy):
    """Implements the economy interface for algorithms in which labour is not
    priced on the marked. Instead the producers in a province produce all they
    can with the available population and then the consumers use the money these
    factories get from selling their products on the market to buy goods."""

    def __init__(self, market_schema: MarketPriceSchema, villages: list[v.Village]):
        self._market_schema = market_schema
        self._villages = villages

    @classmethod
    def from_config(cls, config: economy.EconomyConfig):
        market_schema = MarketPriceSchema(config.goods_schema,
                                          config.province_schema)

        def create_village(province: ProvinceId,
                           province_config: economy.ProvinceConfig) -> v.Village:
            consumer = c.SalaryConsumer(province_config.utilities,
                                        market_schema.placement_of_province(province))

            # creating the production matrix
            def create_factory(factory_config: economy.FactoryConfig) -> np.ndarray:
                slice_of_province = market_schema.production_slice_in_province(province)
                row = np.zeros(market_schema.global_width())
                row[slice_of_province] = factory_config.production_coefficients
                return row

            factoryiter = map(create_factory, province_config.factories)

            def create_merchant(trade_config: economy.TradeConfig) -> np.ndarray:
                row = np.zeros(market_schema.global_width())
                from_listing = market_schema.good_in_province(trade_config.from_province,
                                                              trade_config.good)
                to_listing = market_schema.good_in_province(trade_config.to_province,
                                                            trade_config.good)
                trade_efficiency = trade_config.trade_factor
                row[from_listing] = -trade_efficiency
                row[to_listing] = trade_efficiency
                return row

            merchantiter = map(create_merchant, province_config.merchants)

            production_matrix = np.fromiter(chain(factoryiter, merchantiter),
                                            (float, market_schema.global_width()))

            producer = p.BalancedProducer(province_config.population, production_matrix)
            return v.Village(producer, consumer)

        villages = list(map(uncurry(create_village), enumerate(config.province_configs)))
        return cls(market_schema, villages)

    def population_in_province(self, province: ProvinceId) -> int:
        return self._villages[province].population()

    def price_width(self) -> int:
        return self._market_schema.global_width()

    def participants(self) -> Iterable[Participant]:
        return self._villages
