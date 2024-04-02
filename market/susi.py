from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

@dataclass(frozen=True)
class SusiConfiguration:
    epsilon: float = 0.1
    rate: float = 0.2
    initial_backoff: float = 0.1
    first_momentum_mixin: float = 0.1
    price_scaling: Optional[ScalingConfiguration] = None

def make_market(participants : Iterable[Participant], price : Prices,
                config : SusiConfiguration = SusiConfiguration()) -> Prices:
    logging.info(f"starting eva")
    supply = one_iteration(participants, price)
    # Here we could multiply with the price already
    first_momentum = config.initial_backoff * price * supply.update_term()
    while absolute_badness(supply) >= config.epsilon:
        logging.info(f"\nnext iteration because of badness: {absolute_badness(supply)}")

        price = price - config.rate * first_momentum
        price = np.maximum(price, MIN_PRICE)
        supply = one_iteration(participants, price)
        first_momentum = mixing(first_momentum, price * supply.update_term(),
                                config.first_momentum_mixin)
        tl.log_values(logging.DEBUG, [("price", price),
                                     ("sold", supply.sold()),
                                     ("bought", supply.bought()),
                                     ("fm*1000", first_momentum*1000),
                                    ])
    return price
