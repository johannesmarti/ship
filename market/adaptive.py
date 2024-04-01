from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

@dataclass(frozen=True)
class AdaptiveSearchConfiguration:
    starting_t: float = 0.4
    max_t: float = 100.0
    min_t: float = 0.0001
    min_change_factor: float = 0.5
    max_change_factor: float = 1.5
    necessary_improvement: float = 1
    backoff: float = 0.8
    t_mixing: float = 0.2
    price_scaling : Optional[ScalingConfiguration] = None

def crop(s, values):
    # Determine the lower and upper bounds
    lower_bound, upper_bound = min(s, 1/s), max(s, 1/s)
    
    # Reapply the original sign to v
    cropped = np.clip(values, lower_bound, upper_bound)
    return cropped

def adapt_ts(config: AdaptiveSearchConfiguration, ts: np.ndarray,
             old_supply: VolumeBundle, new_supply: VolumeBundle) -> np.ndarray:
    signed_old = old_supply.update_term()
    sig = np.sign(signed_old)
    old = sig * signed_old
    new = sig * new_supply.update_term()
    #diff = old - new
    diff = np.maximum(old - new, 0.0001)

    adaptation = np.clip(old / diff, config.min_change_factor, config.max_change_factor)
    new_ts = ts * 0.9 * adaptation
    tl.log_values(logging.INFO, [("o*1000", old*1000), ("n*1000", new*1000),
                                 ("d*1000", diff*1000), ("o/d", old/diff), ("1000t", 1000*new_ts)])
    return np.clip(new_ts, config.min_t, config.max_t)

def make_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : AdaptiveSearchConfiguration = AdaptiveSearchConfiguration()) -> Prices:
    logging.info(f"starting adaptive search, with starting_t = {config.starting_t}")
    supply = one_iteration(participants, prices)
    badness = absolute_badness(supply)
    stable_ts = np.full_like(prices, config.starting_t)
    ts = stable_ts
    tl.log_values(logging.INFO, [("price",prices),("error", supply.error),
                                 ("volume", supply.volume),("t*1000",ts*1000)])
    necessary_improvement = config.necessary_improvement
    while absolute_badness(supply) >= epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")
        logging.info(f"real badness: {relative_badness(supply)}")

        increment_step()
        new_prices = broad_adapt_prices(prices, supply, ts, config.price_scaling)
        new_supply = one_iteration(participants, new_prices)
        ts = adapt_ts(config, ts, supply, new_supply)
        new_badness = absolute_badness(new_supply)
        if necessary_improvement * new_badness <= badness:
            necessary_improvement = config.necessary_improvement
            supply = new_supply
            prices = new_prices
            badness = new_badness
            stable_ts = mixing(stable_ts, ts, config.t_mixing)
            ts = stable_ts
        else:
            logging.warning(f"did not adapt prices because new badness {new_badness} is worse than previous badness {badness}")
            ts = config.backoff*ts
            necessary_improvement *= 0.9
            logging.info(f"necessary_improvement = {necessary_improvement}")
        tl.log_values(logging.INFO, [("price",new_prices),("error", new_supply.error),
                                     ("volume", new_supply.volume),("1000stabt",1000*stable_ts)])
    return prices

