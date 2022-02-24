import numpy as np

from derivative import estimate_jacobian, print_estimation
from consumption import lagrangian_consumption


def estimate_jacobian_diagonal(population, prices, income):
    income_per_pop = income / population
    a = np.sum(1 / prices)
    # lambda can be interpreted as the price of 1 utility
    lambda_squared = income_per_pop / a
    return (-2) * population * (lambda_squared/(prices * prices * prices))


prices = np.array([20.0, 12.0, 15.0, 20.0, 29.0, 15.6, 11.1])
population = 10
income = 380

def f_first(p):
    return lagrangian_consumption(population,p,income)[0][0]

def f_second(p):
    return lagrangian_consumption(population,p,income)[0][1]


print("for first good")
print_estimation(f_first,prices,0.0001)

print("for second good")
print_estimation(f_second,prices,0.0001)

print("approximated diagonal of jacobian", estimate_jacobian_diagonal(population, prices, income))
