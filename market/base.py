import numpy as np
from numpy.linalg import norm
import logging
from dataclasses import dataclass

from typing import Callable,Iterable,Optional
#import numpy.typing as npt

from core.participant import *

Market = Callable[[Iterable[Participant],Prices],Prices]

MIN_PRICE = 0.0001

iteration : int = 0

def reset_iteration() -> None:
    global iteration
    iteration = 0

def increment_iteration() -> None:
    global iteration
    iteration += 1

def get_iteration() -> int:
    global iteration
    return iteration


step: int = 0

def reset_step() -> None:
    global step
    step = 0

def increment_step() -> None:
    global step
    step += 1

def get_step() -> int:
    global step
    return step

MIN_PRICE : float = 0.001

@dataclass(frozen=True)
class ScalingConfiguration:
    set_to_price : float = 10

def adapt_prices(price : Prices, error : VolumeBundle, t : float, price_scaling : Optional[ScalingConfiguration]) -> Prices:
    new_price = price * (1 - t * (error.value/(error.volume + 0.1)))
    #assert (new_price > 0).all()
    if (price_scaling != None):
        #avg_price = np.average(new_price)
        avg_price = price[0]
        scaling_factor = price_scaling.set_to_price/avg_price
        new_price *= scaling_factor
    return np.maximum(new_price, MIN_PRICE)

def badness(error : VolumeBundle) -> float:
    #return norm(error)
    #return norm(error, ord=1)
    return norm(error.value/(error.volume + 0.0001), ord=1)

def absolute_badness(error : VolumeBundle) -> float:
    #return norm(error)
    #return norm(error, ord=1)
    return norm(error.value, ord=1)
