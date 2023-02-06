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
    logging.info(f"starting line search, with t = {t}, alpha = {alpha}")
    logging.info(f"at prices: {prices}")
    logging.info(f"for error: {error.value}")
    logging.info(f"with badness: {badness(error)}")
    logging.info(f"with volume: {error.volume}")

    next_prices = adapt_prices(prices, error, t)
    assert((next_prices > 0).all())
    next_error = one_iteration(participants, next_prices)
    logging.info(f"next_prices: {next_prices}")
    logging.info(f"with error: {next_error.value}")
    logging.info(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    while badness(next_error) >= alpha * badness(error):
        t *= beta
        if (t < 0.01):
            logging.warning(f"giving up on line search at t = {t}")
            break
        logging.info(f"next iteration of line search with t = {t}")
        next_prices = adapt_prices(prices, error, t)
        next_error = one_iteration(participants, next_prices)
        logging.info(f"next_prices: {next_prices}")
        assert((next_prices > 0).all())
        logging.info(f"with error: {next_error.value}")
        logging.info(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    logging.info("\n")
    return (next_prices, next_error)

def line_search_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, t : float = 0.9) -> Prices:
    supply = one_iteration(participants, prices)
    while absolute_badness(supply) >= epsilon:
        increment_step()
        (prices, supply) = line_search(participants, prices, supply, t=t)
    return prices

