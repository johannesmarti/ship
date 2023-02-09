import logging
import numpy as np

from participants.abstract import *

class Factory(Participant):
    def __init__(self, name : str, production_coefficient : Bundle, labor_cost : float):
        self.production_coefficient = production_coefficient
        self.labor_cost = labor_cost
        self.name = name
    
    def participate(self, prices : Prices) -> VolumeBundle:
        income_rate = self.production_coefficient @ prices
        if (income_rate <= 0):
            logging.debug(f"{self.name}: income_rate: {income_rate}")
            return VolumeBundle.zero(prices.shape)
        else:
            sqrt_workforce = income_rate / self.labor_cost
            supply = self.production_coefficient * sqrt_workforce
            logging.debug(f"{self.name}: production: {supply}")
            return VolumeBundle(supply, np.absolute(supply))


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



