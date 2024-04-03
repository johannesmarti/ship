import numpy as np

from core.bundle import *
from core.participant import *
from core.placement import Placement, LaborPlacement

def consume(utility : Bundle, budget : float, prices : Prices) -> VolumeBundle:
    assert prices.shape == utility.shape
    a = np.sum(utility / prices)
    # lambda can be interpreted as the price of 1 utility
    lambda_squared = budget / a
    solution = lambda_squared * utility / (prices * prices)
    return VolumeBundle(-solution, solution)


class SalaryConsumer():
    def __init__(self, utilities : Bundle, placement : Placement):
        self.utilities = utilities
        self.goods_slice = placement.production_slice
        
    def consume_salary(self, salary : float, prices : Prices) -> VolumeBundle:
        consumption_of_goods = consume(self.utilities, salary,
                                       prices[self.goods_slice])
        total_consumption = VolumeBundle.zero(prices.shape)
        total_consumption.add_at_slice(self.goods_slice, consumption_of_goods)
        return total_consumption


class LaborerConsumer(Participant):
    def __init__(self, utilities : Bundle, population: int,
                 placement : LaborPlacement):
        self.utilities = utilities
        self._population = population 
        self.labor_index = placement.labor_index
        self.goods_slice = placement.production_slice

    def population(self) -> int:
        return self._population

    def participate(self, prices : Prices) -> VolumeBundle:
        consumption_per_pop = consume(self.utilities, prices[self.labor_index],
                                      prices[self.goods_slice])
        consumption = self._population * consumption_per_pop
        total_consumption = VolumeBundle.zero(prices.shape)
        total_consumption.add_at_ix(self.labor_index, self._population)
        total_consumption.add_at_slice(self.goods_slice, consumption)
        return total_consumption
