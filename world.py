import numpy as np

from consumer import Consumer
from producer import Producer

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


        num_prices = self.num_provinces() * self.num_goods


        def trade_matrix(s, t):
            wide = np.zeros((self.num_trade_goods, num_prices + 1))
            all_goods = trade_factor * np.eye(self.num_trade_goods)
            wide[:,self.trade_slice_of_market_in_province(s)] = -all_goods
            wide[:,self.trade_slice_of_market_in_province(t)] = all_goods
            return wide

        def production_matrix_for(index):
            local = production[index]
            wide_local = np.zeros((local.shape[0],num_prices + 1))
            wide_local[:,self.slice_of_market_in_province(index)] = local[:,:-1]
            wide_local[:,-1] = local[:,-1] # append gold column at end
            
            def tm(other_market):
                return np.vstack((trade_matrix(index,other_market),trade_matrix(other_market,index)))
            
            trade_part = np.vstack(list(map(tm, trade_partners[index])))
            ret = np.vstack((wide_local,trade_part))
            assert ret.shape[1] == num_prices + 1
            return ret
            
            #production_coefficients = list(map(production_coefficients_of_group, range(num_groups)))

        self.producers = list(map(lambda i : Producer(production_matrix_for(i)), range(0,self.num_provinces())))


    def num_provinces(self):
        return len(self.province_names)

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

