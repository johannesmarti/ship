import numpy as np
from numpy.linalg import norm
from math import isclose

np.set_printoptions(precision=2)

from consumption import FlatConsumer, FixpointConsumer, SciPyConsumer, sqrt_utility
from production import production

"""
good_names = ["food","wood","something"]
num_goods = len(good_names)

factories = np.array([
    [-1,-1,5],
])

utility_coefficients = np.array([2,1,1])

trade_factor = 5

locations = [
{'name':        "Switzerland",
 'population':  8,
 'resources':   [
                    [1,0,0],
                    [0,2,0]
                ],
 'trade_partners': ['Italy']},

{'name':        "Italy",
 'population':  50,
 'resources':   [
                    [5,0,0],
                    [0,2,0]
                ],
 'trade_partners': ['Switzerland']}
]

"""

good_names = ["food","wool","wood","ore","weapons"]
num_goods = len(good_names)

factories = np.array([
    [0,-0.5,-1,-4,4],
])

#utility_coefficients = np.array([2,1,1,1,1])
utility_coefficients = np.array([2,1,0.7,0,1])

trade_factor = 3

locations = [
{'name':        "Switzerland",
 'population':  8,
 'resources':   [
                    [4,1,0,0,0],
                    [0,0,2,0,0],
                    [0,0,0,1,0]
                ],
 'trade_partners': ['Italy','France','Germany']},

{'name':        "Italy",
 'population':  50,
 'resources':   [
                    [5,1,0,0,0],
                    [0,0,2,0,0],
                    [0,0,0,1,0],
                    [0,4,0,0,0]
                ],
 'trade_partners': ['Switzerland','France','Spain']},

{'name':        "France",
 'population':  60,
 'resources':   [
                    [6,1,0,0,0],
                    [0,0,3,0,0],
                    [0,3,0,0,0],
                    [0,0,0,2,0]
                ],
 'trade_partners': ['Switzerland','Italy','Spain','Germany','Britain']},

{'name':        "Spain",
 'population':  40,
 'resources':   [
                    [4,1,0,0,0],
                    [0,0,1.5,0,0],
                    [0,5,0,0,0]
                ],
 'trade_partners': ['Italy', 'France', 'Britain']},

{'name':        "Netherlands",
 'population':  20,
 'resources':   [
                    [8,1,0,0,0],
                    [0,0,2,0,0]
                ],
 'trade_partners': ['France','Spain','Germany','Britain']},

{'name':        "Germany",
 'population':  80,
 'resources':   [
                    [4,1,0,0,0],
                    [0,0,4,0,0],
                    [0,0,0,2,0]
                ],
 'trade_partners': ['Switzerland','France','Netherlands','Britain']},

{'name':        "Britain",
 'population':  60,
 'resources':   [
                    [4,1,0,0,0],
                    [0,0,3,0,0],
                    [0,0,0,3,0]
                ],
 'trade_partners': ['France','Spain','Netherlands','Germany']},
]

location_name = list(map(lambda h : h['name'], locations))
def index_of_name(name):
    return location_name.index(name)

market_name = location_name
group_name = location_name

pops = np.array(list(map(lambda h : h['population'], locations)))

resources = list(map(lambda h : h['resources'], locations))

trade_partners = list(map(lambda h : list(map(index_of_name, h['trade_partners'])), locations))

num_groups = pops.size
num_markets = num_groups

def market_of_group(group):
    return group

num_prices = num_markets * num_goods
print("#goods", num_goods)
print("#markets", num_markets)
print("#prices", num_prices)

# initial prices
prices = np.full(num_prices, 20)

def slice_of_market(m):
    s = num_goods * m
    return slice(s, s + num_goods)

def trade_matrix(s, t):
    wide = np.zeros((num_goods,num_prices))
    all_goods = trade_factor * np.eye(num_goods)
    wide[:,slice_of_market(s)] = -all_goods
    wide[:,slice_of_market(t)] = all_goods
    return wide

# each group has its own production_coefficients
def production_coefficients_of_group(group):
    local = np.vstack((resources[group],factories))
    wide_local = np.zeros((local.shape[0],num_prices))
    wide_local[:,slice_of_market(market_of_group(group))] = local

    def tm(other_market):
        return np.vstack((trade_matrix(group,other_market),trade_matrix(other_market,group)))

    trade_part = np.vstack(list(map(tm, trade_partners[group])))
    ret = np.vstack((wide_local,trade_part))
    assert ret.shape[1] == num_prices
    return ret

production_coefficients = list(map(production_coefficients_of_group, range(num_groups)))

num_tasks = list(map(lambda coe: coe.shape[0], production_coefficients))

allocations = list(map(lambda nt: np.full(nt, 1/nt), num_tasks))
consumptions = np.full((num_groups,num_goods), 0.01)

def supply_per_pop(group):
    return production_coefficients[group].T @ np.sqrt(allocations[group])

consumer = FlatConsumer(utility_coefficients)
#consumer = SciPyConsumer(lambda c : sqrt_utility(utility_coefficients, c), jacobi_factor=0.001)
#consumer = FixpointConsumer(utility_coefficients)

# wages are the same as income per pop
def wages(group):
    return prices @ supply_per_pop(group)

def print_consumers(group):
    print(location_name[group], "(consumption)")
    w = wages(group)
    print("wages:", w)
    utility_per_pop = consumer.utility(consumptions[group])
    print("utility:", utility_per_pop)
    price_of_utility = w/ utility_per_pop
    print("price of utility:", price_of_utility)
    local_prices = prices[slice_of_market(group)]
    # lambda can be interpreted as the price of 1 utility
    spending = local_prices @ consumptions[group]
#    print("spending", spending)
#    print("lambda", np.sqrt(lambda_squared))
    print("local prices", local_prices)
    print("consumption", consumptions[group])
    print("utility_per_good", np.sqrt(utility_coefficients * consumptions[group]))


def one_iteration(prices):
    supply = np.zeros(num_prices)
    jacobi = np.zeros(num_prices)
    income = np.zeros(num_groups)
    for i in range(num_groups):
        res = production(production_coefficients[i],prices,allocations[i])
        supply = supply + pops[i] * res.supply
        income[i] = res.income
        allocations[i] = res.allocation
        jacobi = jacobi + pops[i] * res.jacobi
    demand = np.zeros(num_prices)
    for i in range(num_groups):
        ith_slice = slice_of_market(i)
        #res = consumption(utility_coefficients, prices[ith_slice], income[i],consumptions[i])
        res = consumer.consume(prices[ith_slice], income[i])
        demand[ith_slice] = demand[ith_slice] + pops[i] * res.consumption
        consumptions[i] = res.consumption
        jacobi[ith_slice] = jacobi[ith_slice] - pops[i] * res.jacobi

    return (supply - demand,jacobi)


#alpha = 0.5

#alpha = 0.8

#alpha = 1
#alpha = 1.2
alpha = 1.3
#alpha = 1.4
#alpha = 3
t = alpha
prev_badness = 1000000000000.0
prev_prices = prices
prev_derivative = prices
prev_error = prices
error_vector = prices
iterations = 0

while True:
    (error_vector, derivative) = one_iteration(prices)
    iterations += 1
    badness = norm(error_vector)
    #print("error_vector:", error_vector)
    print("badness:", badness, "(previous:", prev_badness, ")")
    if badness < 0.001:
        break
    elif badness > prev_badness:
        t = 0.6 * t
        print("worse! (new t =", t, ")")
        prices = prev_prices - t * (prev_error / prev_derivative)
        prices = np.maximum(prices,0.0001)
        print("now trying with", prices)
        badness = prev_badness
        error_vector = np.zeros_like(error_vector)
        assert t > 0.0001
    else:
        prev_badness = badness
        prev_prices = prices
        prev_error = error_vector
        prev_derivative = derivative
        #prices = prices - alpha * prices * error_vector
        prices = prices - t * (error_vector / derivative)
        prices = np.maximum(prices,0.0001)
        t = alpha
        print("update")
        #print("update to", prices)
        #print("badness: |" + np.array2string(error_vector) + "| =", badness)
        #print("badness:", badness)

#print("solution at:\n", np.reshape(prices,(num_markets,num_goods)))
#print("allocations:\n", allocations)
print("with", iterations, "iterations")
for i in range(num_groups):
    print_consumers(i)
    print()
