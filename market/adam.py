from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

@dataclass(frozen=True)
class AdamConfiguration:
    epsilon: float = 0.1
    rate: float = 0.2
    initial_backoff: float = 0.01
    first_momentum_mixin: float = 0.1
    second_momentum_mixin: float = 0.01
    #price_scaling: Optional[ScalingConfiguration] = None

def make_market(participants : Iterable[Participant], price : Prices,
                config : AdamConfiguration = AdamConfiguration()) -> Prices:
    logging.info(f"starting adam")
    supply = one_iteration(participants, price)
    # Here we could multiply with the price already
    first_momentum = config.initial_backoff * price * supply.update_term()
    second_momentum = np.zeros(first_momentum.shape)
    while absolute_badness(supply) >= config.epsilon:
        logging.info(f"\nnext iteration because of badness: {absolute_badness(supply)}")

        base = second_momentum + (config.rate * 0.001)
        price = price * (1 - config.rate/base * first_momentum)
        price = np.maximum(price, MIN_PRICE)
        supply = one_iteration(participants, price)
        current_first_momentum = supply.update_term()
        first_momentum = mixing(first_momentum, current_first_momentum,
                                config.first_momentum_mixin)
        current_second_momentum = current_first_momentum * current_first_momentum
        second_momentum = mixing(second_momentum, current_second_momentum,
                                 config.second_momentum_mixin)
        tl.log_values(logging.DEBUG, [("price", price),
                                     ("sold", supply.sold()),
                                     ("bought", supply.bought()),
                                     ("fm*1000", first_momentum*1000),
                                    ])
    return price
