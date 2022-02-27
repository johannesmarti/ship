import numpy as np
from collections import namedtuple

def sqrt_utility(coefficients, consumption):
    return np.sum(np.sqrt(coefficients * consumption))

ConsumptionSolution = namedtuple('ConsumptionSolution', ['consumption', 'jacobi'])

class Consumer:
    def __init__(self, coefficients):
        self._coefficients = coefficients

    def utility(self, consumption):
        return sqrt_utility(self._coefficients, consumption)

    def consume(self, prices, income_per_pop):
        assert prices.shape == self._coefficients.shape
        a = np.sum(self._coefficients / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = income_per_pop / a
        solution_per_pop = lambda_squared * self._coefficients / (prices * prices)
        jacobi_diagonal = (-2) * solution_per_pop / prices
        return ConsumptionSolution(solution_per_pop, jacobi_diagonal)


