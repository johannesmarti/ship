from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

def adapt_prices(price : Prices, supply: VolumeBundle, t : float, price_scaling : Optional[ScalingConfiguration]) -> Prices:
    new_price = price * (1 - t * supply.update_term())
    if (price_scaling != None):
        new_price = apply_price_scaling(new_price, price_scaling)
    return np.maximum(new_price, MIN_PRICE)

@dataclass(frozen=True)
class LineSearchConfiguration:
    epsilon: float = 0.1
    necessary_improvement: float = 1
    necessary_improvement_decay: float = 0.9
    initial_backoff: float = 0.8
    backoff_decay: float = 0.2
    necessary_improvement: float = 1
    price_scaling: Optional[ScalingConfiguration] = None

def line_search(participants: Iterable[Participant],
                prices: Prices,
                supply: VolumeBundle,
                config: LineSearchConfiguration) -> Tuple[Prices,VolumeBundle]:
    logging.debug(f"\nstarting line search")
    backoff = config.initial_backoff
    badness = absolute_badness(supply)
    necessary_improvement = config.necessary_improvement
    backoff = config.initial_backoff
    while True:
        increment_step()
        new_prices = adapt_prices(prices, supply, backoff, config.price_scaling)
        new_supply = one_iteration(participants, new_prices)
        new_badness = absolute_badness(new_supply)
        if necessary_improvement * new_badness <= badness:
            logging.info(f"return from line search with badness {new_badness}")
            return (new_prices, new_supply)
        logging.warning(f"did not adapt prices because new badness {new_badness}\n is worse than previous badness {badness}")
        tl.log_values(logging.INFO, [("price",new_prices),
                                     ("sold", new_supply.sold()),
                                     ("bought", new_supply.bought()),
                                     ("oprice", prices),
                                     ("osold", supply.sold()),
                                     ("obought", supply.bought())])
        necessary_improvement *= config.necessary_improvement_decay
        backoff *= config.backoff_decay
        logging.info(f"necessary_improvement = {necessary_improvement}")

def make_market(participants : Iterable[Participant], prices : Prices, config : LineSearchConfiguration = LineSearchConfiguration()) -> Prices:
    logging.info(f"starting equiuilibrium search")
    supply = one_iteration(participants, prices)
    while absolute_badness(supply) >= config.epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")

        (prices, supply) = line_search(participants, prices, supply, config)
        logging.info(f"at step {get_iteration()}:")
        tl.log_values(logging.INFO, [("price", prices),
                                     ("sold", supply.sold()),
                                     ("bought", supply.bought()),
                                     ("error", supply.error),
                                    ])
    return prices
