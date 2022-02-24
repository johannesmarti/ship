import numpy as np
import scipy.optimize as so

def utility(consumption):
    return np.sum(np.sqrt(consumption)) + np.sqrt(np.sum(consumption))

def negative_utility(consumption):
    return -utility(consumption)

def initial_consumption(num_goods):
    return np.full(num_goods, 0.01)

def local_consumption(prices, income_per_pop, init=None):
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


prices = np.array([10,20])

def test(c0,income):
    c1 = (income - prices[0]*c0) / prices[1]
    consumption = np.array([c0,c1])
    print(utility(consumption), "\t", c0/c1, consumption)

test(0.8128,10)
test(0.81281,10)
test(0.81282,10)

test(3.249,40)
test(3.25,40)
test(3.251,40)
test(3.252,40)

rv = local_consumption(prices,40)
ru = local_consumption(prices,45)
rh = local_consumption(prices,50)


r1 = local_consumption(prices,100)
r2 = local_consumption(prices,200)
r3 = local_consumption(prices,300)

rx = local_consumption(prices,1000)
ry = local_consumption(prices,100000)

print("rv", rv, "ratio", rv[0]/rv[1])
print("ru", ru, "ratio", ru[0]/ru[1])
print("rh", rh, "ratio", rh[0]/rh[1])

print("r1", r1, "ratio", r1[0]/r1[1])
print("r2", r2, "ratio", r2[0]/r2[1])
print("r3", r3, "ratio", r3[0]/r3[1])

print("rx", rx, "ratio", rx[0]/rx[1])
print("ry", ry, "ratio", ry[0]/ry[1])

# it seems that the opimal mixing ration is independent of income at 8.68...
