import numpy as np
from numpy.linalg import norm
import logging

from typing import Callable,Iterable
#import numpy.typing as npt

from participants.abstract import *

Market = Callable[[Iterable[Participant],Prices],Prices]

AdvancedMarket = Callable[[Iterable[ElasticityEstimatingParticipant],Prices],Prices]

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


def adapt_prices(prices : Prices, error : ElasticBundle, t : float = 0.9) -> Prices:
    
    return np.maximum(prices - t * (error.value/error.elasticity), 0.001)

def badness(error : Bundle) -> float:
    return norm(error)
