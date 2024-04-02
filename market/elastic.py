from dataclasses import dataclass

from typing import Tuple,Optional

from market.base import *
import pretty_table as tl

@dataclass(frozen=True)
class ElasticMarketConfiguration:
    initial_slowdown: float = 0.4
    necessary_improvement: float = 1
    necessary_improvement_decay: float = 0.9
    initial_backoff: float = 0.8
    backoff_decay: float = 0.2
    elasticity_mixing: float = 0.1
    inner_elasticity_mixing: float = 0.5
    price_scaling : Optional[ScalingConfiguration] = None

MIN_ELASTICITY = 0.0001
MAX_ELASTICITY = 100000

class Elasticities:
    def __init__(self, seller_elasticity: np.ndarray,
                       buyer_elasticity: np.ndarray):
        assert seller_elasticity.shape == buyer_elasticity.shape
        assert (seller_elasticity > 0).all()
        assert (buyer_elasticity > 0).all()
        self.sellers = seller_elasticity
        self.buyers = buyer_elasticity

    def total_elasticity(self) -> np.ndarray:
        t = self.sellers + self.buyers
        assert (t > 0).all()
        return t

def estimate_initial_elasticities(prices: Prices,
                                  supply: VolumeBundle,
                                  config: ElasticMarketConfiguration) -> Elasticities:
    half_of_total_elasticity = config.initial_slowdown * supply.volume/(2*prices)
    hte = np.maximum(half_of_total_elasticity, MIN_ELASTICITY)
    return Elasticities(hte, hte)

def elasticity_adapt_prices(price: Prices, supply: VolumeBundle,
                            elasticities: Elasticities,
                            backoff: float,
                            price_scaling: Optional[ScalingConfiguration]) -> Prices:
    new_price = price - backoff * supply.error/elasticities.total_elasticity()
    if (price_scaling != None):
        new_price = apply_price_scaling(new_price, price_scaling)
    new_price = np.maximum(new_price, MIN_PRICE)
    even_smaller = 0.3 * MIN_PRICE
    adjustments = np.random.uniform(low=-even_smaller, high=even_smaller,
                                    size=new_price.shape)
    new_price += adjustments
    while True:
        # every price gets adjustment applied at least twice and thus stays above 0 because adjustments are smaller than a third of MIN_PRICE
        price_increase = new_price - price
        good_positions = price_increase != 0
        if np.all(good_positions):
            return new_price
        logging.warning("found bad positions when adapting prices")
        adjustments = np.random.uniform(low=-even_smaller, high=even_smaller,
                                        size=new_price.shape)
        new_price += adjustments * (~good_positions)

def compute_elasticities(prices: Prices, supply: VolumeBundle,
                         new_prices: Prices, new_supply: VolumeBundle,
                         config: ElasticMarketConfiguration) -> Elasticities:
    price_increase = new_prices - prices
    assert (np.abs(price_increase) > 0).all()
    esellers = (new_supply.sold() - supply.sold()) / price_increase
    ebuyers  = (supply.bought() - new_supply.bought()) / price_increase
    esellers = np.clip(esellers, MIN_ELASTICITY, MAX_ELASTICITY)
    ebuyers  = np.clip(ebuyers, MIN_ELASTICITY, MAX_ELASTICITY)
    return Elasticities(esellers, ebuyers)

def elasticity_mixing(a: Elasticities, b: Elasticities, factor: float) -> Elasticities:
    es = mixing(a.sellers, b.sellers, factor)
    eb = mixing(a.buyers, b.buyers, factor)
    return Elasticities(es, eb)

def make_step(participants: Iterable[Participant],
              supply: VolumeBundle,
              prices: Prices,
              elasticities: Elasticities,
              config: ElasticMarketConfiguration) -> tuple[VolumeBundle,Prices,Elasticities]:
    logging.info(f"\nstarting next step")
    badness = absolute_badness(supply)
    necessary_improvement = config.necessary_improvement
    backoff = config.initial_backoff
    while True:
        increment_step()
        new_prices = elasticity_adapt_prices(prices, supply,
                                             elasticities, backoff,
                                             config.price_scaling)
        new_supply = one_iteration(participants, new_prices)
        new_badness = absolute_badness(new_supply)
        new_elasticities = compute_elasticities(prices, supply,
                                                new_prices, new_supply, config)
        elasticities = elasticity_mixing(elasticities, new_elasticities, config.inner_elasticity_mixing)
        if necessary_improvement * new_badness <= badness:
            logging.info(f"return new elasticities with badness {new_badness}")
            tl.log_values(logging.INFO, [("esellers",elasticities.sellers),
                                         ("ebuyers", elasticities.buyers)])
            return (new_supply, new_prices, elasticities)
        logging.warning(f"did not adapt prices because new badness {new_badness}\n is worse than previous badness {badness}")
        tl.log_values(logging.INFO, [("price",new_prices),
                                     ("sold", new_supply.sold()),
                                     ("bought", new_supply.bought()),
                                     ("oprice", prices),
                                     ("osold", supply.sold()),
                                     ("obought", supply.bought())])
        # Here we should maybe backoff with the elasticities a bit
        necessary_improvement *= config.necessary_improvement_decay
        backoff *= config.backoff_decay
        logging.info(f"necessary_improvement = {necessary_improvement}")


def make_market(participants : Iterable[Participant], prices : Prices, epsilon : float = 0.001, config : ElasticMarketConfiguration = ElasticMarketConfiguration()) -> Prices:
    logging.info(f"starting elastic equiuilibrium search")
    supply = one_iteration(participants, prices)
    badness = absolute_badness(supply)
    elasticities = estimate_initial_elasticities(prices, supply, config)
    logging.info(f"initial elasticities:")
    tl.log_values(logging.INFO, [("esellers",elasticities.sellers),
                                 ("ebuyers", elasticities.buyers),
                                 ("price", prices),
                                 ("error", supply.error)])
    while absolute_badness(supply) >= epsilon:
        logging.info(f"\n\nnext iteration because of badness: {absolute_badness(supply)}")

        (supply,prices,final_elasticities) = make_step(participants, supply, prices, elasticities, config)
        elasticities = elasticity_mixing(elasticities, final_elasticities,
                                         config.elasticity_mixing)
        logging.info(f"new longterm-elasticities:")
        tl.log_values(logging.INFO, [("esellers",elasticities.sellers),
                                     ("ebuyers", elasticities.buyers),
                                     ("price", prices),
                                     ("sold", supply.sold()),
                                     ("bought", supply.bought()) ])
    return prices

