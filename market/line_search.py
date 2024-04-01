from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *

@dataclass(frozen=True)
class LineSearchConfiguration:
    t : float = 0.6
    necessary_improvement : float = 1
    backoff : float = 0.6
    price_scaling : Optional[ScalingConfiguration] = None

def one_iteration(participants : Iterable[Participant], prices : Prices) -> VolumeBundle:
    increment_iteration()
    logging.debug(f"at iteration {get_iteration()}")
    eb = VolumeBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate(prices)
    return eb

def line_search(participants : Iterable[Participant],
                prices : Prices,
                error : VolumeBundle,
                config : LineSearchConfiguration) -> Tuple[Prices,VolumeBundle]:
    t = config.t
    logging.debug(f"starting line search, with t = {t}, necessary_improvement = {config.necessary_improvement}")
    logging.debug(f"at prices: {prices}")
    logging.debug(f"for error: {error.error}")
    logging.debug(f"with volume: {error.volume}")
    logging.debug(f"with badness: {relative_badness(error)}")

    next_prices = adapt_prices(prices, error, t, config.price_scaling)
    logging.debug(f"iterating for prices: {next_prices}")
    assert (next_prices > 0).all()
    next_error = one_iteration(participants, next_prices)
    logging.debug(f"with error: {next_error.error}")
    logging.debug(f"with volume: {next_error.volume}")
    logging.debug(f"with badness: {relative_badness(next_error)}, vs old: {relative_badness(error)}")
    while config.necessary_improvement * relative_badness(next_error) >=  relative_badness(error):
        t *= config.backoff
        if (t < 0.01):
            logging.warning(f"giving up on line search at badness {relative_badness(next_error)}")
            break
        logging.info(f"next iteration of line search with t = {t}")
        next_prices = adapt_prices(prices, error, t, config.price_scaling)
        logging.debug(f"iterating for prices: {next_prices}")
        next_error = one_iteration(participants, next_prices)
        assert (next_prices > 0).all()
        logging.debug(f"with error: {next_error.error}")
        logging.debug(f"next volume: {next_error.volume}")
        logging.debug(f"with badness: {relative_badness(next_error)}, vs old: {relative_badness(error)}")
    logging.debug("\n")
    return (next_prices, next_error)

def make_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : LineSearchConfiguration = LineSearchConfiguration()) -> Prices:
    supply = one_iteration(participants, prices)
    while absolute_badness(supply) >= epsilon:
        increment_step()
        #print(supply.volume)
        #print(supply.volume)
        #print(supply.error, absolute_badness(supply))
        #print(supply.error, badness(supply))
        #print(prices, absolute_badness(supply))
        (prices, supply) = line_search(participants, prices, supply, config)
    return prices
