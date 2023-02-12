import logging
import numpy as np

from participants.abstract import *
from placement import Placement

def consume(utility : Bundle, money : float, prices : Prices) -> VolumeBundle:
    assert prices.shape == utility.shape
    a = np.sum(utility / prices)
    # lambda can be interpreted as the price of 1 utility
    lambda_squared = money / a
    solution = lambda_squared * utility / (prices * prices)
    logging.debug(f"{-solution} consumption")
    return VolumeBundle(-solution, solution)
    

class FixedBudgetConsumer(Participant):
    def __init__(self, utility : Bundle, budget : float):
        self.utility = utility
        self.budget = budget
        
    def participate(self, prices : Prices) -> VolumeBundle:
        return consume(self.utility, self.budget, prices)


class SalaryConsumer():
    def __init__(self, utility : Bundle):
        self.utility = utility
        
    def consume_salary(self, salary : float, prices : Prices) -> VolumeBundle:
        return consume(self.utility, salary, prices)


class LabourerConsumer(Participant):
    def __init__(self, utilities : Bundle, workforce : float,
                 placement : Placement):
        self.utilities = utilities
        self.workforce = workforce
        self.labour_index = placement.labour_index
        self.goods_slice = placement.production_slice

    def participate(self, prices : Prices) -> VolumeBundle:
        salary = self.workforce * prices[self.labour_index]
        consumption_of_goods = consume(self.utilities, salary,
                                       prices[self.goods_slice])
        total_consumption = VolumeBundle.zero(prices.shape)
        total_consumption.add_at_ix(self.labour_index, self.workforce)
        total_consumption.add_at_slice(self.goods_slice, consumption_of_goods)
        return total_consumption
