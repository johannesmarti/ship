import logging
import numpy as np

from participants.abstract import *

class Consumer(Participant):
    def __init__(self, utility : Bundle, money : float):
        self.utility = utility
        self.money = money
        
    def participate(self, prices : Prices) -> VolumeBundle:
        assert prices.shape == self.utility.shape
        a = np.sum(self.utility / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = self.money / a
        solution = lambda_squared * self.utility / (prices * prices)
        logging.debug(f"consumption: {solution}")
        return VolumeBundle(-solution, solution)
