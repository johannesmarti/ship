from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import table_logger as tl

@dataclass(frozen=True)
class AdaptiveSearchConfiguration:
    starting_t : float = 0.4
    max_change_factor : float = 4
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
    diff = np.maximum(old - new, 0.000001)

    adaptation = crop(max_change_factor, old / diff)
    tl.log_values(logging.INFO, [("o", old), ("n", new),
                                 ("d", diff), ("o/d", old/diff), ("ada", adaptation)])
    return ts * adaptation

def adaptive_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : AdaptiveSearchConfiguration = AdaptiveSearchConfiguration()) -> Prices:
    logging.info(f"starting adaptive search, with starting_t = {config.starting_t}")
    supply = one_iteration(participants, prices)
    ts = np.full_like(prices, config.starting_t)
    tl.log_values(logging.INFO, [("price",prices),("error", supply.value),
                                 ("volume", supply.volume),("t",ts)])
    while absolute_badness(supply) >= epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")

        increment_step()
        prices = broad_adapt_prices(prices, supply, ts, config.price_scaling)
        new_supply = one_iteration(participants, prices)
        ts = adapt_ts(config.max_change_factor, ts, supply, new_supply)
        supply = new_supply
        tl.log_values(logging.INFO, [("price",prices),("error", supply.value),
                                     ("volume", supply.volume),("100t",100*ts)])
    return prices

