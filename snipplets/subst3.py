import numpy as np
import scipy.optimize as so
import timeit

coefficients = np.array([0.1, 0.1, 0.1, 1, 2, 1, 1, 1.3])
num_subst = 3
subst_coefficients = np.array([0.9,0.9,0.9])
scoeff = coefficients.copy()
scoeff[0:num_subst] = scoeff[0:num_subst] + subst_coefficients

def utility(consumption):
    base_util = np.sum(np.sqrt(coefficients * consumption))
    subst_util = np.sqrt(np.sum(subst_coefficients * consumption[0:num_subst]))
    return base_util + subst_util

def negative_utility(consumption):
    return -utility(consumption)

def initial_consumption(num_goods):
    return np.full(num_goods, 0.01)

def opti_consumption(prices, income_per_pop, init=None):
    num_goods = prices.size

    if init is None:
        init = initial_consumption(num_goods)

    bounds = [(0,None) for i in range(num_goods)]
    constraints = so.LinearConstraint(prices, lb=income_per_pop, ub=income_per_pop)
    res = so.minimize(negative_utility,
                      bounds=bounds,
                      constraints=constraints,
                      x0=init)
    return res.x

def opti_subst_ratio(prices):
    pzero = prices[0]
    pminus = prices[1:]
    def czero(cminus):
        return (1000 - cminus @ pminus) / pzero

    def neg_util(cminus):
        c = np.insert(cminus, 0, czero(cminus))
        util = np.sum(np.sqrt(coefficients[0:num_subst] * c)) + np.sqrt(subst_coefficients @ c)
        return -util
    
    bounds = [(0,None) for i in range(num_subst - 1)]
    init = initial_consumption(num_subst - 1)
    res = so.minimize(neg_util,
                      bounds=bounds,
                      x0=init)
    return np.insert(res.x, 0, czero(res.x))

def subst_ratio(prices, init_c=None):
    if init_c is None:
        init_c = initial_consumption(num_subst)
        #print("initialize to", init_c)
    def ut(c):
        util = np.sum(np.sqrt(coefficients[0:num_subst] * c)) + np.sqrt(subst_coefficients @ c)
        return util
    
    def comp_delta(c):
        return (prices @ c) / ut(c)
    
    def comp_alpha(c):
        return 1 / np.sqrt(subst_coefficients @ c)
    
    def comp_c(alpha,delta):
        lower = prices - delta * alpha * subst_coefficients
        return delta * delta * coefficients[0:num_subst] / (lower * lower)

    c = init_c
    for i in range(3):
        alpha = comp_alpha(c)
        delta = comp_delta(c)
        c = comp_c(alpha,delta)
        c = c * (1000/(c@prices))

    return c


def consumption(prices, income_per_pop):
    subst_prices = prices[0:num_subst]
    flat_prices = prices[num_subst:]
    subst_c = subst_ratio(subst_prices)
    alpha = np.sum(np.sqrt(coefficients[0:num_subst] * subst_c)) + np.sqrt(subst_coefficients @ subst_c)
    a = np.sum(coefficients[num_subst:] / flat_prices)
    b = alpha * alpha / (subst_prices @ subst_c)
    # lambda can be interpreted as the price of 1 utility
    lambda_squared = income_per_pop / (b + a)
    flat_solution = lambda_squared * coefficients[num_subst:] / (flat_prices * flat_prices)
    r = lambda_squared * (alpha/(subst_prices @ subst_c)) ** 2
    solution = np.concatenate([r * subst_c, flat_solution])

    jacobi_diagonal = (-2) * (lambda_squared * scoeff /(prices * prices * prices))

    #return ConsumptionSolution(solution_per_pop, jacobi_diagonal)
    return solution


prices = np.array([5,20,15,8,12,11,11, 8])
c = opti_consumption(prices, 10)
print(c, "consumption at income 10 and prices", prices)

prices = np.array([10,10,10,10,12,11,11, 8])
c = opti_consumption(prices, 1000)
print(c, "consumption at income 1000 and prices", prices)

prices = np.array([11,9,18,9,12,11,11, 8])
c = opti_consumption(prices, 1000)
print(c, "consumption at income 1000 and prices", prices)

prices = np.array([9,11,10,9,12,11,11, 8])
c = opti_consumption(prices, 1000)
print(c, "consumption with utility", utility(c), "at income", c @ prices, "and prices", prices)
cplus = consumption(prices, 1000)
print(cplus, "consumption with utilty", utility(cplus), "at income", cplus @ prices, "and prices", prices)


print("")
t = timeit.timeit('opti_subst_ratio(prices[:num_subst])', number=5000, globals=globals()) 
print(t, "for opti")
t = timeit.timeit('subst_ratio(prices[:num_subst])', number=5000, globals=globals()) 
print(t, "for lagrange")
