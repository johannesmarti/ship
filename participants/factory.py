import logging
import numpy as np

from market.types import *

class Factory:
    def __init__(self, production_coefficient : Bundle, labor_cost : float):
    	self.production_coefficient = production_coefficient
    	self.labor_cost = labor_cost
    
    def participate_with_volume(self, prices : Prices) -> Tuple[Bundle,Bundle]:
        income_rate = self.production_coefficient @ prices
        if (income_rate <= 0):
            return (np.zeros(prices.shape), np.zeros(prices.shape))
        else:
            sqrt_workforce = income_rate / self.labor_cost
            supply = self.production_coefficient * sqrt_workforce
            logging.debug(f"production: {supply}")
            return (supply, np.absolute(supply))

    def participate_and_estimate(self, prices : Prices) -> ElasticBundle:
        income_rate = self.production_coefficient @ prices
        if (income_rate <= 0):
            return (np.zeros(prices.shape), np.zeros(prices.shape))
        else:
            sqrt_workforce = income_rate / self.labor_cost
            supply = self.production_coefficient * sqrt_workforce
            logging.debug(f"production: {supply}")

            elasticity = (self.production_coefficient ** 2) / self.labor_cost

            return ElasticBundle(supply, elasticity)
            


# supply = sqrt(wf) * coeff
# 
# wf * l = supply @ prices
# wf * l = (coeff @ prices) * sqrt(wf) 
# sqrt(wf) * l = coeff @ prices
# wf = ((coeff@prices)/l)^2
# wf = ir^2 / l^2
#
# supply = coeff * (coeff @ price / l)
# supply' = (coeff / l) * (coeff)
# supply' = (coeff^2 / l) 
# 
# wf * l = (coeff @ prices) * sqrt(wf) 
# wf^2 * l^2 = (coeff @ prices)^2 * wf 
# l^2 * wf^2 = (coeff @ prices)^2 * wf
# l^2 * wf^2 - (coeff @ prices)^2 * wf = 0
# wf * (l^2 * wf - (coeff @ prices)^2) = 0


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



