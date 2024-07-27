from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl
from core.bundle import Bundle

@dataclass(frozen=True)
class EvaConfiguration:
    epsilon: float = 0.1
    rate: float = 0.2
    initial_backoff: float = 0.1
    first_momentum_mixin: float = 0.1
    max_iterations: int | None = 10000
    keep_history: bool = False

@dataclass(frozen=True)
class Iteration:
    price: Prices
    supply: Bundle
    badness: float
    momentum: np.ndarray

@dataclass(frozen=True)
class Result:
    price: Prices
    supply: Bundle
    timeout: bool
    iterations: int 
    history: list[Iteration]

def make_market(participants : Iterable[Participant], price : Prices,
                config : EvaConfiguration = EvaConfiguration()) -> Result:
    logging.info(f"starting eva")
    iterations = 1
    history = []
    supply = one_iteration(participants, price)
    # Here we could multiply with the price already
    first_momentum = config.initial_backoff * supply.update_term()
    while True:
        badness = absolute_badness(supply)
        if config.keep_history:
            iteration = Iteration(price=price,
                                  supply=supply,
                                  badness=badness,
                                  momentum=first_momentum)
            history.append(iteration)
        if badness < config.epsilon:
            return Result(price=price,
                          supply=supply,
                          timeout=False,
                          iterations=iterations,
                          history=history)
        if iterations >= config.max_iterations:
            return Result(price=price,
                          supply=supply,
                          timeout=True,
                          iterations=iterations,
                          history=history)
        logging.info(f"\nnext iteration because of badness: {badness}")

        price = price * (1 - config.rate * first_momentum)
        price = np.maximum(price, MIN_PRICE)
        supply = one_iteration(participants, price)
        first_momentum = mixing(first_momentum, supply.update_term(),
                                config.first_momentum_mixin)
        iterations += 1
        tl.log_values(logging.DEBUG, [("price", price),
                                      ("sold", supply.sold()),
                                      ("bought", supply.bought()),
                                      ("fm*1000", first_momentum*1000)
                                    ])
    return price
