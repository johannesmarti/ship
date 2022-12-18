import numpy as np
import logging

from market import *

np.set_printoptions(precision=4,suppress=True,threshold=8)

class Factory:
    def __init__(self, production_vector : Bundle, labor_cost : float):
    	self.production_vector = production_vector
    	self.labor_cost = labor_cost
    
    def participate_with_volume(self, prices : Prices) -> Tuple[Bundle,Bundle]:
        if (prices @ self.production_vector <= 0):
            return (np.zeros(prices.shape), np.zeros(prices.shape))
        else:
            revenue = self.production_vector @ prices
            workforce = (revenue / self.labor_cost) ** 2
            result = workforce * self.production_vector
            logging.debug(f"production: {result}")
            return (result, np.absolute(result))
            
class Consumers:
    def __init__(self, utility : Bundle, money : float):
        self.utility = utility
        self.money = money
        
    def participate_with_volume(self, prices : Prices) -> Tuple[Bundle,Bundle]:
        assert prices.shape == self.utility.shape
        a = np.sum(self.utility / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = self.money / a
        solution = lambda_squared * self.utility / (prices * prices)
        logging.debug(f"consumption: {solution}")
        return (-solution, solution)


logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')

farm = Factory(np.array([8,1,0,0]), 10)
mine = Factory(np.array([0,-0.5,1.5,0]), 10)
smith = Factory(np.array([0,-1,-2,2]), 20)

consumers = Consumers(np.array([3,1,0,3]), 10000)

village = list(map(ElasticityFromVolumeParticipant, [farm,mine,smith,consumers]))
p0 = np.array([10,10,10,10])

p = line_search_market(village, p0, 0.01)
#p = simple_market(village, p0, 0.01)
print("iterations:", iterations())
print(p)

