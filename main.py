import json
import logging
import sys
from typing import Iterable

import core.economy as economy
import market.eva as eva
import pretty_table as pt
import schema as schema

#np.set_printoptions(precision=3,suppress=True,threshold=12)

#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

def read_world(parsed_json: Any) -> economy.EconomyConfig:
    provinces_json = parsed_json['provinces']
    province_names = list(map(lambda h : h['name'], provinces_json))
    province_schema = schema.ProvinceSchema(province_names)
    tradable_goods_json = parsed_json['tradable_goods']
    fixed_goods_json = parsed_json['fixed_goods']
    local_schema = TradeGoodsSchema.from_list(tradable_goods, fixed_goods)

    econfig = economy.EconomyConfig(local_schema, province_schema,
                                    province_configs)
    return econfig

def set_up_merchants(home: int, foreign: int) -> Iterable[economy.TradeConfig]:
    def for_good(good: int) -> Iterable[economy.TradeConfig]:
        factor = trade_factors[good]
        return [economy.TradeConfig(good, home, foreign, factor),
                economy.TradeConfig(good, foreign, home, factor)]
    return concat_map(for_good, local_schema.trade_goods())

def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = "world.json"

    with open(filename, "r") as input_stream:
        parsed_json = json.load(input_stream)

    economy_config = read_world(parsed_json)
    #economy = we.WageEconomy.from_config(econfig)
    economy = le.LaborEconomy.from_config(economy_config)

    market_schema = economy.price_schema()
    pt.set_global_table_logging_from_schema(market_schema)
    p0 = np.full(market_schema.global_width(), 100.0)
    epsilon = 0.1
    participants = list(economy.participants())

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

    return 0

if __name__ == '__main__':
    sys.exit(main())

