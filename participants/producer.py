import logging
import numpy as np

from typing import Tuple

from participants.abstract import *
from placement import Placement

# litter helper function we use further below
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

class Producer(Participant):
    @classmethod
    def factory(cls, name : str, production_coefficients : Bundle,
                placement : Placement):
        wide_pcs = np.zeros(placement.width)
        wide_pcs[placement.production_slice] = production_coefficients
        return Producer(name, wide_pcs, placement.labour_index)

    @classmethod
    def trader(cls, name : str, production_coefficients : Bundle,
               production_slice : slice, labour_index : int, global_width : int):
        wide_pcs = np.zeros(global_width)
        wide_pcs[from_index] = -trade_efficiency
        wide_pcd[to_index] = trade_efficiency
        return Producer(name, wide_pcs, labour_index)

    def __init__(self, name : str, production_coefficients : Bundle,
                 labour_index : int):
        self.name = name 
        self.production_coefficients = production_coefficients
        self.labour_index = labour_index

    def participate(self, prices : Prices) -> VolumeBundle:
        (workforce,production) = produce(self.name,
                                         self.production_coefficients,
                                         prices[self.labour_index],
                                         prices)
        production.add_at_ix(self.labour_index, -workforce)
        return production
