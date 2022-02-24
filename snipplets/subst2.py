import numpy as np
import scipy.optimize as so

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

def consumption(prices, income_per_pop):
    subst_prices = prices[0:num_subst]
    flat_prices = prices[num_subst:]
    subst_c = opti_subst_ratio(subst_prices)
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

prices = np.array([9,11,18,9,12,11,11, 8])
c = opti_consumption(prices, 1000)
print(c, "consumption with utility", utility(c), "at income 1000 and prices", prices)
cplus = consumption(prices, 1000)
print(cplus, "consumption with utilty", utility(cplus), "at income 1000 and prices", prices)

def ut(c):
    util = np.sum(np.sqrt(coefficients[0:num_subst] * c)) + np.sqrt(subst_coefficients @ c)
    return util

def delta(c):
    subst_prices = prices[0:num_subst]
    return (subst_prices @ c) / ut(c)

def x(c):
    return 1 / np.sqrt(subst_coefficients @ c)

def cs(x,delta):
    subst_prices = prices[0:num_subst]
    lower = subst_prices - delta * x * subst_coefficients
    return delta * delta * coefficients[0:num_subst] / (lower * lower)
    
subst_prices = prices[0:num_subst]
realc = opti_subst_ratio(prices[0:num_subst])

initc = realc
x0 = x(initc)
d0 = delta(initc)
c0 = cs(x0,d0)
print("x:", x0, "delta:", d0, "cs:", c0)

print()
#initc = np.array([10,100,10000000])
initc = np.array([1,1,1])
ic = initc * (1000/(initc@subst_prices))

x0 = x(ic)
d0 = delta(ic)
c = cs(x0,d0)
c0 = c * (1000/(c@subst_prices))
print("x:", x0, "delta:", d0, "cs:", c0)

x1 = x(c0)
d1 = delta(c0)
c = cs(x1,d1)
c1 = c * (1000/(c@subst_prices))
print("x:", x1, "delta:", d1, "cs:", c1)

x2 = x(c1)
d2 = delta(c1)
c = cs(x2,d2)
c2 = c * (1000/(c@subst_prices))
print("x:", x2, "delta:", d2, "cs:", c2)

x3 = x(c2)
d3 = delta(c2)
c = cs(x3,d3)
c3 = c * (1000/(c@subst_prices))
print("x:", x3, "delta:", d3, "cs:", c3)

x4 = x(c3)
d4 = delta(c3)
c = cs(x4,d4)
c4 = c * (1000/(c@subst_prices))
print("x:", x4, "delta:", d4, "cs:", c4)

x5 = x(c4)
d5 = delta(c4)
c = cs(x5,d5)
c5 = c * (1000/(c@subst_prices))
print("x:", x5, "delta:", d5, "cs:", c5)

x6 = x(c5)
d6 = delta(c5)
c = cs(x6,d6)
c6 = c * (1000/(c@subst_prices))
print("x:", x6, "delta:", d6, "cs:", c6)

x7 = x(c6)
d7 = delta(c6)
c = cs(x7,d7)
c7 = c * (1000/(c@subst_prices))
print("x:", x7, "delta:", d7, "cs:", c7)

x8 = x(c7)
d8 = delta(c7)
c = cs(x8,d8)
c8 = c * (1000/(c@subst_prices))
print("x:", x8, "delta:", d8, "cs:", c8)

intc = c3 * (1000/(c3@subst_prices))
print("realc:", realc, "with util", ut(realc), "spending", realc@subst_prices)
print("intc:", intc, "with util", ut(intc), "spending", intc@subst_prices)
print("better by:", (ut(intc) - ut(realc)) * 100)
finalc = c8 * (1000/(c8@subst_prices))
print("finalc:", finalc, "with util", ut(finalc), "spending", finalc@subst_prices)
print("better by:", (ut(finalc) - ut(realc)) * 100)
