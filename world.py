import numpy as np
from collections import namedtuple

from consumer import Consumer
from producer import Producer

Equilibrium = namedtuple('Equilibrium', ['prices', 'allocations', 'consumptions'])

class World:
    def __init__(self, province_config, pop_utility_coefficients, trade_factor, num_trade_goods=None):

        self.num_goods = pop_utility_coefficients.shape[0]
        if num_trade_goods is None:
            num_trade_goods = self.num_goods
        self.num_trade_goods = num_trade_goods
        self.province_names = list(map(lambda h : h['name'], province_config))
        self.populations = np.array(list(map(lambda h : h['population'], province_config)))
        self.consumers = list(map(lambda h : Consumer(pop_utility_coefficients), province_config))
        self.tax_rates = np.array(list(map(lambda h : h['tax_rate'], province_config)))

        production = list(map(lambda h : np.array(h['production']), province_config))
        trade_partners = list(map(lambda h : list(map(self.index_of_name, h['trade_partners'])), province_config))


        self.num_prices = self.num_provinces() * self.num_goods


        def trade_matrix(s, t):
            wide = np.zeros((num_trade_goods, self.num_prices + 1))
            all_goods = trade_factor * np.eye(self.num_trade_goods)
            wide[:,self.trade_slice_of_market_in_province(s)] = -all_goods
            wide[:,self.trade_slice_of_market_in_province(t)] = all_goods
            return wide

        def production_matrix_for(index):
            local = production[index]
            wide_local = np.zeros((local.shape[0],self.num_prices + 1))
            wide_local[:,self.slice_of_market_in_province(index)] = local[:,:-1]
            wide_local[:,-1] = local[:,-1] # append gold column at end
            
            def tm(other_market):
                return np.vstack((trade_matrix(index,other_market),trade_matrix(other_market,index)))
            
            trade_part = np.vstack(list(map(tm, trade_partners[index])))
            ret = np.vstack((wide_local,trade_part))
            assert ret.shape[1] == self.num_prices + 1
            return ret
            
        self.producers = list(map(lambda i : Producer(production_matrix_for(i)), range(0,self.num_provinces())))


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


    def num_provinces(self):
        return len(self.province_names)

    def num_provinces(self):
        return self.num_goods

    def num_prices(self):
        return self.num_prices

    def index_of_name(self, name):
        return self.province_names.index(name)

    def name_of_index(self, index):
        return self.province_names[index]

    def slice_of_market_in_province(self, i):
        s = self.num_goods * i
        return slice(s, s + self.num_goods)

    def trade_slice_of_market_in_province(self, i):
        s = self.num_goods * i
        return slice(s, s + self.num_trade_goods)

    def consumer(self, i)
        return self.consumers[i]

    def producer(self, i)
        return self.producers[i]



def find_equilibrium(world, prices=None, alpha=1.2):
    if prices is None:
        prices = np.full(world.num_prices(), 20)
    assert(prices.size == world.num_prices())

    allocations = list(map(lambda nt: np.full(nt, 1/nt), num_tasks))
    consumptions = np.full((world.num_provinces(),world.num_goods()), 0.01)

    t = alpha
    prev_badness = 1000000000000.0
    prev_prices = prices
    prev_derivative = prices
    prev_error = prices
    error_vector = prices
    iterations = 0

    while True:
        (error_vector, derivative) = world.one_iteration(prices)
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

    return Equilibrium(prices, allocations, consumptions)
