from typing import List, Iterable, Callable
from itertools import chain

import consumer as c
import labor_market.producer as p
from core.participant import Participant
from core.schema import LaborTradeGoodsSchema, LaborMarketPriceSchema, ProvinceId
import core.economy as economy

def uncurry(function: Callable):
    return lambda args: function(*args)

class LaborEconomy(economy.Economy):
    """Implements the economy interface for algorithms in which labor is one of
    the goods that is priced by the market."""

    def __init__(self, market_schema: LaborMarketPriceSchema, consumers: List[c.LaborerConsumer],
                 factories: List[p.Producer], traders: List[p.Producer]):
        self._market_schema = market_schema
        self._consumers = consumers
        self._factories = factories
        self._traders = traders

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

        def create_factories(province: ProvinceId,
                             config: economy.ProvinceConfig
                            ) -> Iterable[p.Producer]:
            def create_factory(factory_config: economy.FactoryConfig) -> p.Producer:
                labor_index = market_schema.labor_placement_of_province(province)
                return p.Producer.factory("factory without name",
                                          factory_config.production_coefficients,
                                          labor_index)
            return map(create_factory, config.factories)
        nested_factories = map(uncurry(create_factories), enumerate(config.province_configs))
        factories = list(chain(*nested_factories))

        def create_traders(province: ProvinceId, config: economy.ProvinceConfig
                          ) -> Iterable[p.Producer]:
            def create_trader(trade_config: economy.TradeConfig) -> p.Producer:
                from_listing = market_schema.good_in_province(trade_config.from_province,
                                                              trade_config.good)
                to_listing = market_schema.good_in_province(trade_config.to_province,
                                                            trade_config.good)
                return p.Producer.trader("trader without name",
                                         market_schema.labour_in_province(province),
                                         from_listing, to_listing,
                                         trade_config.trade_factor,
                                         market_schema.global_width())
            return map(create_trader, config.merchants)
        nested_traders = map(uncurry(create_traders), enumerate(config.province_configs))
        traders = list(chain(*nested_traders))

        return cls(market_schema, consumers, factories, traders)

    def population_in_province(self, province: ProvinceId) -> int:
        return self._consumers[province].population()

    def price_width(self) -> int:
        return self._market_schema.global_width()

    def participants(self) -> Iterable[Participant]:
        return chain(self._consumers, self._factories, self._traders)
