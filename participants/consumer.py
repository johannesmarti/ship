import logging
import numpy as np

from participants.abstract import *

def consume(utility : Bundle, money : float, prices : Prices) -> VolumeBundle:
    assert prices.shape == utility.shape
    a = np.sum(utility / prices)
    # lambda can be interpreted as the price of 1 utility
    lambda_squared = money / a
    solution = lambda_squared * utility / (prices * prices)
    logging.debug(f"consumption: {solution}")
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
