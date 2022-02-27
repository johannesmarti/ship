import numpy as np
from collections import namedtuple

ProductionSolution = namedtuple('ProductionSolution', ['supply', 'income', 'allocation', 'jacobi'])

# adds an additonal entry at the end of prices which corresponds to one additional listenting for the price of gold. It's price is always 1 since prices are listed in gold.
extended_prices(prices):
    return np.append(prices, 1)

class Producer:
    def __init__(self, production_matrix):
        self.production_matrix = production_matrix

    def supply(self, allocation):
        return self.production_matrix.T @ np.sqrt(allocation)

    def income(self, allocation, extended_prices):
        return extended_prices @ self.supply(allocation)

    def produce(prices):
        assert(prices.size + 1 == self.production_matrix.shape[1])
        extended_prices = extend_prices(prices)

        # we first remove all tasks which result in negative income if all the necessary goods are bought at current prices
    
        # compute for each task how much money it makes
        payoff_one_unit = production_matrix @ extended_prices
    
        # remove money loosing tasks from the production matrix
        tasks_to_cancel = payoff_one_unit < 0
        pm = production_matrix.copy()
        pm[tasks_to_cancel,] = 0
    
        ep = pm @ extended_prices
        epsq = ep * ep
        lambda_squared = np.sum(epsq)
        allocation = epsq / lambda_squared
    
        lbd = np.sqrt(lambda_squared)
        prod_squared = pm * pm
        jacobi_diagonal = 1 / lbd * np.sum(prod_squared, axis=0)
        assert (allocation >= 0).all()
        assert (allocation <= 1).all()
        return ProductionSolution(self.supply(allocation),
                                  self.income(allocation, extended_prices),
                                  allocation,
                                  jacobi_diagonal)
