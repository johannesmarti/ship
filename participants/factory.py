import logging
import numpy as np

from typing import Tuple

from participants.abstract import *

def produce(name : str, production_coefficients : Bundle, wage_per_worker : float, prices : Prices) -> Tuple[float, VolumeBundle]:
    income_rate = production_coefficients @ prices
    if (income_rate <= 0):
        logging.debug(f"{name}: income_rate: {income_rate}")
        return (0,VolumeBundle.zero(prices.shape))
    else:
        sqrt_workforce = income_rate / wage_per_worker
        supply = production_coefficients * sqrt_workforce
        logging.debug(f"{name}: production: {supply}")
        return (sqrt_workforce**2, VolumeBundle(supply, np.absolute(supply)))

class UncompetitiveFactory(Participant):
    def __init__(self, name : str, production_coefficients : Bundle, wage_per_worker : float):
        self.production_coefficients = production_coefficients
        self.wage_per_worker = wage_per_worker
        self.name = name
    
    def participate(self, prices : Prices) -> VolumeBundle:
        (_,res) = produce(self.name, self.production_coefficients,
                          self.wage_per_worker, prices)
        return res

class Factory(Participant):
    def __init__(self, name : str, production_coefficients : Bundle,
                 labour_index : int, goods_slice : slice):
        self.name = name 
        self.production_coefficients = production_coefficients
        self.labour_index = labour_index
        self.goods_slice = goods_slice

    def participate(self, prices : Prices) -> VolumeBundle:
        (wf,res) = produce(self.name, self.production_coefficients,
                           price[self.labour_index], prices[self.goods_slice])
        consumption_of_goods = consume(self.utilities, salary,
                                       prices[self.goods_slice])
        total_consumption = VolumeBundle.zero(prices.shape)
        total_consumption.add_at_ix(self.labour_index, wf)
        total_consumption.add_at_slice(self.goods_slice, consumption_of_goods)
        return total_consumption

# Example
# 
# ======
# 1 production gives 10 E
# 1 salary = 10
# 
# 1 workers cost 10 E
# produce 1 for 10 E
# 
# 4 workers cost 40 E
# produce 2 for 20 E
# 
# ======
# 1 production gives 20 E
# 1 salary = 10
# 
# 4 workers cost 40 E
# produce 2 for 40 E
# 
# ======
# 1 production gives 40 E
# 1 salary = 10
# 
# 16 workers cost 160 E
# produce 4 for 160 E
# 
# ======
# 1 production gives 50 E
# 1 salary = 10
# 
# 25 workers cost 250 E
# produce 5 for 250 E
# 



