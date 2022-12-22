from market.base import *

def one_iteration(participants : Iterable[Participant], prices : Prices) -> Bundle:
    increment_iteration()
    logging.info(f"at iteration {get_iteration()}")
    e = np.zeros(prices.shape)
    for p in participants:
        e += p.participate(prices)
    return e

def minimal_change(prices : Prices, error : Bundle) -> Prices:
    return prices - ((error * prices + 0.1) / 10000)

def update_elasticity(to_change : Elasticity, other : Elasticity, factor : float = 0.8) -> None:
    assert factor >= 0 and factor <= 1
    to_change *= (1 - factor)
    to_change += factor * other

def estimate_elasticity(p0 : Prices, p1 : Prices, e0 : Bundle, e1 : Bundle, base : Elasticity) -> Elasticity:
    guess = np.maximum((e0 - e1) / (p0 - p1), MINIMAL_ELASTICITY)
    guess = np.minimum(guess, MAXIMAL_ELASTICITY)
    #guess = (e0 - e1) / (p0 - p1)
    mask = np.isnan(guess)
    guess[mask] = base[mask]
    return guess

def line_search(participants : Iterable[Participant], prices : Prices, error : Bundle, elasticity : Elasticity, t : float = 0.9, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,Bundle,Elasticity]:
    logging.info(f"starting line search, with t = {t}, alpha = {alpha}")
    logging.info(f"at prices: {prices}")
    logging.info(f"for error: {error}")
    logging.info(f"with badness: {badness(error)}")
    logging.info(f"with elasticity: {elasticity}")

    next_prices = adapt_prices(prices, ElasticBundle(error,elasticity), t)
    assert((next_prices > 0).all())
    next_error = one_iteration(participants, next_prices)
    next_elasticity = estimate_elasticity(prices, next_prices, error, next_error, elasticity)
    logging.info(f"next_prices: {next_prices}")
    logging.info(f"with error: {next_error}")
    logging.info(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
    logging.info(f"next elasticity: {next_elasticity}")
    while badness(next_error) >= alpha * badness(error):
        t *= beta
        if (t < 0.01):
            logging.warning(f"giving up on line search at t = {t}")
            break
        logging.info(f"next iteration of line search with t = {t}")
        next_prices = adapt_prices(prices, ElasticBundle(error, elasticity), t)
        next_error = one_iteration(participants, next_prices)
        next_elasticity = estimate_elasticity(prices, next_prices, error, next_error, elasticity)
        logging.info(f"next_prices: {next_prices}")
        assert((next_prices > 0).all())
        logging.info(f"with error: {next_error}")
        logging.info(f"with badness: {badness(next_error)}, vs old: {badness(error)}")
        logging.info(f"next elasticity: {next_elasticity}")
    logging.info("\n")
    return (next_prices, next_error, next_elasticity)

def estimating_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, t : float = 0.9, mixing : float = 0.5) -> Prices:
    error = one_iteration(participants, prices)
    better_prices = minimal_change(prices, error)
    better_error = one_iteration(participants, better_prices)
    elasticity = estimate_elasticity(prices, better_prices, error, better_error, np.full(prices.shape, MAXIMAL_ELASTICITY))
    # the following two lines let the better of the two guesses be the starting point. Not sure this is a good idea
    prices = better_prices
    error = better_error
    while badness(error) >= epsilon:
        increment_step()
        (prices, error, next_elasticity) = line_search(participants, prices, error, elasticity, t=t)
        update_elasticity(elasticity, next_elasticity, mixing)
    return prices

