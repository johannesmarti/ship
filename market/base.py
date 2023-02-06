import numpy as np
from numpy.linalg import norm
import logging

from typing import Callable,Iterable
#import numpy.typing as npt

from participants.abstract import *

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


def adapt_prices(price : Prices, error : VolumeBundle, t : float = 0.9) -> Prices:
    new_price = price * (1 - t * (error.value/error.volume))
    assert (new_price > 0).all()
    return new_price
    #return np.maximum(new_price, MIN_PRICE)

def badness(error : Bundle) -> float:
    #return norm(error)
    return norm(error, ord=1)
