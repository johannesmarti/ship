import pytest

import numpy as np

import core.economy as economy
import wage_economy.wage_economy as we
import labor_economy.labor_economy as le
import fast_labor_economy.labor_economy as ne
from market.eva import *
import market.base as mb
from core.schema import ProvinceSchema, TradeGoodsSchema
from itertools import chain

import logging

@pytest.fixture
def config():
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
    
    config = economy.EconomyConfig(local_schema, province_schema, province_configs)
    return config


def test_labor_against_wages(config):
    wecon = we.WageEconomy.from_config(config)
    wpart = list(wecon.participants())
    wschema = wecon.market_schema()
    lecon = le.LaborEconomy.from_config(config)
    lpart = list(lecon.participants())
    lschema = lecon.market_schema()

    p0 = np.full(wschema.global_width(), 10)
    pw = make_market(wpart, p0).price

    reset_iteration()

    p0 = np.full(lschema.global_width(), 10)
    pl = make_market(lpart, p0).price

    wscaling = mb.ScalingConfiguration(
        set_to_price=10,
        norm_listing=wschema.listing_of_good_in_province("food", "Italy"))

    lscaling = mb.ScalingConfiguration(
        set_to_price=10,
        norm_listing=lschema.listing_of_good_in_province("food", "Italy"))

    pw = mb.apply_price_scaling(pw, wscaling)
    pl = mb.apply_price_scaling(pl, lscaling)

    assert np.isclose(pw[wschema.production_slice_in_province(0)], pl[lschema.production_slice_in_province(0)]).all()
    assert np.isclose(pw[wschema.production_slice_in_province(1)], pl[lschema.production_slice_in_province(1)]).all()

def test_vectorized_labor(config):
    lecon = le.LaborEconomy.from_config(config)
    lpart = list(lecon.participants())
    lschema = lecon.market_schema()
    necon = ne.LaborEconomy.from_config(config)
    npart = list(necon.participants())
    nschema = necon.market_schema()


    p0 = np.full(lschema.global_width(), 10)
    pl = make_market(lpart, p0).price

    p0 = np.full(nschema.global_width(), 10)
    pn = make_market(npart, p0).price

    lscaling = mb.ScalingConfiguration(
        set_to_price=10,
        norm_listing=lschema.listing_of_good_in_province("food", "Italy"))

    nscaling = mb.ScalingConfiguration(
        set_to_price=10,
        norm_listing=nschema.listing_of_good_in_province("food", "Italy"))

    pl = mb.apply_price_scaling(pl, lscaling)
    pn = mb.apply_price_scaling(pn, nscaling)

    assert np.isclose(pl[lschema.production_slice_in_province(0)], pn[nschema.production_slice_in_province(0)]).all()
    assert np.isclose(pl[lschema.production_slice_in_province(1)], pn[nschema.production_slice_in_province(1)]).all()

