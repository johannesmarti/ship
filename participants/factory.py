import logging
import numpy as np

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
            
