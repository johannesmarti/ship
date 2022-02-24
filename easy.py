import numpy as np
from numpy.linalg import norm
from math import isclose

#np.set_printoptions(precision=4)

from consumption import FlatConsumer, FixpointConsumer, SciPyConsumer, sqrt_utility
from production import production

good_names = ["food","wool","wood"]
num_goods = len(good_names)

factories = np.zeros((0,3))
#factories = np.array([
#    [0,-0.5,-1,-4,4],
#])

utility_coefficients = np.array([2,1,0.7])

trade_factor = 3

locations = [
{'name':        "Switzerland",
 'population':  8,
 'resources':   [
                    [4,1,0],
                    [0,0,2.5],
                ],
 'trade_partners': ['Italy']},

{'name':        "Italy",
 'population':  50,
 'resources':   [
                    [5,1,0],
                    [0,0,2],
                    [0,4,0]
                ],
 'trade_partners': ['Switzerland']},
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
#prices = np.array([20,20,20,33,45,
#                   20,20,20,33,45])

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
    new_prices = np.zeros(num_prices)
    income = np.zeros(num_groups)
    print("old prices", prices)
    for i in range(num_groups):
        res = production(production_coefficients[i],prices,allocations[i])
        supply = supply + pops[i] * res.supply
        income[i] = res.income
        allocations[i] = res.allocation

    print("supply", supply)
    print("allocations[0]", allocations[0])
    print("allocations[1]", allocations[1])
    supply = np.maximum(0.000001,supply)
    for i in range(num_groups):
        ith_slice = slice_of_market(i)
        #res = consumption(utility_coefficients, prices[ith_slice], income[i],consumptions[i])
        new_prices[ith_slice] = consumer.supply_to_prices(income[i], (supply[ith_slice])/pops[i])
        consumptions[i] = supply[ith_slice]

    #print("new prices", new_prices)
    return new_prices

iterations = 0

while True:
    iterations += 1
    new_prices = one_iteration(prices)
    difference = prices - new_prices
    badness = norm(difference)
    #print("error_vector:", error_vector)
    print("badness:", badness)
    if badness < 0.001:
        break
    else:
        from_new = 1/(1.5 + badness)
        prices = from_new*new_prices + (1-from_new)*prices

#print("solution at:\n", np.reshape(prices,(num_markets,num_goods)))
#print("allocations:\n", allocations)
print("with", iterations, "iterations")
for i in range(num_groups):
    print_consumers(i)
    print()
