import numpy as np
from collections import namedtuple

ProductionSolution = namedtuple('ProductionSolution', ['supply', 'income', 'allocation', 'jacobi'])

def production(production_matrix, prices, initial=None):
    # we first remove all tasks which result in negative income if all the necessary goods are bought at current prices

    # compute for each task how much money it makes
    payoff_one_unit = production_matrix @ prices

    # remove money loosing tasks from the production matrix
    tasks_to_cancel = payoff_one_unit < 0
    pm = production_matrix.copy()
    pm[tasks_to_cancel,] = 0

    def supply(allocation):
        return pm.T @ np.sqrt(allocation)

    def income(allocation):
        return prices @ supply(allocation)

    ep = pm @ prices
    epsq = ep * ep
    lambda_squared = np.sum(epsq)
    allocation = epsq / lambda_squared

    lbd = np.sqrt(lambda_squared)
    prod_squared = pm * pm
    jacobi_diagonal = 1 / lbd * np.sum(prod_squared, axis=0)
    if not ((allocation >= 0).all()):
        print("production allocations:")
        print(allocation)
    assert (allocation >= 0).all()
    return ProductionSolution(supply(allocation),
                              income(allocation),
                              allocation,
                              jacobi_diagonal)
