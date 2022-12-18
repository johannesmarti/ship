import logging
import numpy as np

from market.types import *

class Consumers:
    def __init__(self, utility : Bundle, money : float):
        self.utility = utility
        self.money = money
        
    def participate_with_volume(self, prices : Prices) -> Tuple[Bundle,Bundle]:
        assert prices.shape == self.utility.shape
        a = np.sum(self.utility / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = self.money / a
        solution = lambda_squared * self.utility / (prices * prices)
        logging.debug(f"consumption: {solution}")
        return (-solution, solution)

