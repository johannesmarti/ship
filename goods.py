import numpy as np

class GoodsConfig:
    def __init__(self, tradable_goods, untradable_goods):
        self._num_tradable_goods = len(tradable_goods)
        self._names = tradable_goods + untradable_goods

    def num_goods(self):
        return len(self._names)

    def name_of_index(self, i):
        if i == self.num_goods() + 1:
            return 'gold'
        return self._names[i]

    def index_of_name(self, name):
        return self._names.index(name)

    def dict_to_vector(self, dictionary):
        v = np.zeros(self.num_goods())
        for name, value in dictionary.items():
            v[self.index_of_name(name)] = value
        return v
        
    def gold_dict_to_vector(self, dictionary):
        v = np.zeros(self.num_goods() + 1)
        for name, value in dictionary.items():
            if name == 'gold':
                v[-1] = value
            else:
                v[self.index_of_name(name)] = value
        return v
        
