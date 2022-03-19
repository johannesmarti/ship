import numpy as np
from numpy.linalg import norm
from collections import namedtuple

from consumer import Consumer
from producer import Producer

AllocationAtPrices = namedtuple('AllocationAtPrices', ['error_vector', 'derivative', 'allocations', 'consumptions'])

Equilibrium = namedtuple('Equilibrium', ['prices', 'values'])

class World:
    def __init__(self, province_config, pop_utility_coefficients, trade_factor, num_trade_goods=None):

        self._num_goods = pop_utility_coefficients.shape[0]
        if num_trade_goods is None:
            num_trade_goods = self.num_goods
        self._num_trade_goods = num_trade_goods
        self.province_names = list(map(lambda h : h['name'], province_config))
        self.populations = np.array(list(map(lambda h : h['population'], province_config)))
        self.consumers = list(map(lambda h : Consumer(pop_utility_coefficients), province_config))
        self.tax_rates = np.array(list(map(lambda h : h['tax_rate'], province_config)))

        production = list(map(lambda h : np.array(h['production']), province_config))
        trade_partners = list(map(lambda h : list(map(self.index_of_name, h['trade_partners'])), province_config))



        def trade_matrix(s, t):
            wide = np.zeros((self._num_trade_goods, self.num_prices() + 1))
            all_goods = trade_factor * np.eye(self._num_trade_goods)
            wide[:,self.trade_slice_of_market_in_province(s)] = -all_goods
            wide[:,self.trade_slice_of_market_in_province(t)] = all_goods
            return wide

        def production_matrix_for(index):
            local = production[index]
            wide_local = np.zeros((local.shape[0],self.num_prices() + 1))
            wide_local[:,self.slice_of_market_in_province(index)] = local[:,:-1]
            wide_local[:,-1] = local[:,-1] # append gold column at end
            
            def tm(other_market):
                return np.vstack((trade_matrix(index,other_market),trade_matrix(other_market,index)))
            
            trade_part = np.vstack(list(map(tm, trade_partners[index])))
            ret = np.vstack((wide_local,trade_part))
            assert ret.shape[1] == self.num_prices() + 1
            return ret
            
        self.producers = list(map(lambda i : Producer(production_matrix_for(i)), range(0,self.num_provinces())))


    def one_iteration(self, prices):
        supply = np.zeros(self.num_prices())
        jacobi = np.zeros(self.num_prices())
        income = np.zeros(self.num_provinces())
        allocations = list(map(lambda i: self.producer(i).allocation_vector(), range(self.num_provinces())))
        consumptions = np.full((self.num_provinces(), self.num_goods()), 0.01)
        for i in range(self.num_provinces()):
            res = self.producer(i).produce(prices)
            supply = supply + self.population(i) * res.supply
            income[i] = res.income * (1 - self.tax_rates[i])
            allocations[i] = res.allocation
            jacobi = jacobi + self.population(i) * res.jacobi
        demand = np.zeros(self.num_prices())
        for i in range(self.num_provinces()):
            ith_slice = self.slice_of_market_in_province(i)
            res = self.consumer(i).consume(prices[ith_slice], income[i])
            demand[ith_slice] = demand[ith_slice] + self.population(i) * res.consumption
            consumptions[i] = res.consumption
            jacobi[ith_slice] = jacobi[ith_slice] - self.population(i) * res.jacobi
    
        return AllocationAtPrices(supply - demand, jacobi, allocations, consumptions)


    def num_provinces(self):
        return len(self.province_names)

    def num_goods(self):
        return self._num_goods

    def num_prices(self):
        return self.num_provinces() * self.num_goods()

    def index_of_name(self, name):
        return self.province_names.index(name)

    def name_of_index(self, index):
        return self.province_names[index]

    def slice_of_market_in_province(self, i):
        ng = self.num_goods()
        s = ng * i
        return slice(s, s + ng)

    def trade_slice_of_market_in_province(self, i):
        ng = self.num_goods()
        s = ng * i
        return slice(s, s + self._num_trade_goods)

    def consumer(self, i):
        return self.consumers[i]

    def producer(self, i):
        return self.producers[i]

    def population(self, i):
        return self.populations[i]

    def find_equilibrium(self, prices=None, alpha=1.2):
        if prices is None:
            prices = np.full(self.num_prices(), 20)
        assert(prices.size == self.num_prices())
    
        t = alpha
        prev_badness = 1000000000000.0
        prev_prices = prices
        prev_derivative = prices
        prev_error = prices
        error_vector = prices
        iterations = 0
    
        while True:
            res = self.one_iteration(prices)
            error_vector = res.error_vector
            derivative = res.derivative
            iterations += 1
            badness = norm(error_vector)
            #print("error_vector:", error_vector)
            print("badness:", badness, "(previous:", prev_badness, ")")
            if badness < 0.01:
                break
            elif badness > prev_badness and t > 1:
                #t = 0.6 * t
                t = 0.6
                print("worse! (new t =", t, ")")
                prices = prev_prices - t * (prev_error / prev_derivative)
                #prices = np.maximum(prices,0.0001)
                #print("now trying with", prices)
                #print("had            ", prev_prices)
                #print("derivative     ", prev_derivative)
                print("error_vector   ", error_vector)
                badness = prev_badness
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
    
        return Equilibrium(prices, res)
