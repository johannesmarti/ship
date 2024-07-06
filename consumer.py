import numpy as np

from core.bundle import *
from core.participant import *
from core.placement import Placement, LaborPlacement

def consume(utility: Bundle, budget: float, prices: Prices) -> VolumeBundle:
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

class Consumers(Participant):
    def __init__(self, populations: np.ndarray, coefficient_matrix: np.ndarray,
                       labor_indices: np.ndarray):
        self._populations = populations
        self._coefficient_matrix = coefficient_matrix
        self._labor_indices = labor_indices

    def participate(self, prices: Prices) -> VolumeBundle:
        incomes_per_pop = prices[self._labor_indices]
        # this will broadcast the vector along the rows:
        preas = self._coefficient_matrix / prices
        a = np.sum(preas, axis=1)
        lambda_squared = incomes_per_pop / a
        # this will broadcast the vector along the rows:
        pre_div = self._coefficient_matrix / (prices * prices)
        pre_solution = pre_div * lambda_squared[:, np.newaxis]
        solution = np.sum(pre_solution * self._populations[:, np.newaxis], axis=0)
        labor_supply = np.zeros(prices.shape)
        labor_supply[self._labor_indices] = self._populations

        return VolumeBundle(-solution + labor_supply, solution + labor_supply)
