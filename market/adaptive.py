from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import table_logger as tl

@dataclass(frozen=True)
class AdaptiveSearchConfiguration:
    starting_t : float = 0.4
    max_change_factor : float = 4
    price_scaling : Optional[ScalingConfiguration] = None

def adaptive_search(participants : Iterable[Participant],
                    prices : Prices,
                    error : VolumeBundle,
                    config : AdaptiveSearchConfiguration) -> Tuple[Prices,VolumeBundle]:
    logging.debug(f"adaptive_search")
    logging.debug(f"for error: {error.value}")
    logging.debug(f"with volume: {error.volume}")
    logging.debug(f"with badness: {badness(error)}")
    logging.debug(f"starting adptive search, with t = {config.t}")
    logging.debug(f"at prices: {prices}")
    logging.debug(f"for error: {error.value}")
    logging.debug(f"with volume: {error.volume}")
    logging.debug(f"with badness: {badness(error)}")

    next_prices = adapt_prices(prices, error, ts, config.price_scaling)
    logging.debug(f"iterating for prices: {next_prices}")
    assert (next_prices > 0).all()
    next_error = one_iteration(participants, next_prices)
    logging.debug(f"with error: {next_error.value}")
    logging.debug(f"with volume: {next_error.volume}")
    logging.debug(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    while badness(next_error) >= config.alpha * badness(error):
        t *= config.beta
        if (t < 0.01):
            logging.warning(f"giving up on line search at badness {badness(next_error)}")
            break
        logging.info(f"next iteration of line search with t = {t}")
        next_prices = adapt_prices(prices, error, ts, config.price_scaling)
        logging.debug(f"iterating for prices: {next_prices}")
        next_error = one_iteration(participants, next_prices)
        assert (next_prices > 0).all()
        logging.debug(f"with error: {next_error.value}")
        logging.debug(f"next volume: {next_error.volume}")
        logging.debug(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    logging.debug("\n")
    return (next_prices, next_error)

def crop(s, values):
    # Determine the lower and upper bounds
    lower_bound, upper_bound = min(s, 1/s), max(s, 1/s)
    
    # Reapply the original sign to v
    cropped = np.clip(values, lower_bound, upper_bound)
    return cropped

def adapt_ts(max_change_factor: float, ts: np.ndarray,
             old_supply: VolumeBundle, new_supply: VolumeBundle) -> np.ndarray:
    old = old_supply.value
    new = new_supply.value
    diff = np.maximum(old - new, 0.0001)
    adaptation = crop(max_change_factor, old / diff)
    return ts * adaptation

def adaptive_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : AdaptiveSearchConfiguration = AdaptiveSearchConfiguration()) -> Prices:
    logging.info(f"starting adaptive search, with starting_t = {config.starting_t}")
    supply = one_iteration(participants, prices)
    ts = np.full_like(prices, config.starting_t)
    tl.log_values(logging.INFO, [("price",prices),("error", supply.value),
                                 ("volume", supply.volume),("t",ts)])
    while absolute_badness(supply) >= epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")

        tl.log_values(logging.INFO, [("price",prices),("error", supply.value),
                                     ("volume", supply.volume),("t",ts)])
        increment_step()
        prices = broad_adapt_prices(prices, supply, ts, config.price_scaling)
        new_supply = one_iteration(participants, prices)
        ts = adapt_ts(config.max_change_factor, ts, supply, new_supply)
        supply = new_supply
    return prices

