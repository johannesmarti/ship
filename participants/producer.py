import numpy as np

from typing import Tuple
import numpy.typing as npt

from participants.abstract import *

Allocation = npt.NDArray

class Producer():
    def __init__(self, workforce : float, production_matrix : npt.NDArray):
        self.production_matrix = production_matrix
        self.workforce = workforce

    def num_tasks(self):
        return self.production_matrix.shape[0]

    def supply(self, allocation : Allocation):
        return self.production_matrix.T @ np.sqrt(allocation)

    def wages(self, allocation : Allocation, prices : Prices):
        return prices @ self.supply(allocation)

    def produce(self, prices : Prices) -> Tuple[float, VolumeBundle]:
        assert(prices.size == self.production_matrix.shape[1])

        # we first remove all tasks which result in negative income if all the necessary goods are bought at current prices
    
        # compute for each task how much money it makes
        payoff_one_unit = self.production_matrix @ prices
    
        # remove money loosing tasks from the production matrix
        tasks_to_cancel = payoff_one_unit < 0
        logging.info(f"productivity: {payoff_one_unit}")
        pm = self.production_matrix.copy()
        pm[tasks_to_cancel,] = 0
    
        ep = pm @ prices
        epsq = ep * ep
        lambda_squared = np.sum(epsq)
        allocation = epsq / lambda_squared
    
        assert (allocation >= 0).all()
        assert (allocation <= 1).all()
        real_allocation = allocation * self.workforce
        supply = self.supply(real_allocation)
        return (self.wages(real_allocation, prices),
                VolumeBundle(supply, np.absolute(supply)))
