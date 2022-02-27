import numpy as np

from consumer import Consumer
from producer import Producer

class World:
    def __init__(self, province_config, pop_utility_coefficients):
        self.province_names = list(map(lambda h : h['name'], province_config))
        self.populations = np.array(list(map(lambda h : h['population'], province_config)))
        self.consumers = list(map(lambda h : Consumer(pop_utility_coefficients), province_config))
        self.tax_rates = np.array(list(map(lambda h : h['tax_rate'], province_config)))

        def production_matrix_for(index):
            return np.array([[4,3],[5,6]])

        self.producers = list(map(lambda i : Producer(production_matrix_for(i)), range(0,self.num_provinces()))


    def num_provinces(self):
        return len(self.province_names)

    def index_of_name(self, name):
        return self.province_names.index(name)

    def name_of_index(self, index):
        return self.province_names[index]

    def slice_of_market_in_province(i):
        s = num_goods * i
        return slice(s, s + num_goods)

