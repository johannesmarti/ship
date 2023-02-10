import logging
import numpy as np

from participants.abstract import *

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
    def __init__(self, utility : Bundle, workforce : float, labour_index : int, goods_index : int):
        self.utility = utility
        self.workforce = workforce
        self.labour_index = labour_index
        self.goods_index = goods_index

    def participate(self, prices : Prices) -> VolumeBundle:
        salary = self.workforce * price[self.labour_index]
        consumption_of_goods = consume(self.utility, salary, prices)
        # need to place goods at the right ix
        consumption_of_goods.add_at_ix(self.labour_index, self.workforce)
        return consumption_of_goods
