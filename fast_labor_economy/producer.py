from typing import Tuple
import logging
import numpy as np

from core.bundle import *
from core.participant import *
from core.placement import LaborPlacement

class Producer(Participant):
    @classmethod
    def factory(cls, name : str, production_coefficients : Bundle,
                placement : LaborPlacement):
        wide_pcs = np.zeros(placement.global_width)
        wide_pcs[placement.production_slice] = production_coefficients
        return Producer(name, wide_pcs, placement.labor_index)

    @classmethod
    def trader(cls, name : str, labor_index : int, from_index : int,
               to_index : int, trade_efficiency : float, global_width : int):
        wide_pcs = np.zeros(global_width)
        wide_pcs[from_index] = -trade_efficiency
        wide_pcs[to_index] = trade_efficiency
        return Producer(name, wide_pcs, labor_index)

    def __init__(self, name : str, production_coefficients : Bundle,
                 labor_index : int):
        self.name = name 
        self.production_coefficients = production_coefficients
        self.labor_index = labor_index
        # could this also be implemented if we make labor part of the production_coefficients

    def participate(self, prices : Prices) -> VolumeBundle:
        (workforce,production) = produce(self.name,
                                         self.production_coefficients,
                                         prices[self.labor_index],
                                         prices)
        production.add_at_ix(self.labor_index, -workforce)
        return production

class Producers(Participant):
    """
    Implements a Participant for a setting where all the producers in all
    the provinces are treated as one big matrix/vector. This is hopefully
    more efficient than having a seperate participant for every work task.
    """

    def __init__(self, production_matrix: np.ndarray,
                       labor_indices: np.ndarray):
        self._production_matrix = production_matrix
        self._labor_indices = labor_indices

    def participate(self, prices: Prices) -> VolumeBundle:
        income_rate = self._production_matrix @ prices
        # set entries with negative income to 0
        income_rate[income_rate < 0] = 0
        wage_per_worker = prices[self._labor_indices]

        sqrt_workforce = income_rate / wage_per_worker
        goods_supply = self._production_matrix.T @ sqrt_workforce
        goods_supply_abs = np.abs(self._production_matrix).T @ sqrt_workforce
        workforce = sqrt_workforce**2
        labor_supply = np.bincount(self._labor_indices,
                                   weights=workforce,
                                   minlength=prices.shape[0])
        supply = goods_supply - labor_supply
        supply_abs = goods_supply_abs + labor_supply
        return VolumeBundle(supply, supply_abs)
