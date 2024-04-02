from typing import Tuple
import logging
import numpy as np

from core.bundle import *
from core.participant import *
from core.placement import LaborPlacement

# helper function used further below
def produce(name : str, production_coefficients : Bundle, wage_per_worker : float, prices : Prices) -> Tuple[float, VolumeBundle]:
    income_rate = production_coefficients @ prices
    if (income_rate <= 0):
        #logging.debug(f"{name}: income_rate: {income_rate}")
        return (0,VolumeBundle.zero(prices.shape))
    else:
        sqrt_workforce = income_rate / wage_per_worker
        supply = production_coefficients * sqrt_workforce
        workforce = sqrt_workforce**2
        #logging.debug(f"{name}: workforce: {workforce}")
        #logging.debug(f"{name}: production: {supply}")
        return (workforce, VolumeBundle(supply, np.absolute(supply)))

class Producer(Participant):
    @classmethod
    def factory(cls, name : str, production_coefficients : Bundle,
                placement : LaborPlacement):
        wide_pcs = np.zeros(placement.global_width)
        wide_pcs[placement.production_slice] = production_coefficients
        return Producer(name, wide_pcs, placement.labour_index)

    @classmethod
    def trader(cls, name : str, labour_index : int, from_index : int,
               to_index : int, trade_efficiency : float, global_width : int):
        wide_pcs = np.zeros(global_width)
        wide_pcs[from_index] = -trade_efficiency
        wide_pcs[to_index] = trade_efficiency
        return Producer(name, wide_pcs, labour_index)

    def __init__(self, name : str, production_coefficients : Bundle,
                 labour_index : int):
        self.name = name 
        self.production_coefficients = production_coefficients
        self.labour_index = labour_index
        # could this also be implemented if we make labour part of the production_coefficients

    def participate(self, prices : Prices) -> VolumeBundle:
        (workforce,production) = produce(self.name,
                                         self.production_coefficients,
                                         prices[self.labour_index],
                                         prices)
        production.add_at_ix(self.labour_index, -workforce)
        return production
