from market.base import *
from typing import Tuple

def one_iteration(participants : Iterable[Participant], prices : Prices) -> VolumeBundle:
    increment_iteration()
    logging.info(f"at iteration {get_iteration()}")
    eb = VolumeBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate(prices)
    return eb

def line_search(participants : Iterable[Participant], prices : Prices, error : VolumeBundle, t : float = 0.9, alpha : float = 1, beta : float = 0.6) -> Tuple[Prices,VolumeBundle]:
    logging.debug(f"starting line search, with t = {t}, alpha = {alpha}")
    logging.info(f"at prices: {prices}")
    logging.info(f"for error: {error.value}")
    logging.info(f"with volume: {error.volume}")
    logging.info(f"with badness: {badness(error)}")

    next_prices = adapt_prices(prices, error, t)
    assert((next_prices > 0).all())
    next_error = one_iteration(participants, next_prices)
    logging.debug(f"next_prices: {next_prices}")
    logging.debug(f"with error: {next_error.value}")
    logging.debug(f"with volume: {next_error.volume}")
    logging.debug(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    while badness(next_error) >= alpha * badness(error):
        t *= beta
        if (t < 0.1):
            logging.warning(f"giving up on line search at t = {t}")
            break
        logging.debug(f"next iteration of line search with t = {t}")
        next_prices = adapt_prices(prices, error, t)
        next_error = one_iteration(participants, next_prices)
        logging.debug(f"next_prices: {next_prices}")
        assert((next_prices > 0).all())
        logging.debug(f"with error: {next_error.value}")
        logging.debug(f"next volume: {next_error.volume}")
        logging.debug(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    logging.debug("\n")
    return (next_prices, next_error)

def line_search_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, t : float = 0.9) -> Prices:
    supply = one_iteration(participants, prices)
    while absolute_badness(supply) >= epsilon:
        increment_step()
        #print(supply.volume)
        print(supply.volume)
        print(supply.value, absolute_badness(supply))
        #print(prices, absolute_badness(supply))
        (prices, supply) = line_search(participants, prices, supply, t=t)
    return prices

