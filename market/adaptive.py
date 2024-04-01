from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

@dataclass(frozen=True)
class AdaptiveSearchConfiguration:
    starting_t: float = 0.4
    max_change_factor: float = 1.3
    necessary_improvement: float = 1
    backoff: float = 0.8
    price_scaling : Optional[ScalingConfiguration] = None

def crop(s, values):
    # Determine the lower and upper bounds
    lower_bound, upper_bound = min(s, 1/s), max(s, 1/s)
    
    # Reapply the original sign to v
    cropped = np.clip(values, lower_bound, upper_bound)
    return cropped

def adapt_ts(max_change_factor: float, ts: np.ndarray,
             old_supply: VolumeBundle, new_supply: VolumeBundle) -> np.ndarray:
    signed_old = old_supply.update_term()
    sig = np.sign(signed_old)
    old = sig * signed_old
    new = sig * new_supply.update_term()
    diff = old - new
    #diff = np.maximum(old - new, 0.001)

    adaptation = crop(max_change_factor, old / diff)
    tl.log_values(logging.INFO, [("o*1000", old*1000), ("n*1000", new*1000),
                                 ("d", diff), ("o/d", old/diff), ("ada", adaptation)])
    new_ts = ts * adaptation
    return np.clip(new_ts, 0.0001, 10)

def make_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : AdaptiveSearchConfiguration = AdaptiveSearchConfiguration()) -> Prices:
    logging.info(f"starting adaptive search, with starting_t = {config.starting_t}")
    supply = one_iteration(participants, prices)
    badness = relative_badness(supply)
    ts = np.full_like(prices, config.starting_t)
    tl.log_values(logging.INFO, [("price*10",prices*10),("error*10", supply.value*10),
                                 ("volume", supply.volume),("t",ts)])
    while absolute_badness(supply) >= epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")

        increment_step()
        new_prices = broad_adapt_prices(prices, supply, ts, config.price_scaling)
        new_supply = one_iteration(participants, new_prices)
        ts = adapt_ts(config.max_change_factor, ts, supply, new_supply)
        new_badness = relative_badness(new_supply)
        if config.necessary_improvement * new_badness <= badness:
            supply = new_supply
            prices = new_prices
            badness = new_badness
        else:
            logging.warning(f"did not adapt prices because new badness {new_badness} is worse than previous badness {badness}")
            ts = config.backoff*ts
        tl.log_values(logging.INFO, [("price",prices),("error", supply.value),
                                     ("volume", supply.volume),("100t",100*ts)])
    return prices

