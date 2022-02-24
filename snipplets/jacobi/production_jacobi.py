import numpy as np

from derivative import print_estimation
from production import lagrangian_production


def estimate_jacobian_diagonal(population, production_matrix, prices):
    # If a task is not performed at current prices it is completely disregarded from the computation.
    payoff_one_unit = production_matrix @ prices

    tasks_to_cancel = payoff_one_unit < 0
    production_matrix[tasks_to_cancel,] = 0

    ep = production_matrix @ prices
    epsq = ep * ep
    lambda_squared = np.sum(epsq)
    lbd = np.sqrt(lambda_squared)
    print("lambda", lbd)
    prod_squared = production_matrix * production_matrix
    return population / lbd * np.sum(prod_squared, axis=0)


prices = np.array([10.0, 20.0, 8.0, 14.0])
population = 10
production_matrix = np.array([
  [4, 0, 0, 0],
  [0, 3, 0, 0],
  [0, 0, 6, 0],
  [0, 0, 0, 3.2],
  [-4, 0, 10, 0],
])

def f_first(p):
    return lagrangian_production(population,production_matrix, p)[0][0]

def f_second(p):
    return lagrangian_production(population,production_matrix,p)[0][1]

print("for first good")
print_estimation(f_first,prices,0.0001)

print("for second good")
print_estimation(f_second,prices,0.0001)

print("approximated diagonal of jacobian", estimate_jacobian_diagonal(population, production_matrix, prices))
