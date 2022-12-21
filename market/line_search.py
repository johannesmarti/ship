from market.types import *

iteration : int = 0

def reset_iteration() -> None:
    global iteration
    iteration = 0

def increment_iteration() -> None:
    global iteration
    iteration += 1

def get_iteration() -> int:
    global iteration
    return iteration


step: int = 0

def reset_step() -> None:
    global step
    step = 0

def increment_step() -> None:
    global step
    step += 1

def get_step() -> int:
    global step
    return step

def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    increment_iteration()
    logging.info(f"at iteration {get_iteration()}")
    eb = ElasticBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate_and_estimate(prices)
    eb.set_min_elasticity(0.001)
    return eb

def update_prices(prices : Prices, error : ElasticBundle, t : float = 0.9) -> Prices:
    
    return np.maximum(prices - t * (error.value/error.elasticity), 0.000001)

def badness(error : Bundle) -> float:
    return norm(error)

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.001, t : float = 0.9) -> Prices:
    logging.info(f"simple market for epsilon = {epsilon}")
    logging.info(f"with prices: {prices}")
    error = one_iteration(participants, prices)
    
    logging.info(f"with error: {error.value}")
    logging.info(f"with badness: {badness(error.value)}")
    logging.info(f"with elasticity: {error.elasticity}")
    while badness(error.value) >= epsilon:
        increment_step()
        logging.info("next iteration")
        prices = update_prices(prices, error, t)
        error = one_iteration(participants, prices)
        logging.info(f"next_prices: {prices}")
        assert((prices > 0).all())
        logging.info(f"with error: {error.value}")
        logging.info(f"with badness: {badness(error.value)}")
        logging.info(f"with elasticity: {error.elasticity}")
    return prices

def line_search(participants : Iterable[EEP], prices : Prices, error : ElasticBundle, t : float = 0.9, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,ElasticBundle]:
    logging.info(f"starting line search, with t = {t}, alpha = {alpha}")
    logging.info(f"at prices: {prices}")
    logging.info(f"for error: {error.value}")
    logging.info(f"with badness: {badness(error.value)}")
    logging.info(f"with elasticity: {error.elasticity}")

    next_prices = update_prices(prices, error, t)
    assert((next_prices > 0).all())
    next_error = one_iteration(participants, next_prices)
    logging.info(f"next_prices: {next_prices}")
    logging.info(f"with error: {next_error.value}")
    logging.info(f"with badness: {badness(next_error.value)}, vs old: {badness(error.value)}")
    while badness(next_error.value) >= alpha * badness(error.value):
        t *= beta
        if (t < 0.01):
            logging.warning(f"giving up on line search at t = {t}")
            break
        logging.info(f"next iteration of line search with t = {t}")
        next_prices = update_prices(prices, error, t)
        next_error = one_iteration(participants, next_prices)
        logging.info(f"next_prices: {next_prices}")
        assert((next_prices > 0).all())
        logging.info(f"with error: {next_error.value}")
        logging.info(f"with badness: {badness(next_error.value)}, vs old: {badness(error.value)}")
    logging.info("\n")
    return (next_prices, next_error)

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.001, t : float = 0.9) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        increment_step()
        (prices, error) = line_search(participants, prices, error, t=t)
    return prices

