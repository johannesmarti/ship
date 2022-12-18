import numpy as np
from numpy.linalg import norm
import logging

from typing import Callable,Iterable,Protocol,Tuple
import numpy.typing as npt


Prices = npt.NDArray
Bundle = npt.NDArray

class Participant(Protocol):
    def participate(self, prices : Prices) -> Bundle:
        ...

Market = Callable[[Iterable[Participant],Prices],Prices]

Elasticity = npt.NDArray

class ElasticBundle:
    value : Bundle
    elasticity : Elasticity
    def __init__(self, value, elasticity):
        assert np.all(elasticity >= 0)
        assert np.shape(value) == np.shape(elasticity)
        self.value = value
        self.elasticity = elasticity

    @classmethod
    def zero(cls,shape):
        return ElasticBundle(np.zeros(shape), np.zeros(shape))

    def __add__(self, other):
        assert other.shape() == self.shape()
        assert isinstance(other, ElasticBundle)
        logging.debug("add creates new object")
        return ElasticBundle(self.value + other.value,
                             self.elasticity + other.elasticity)

    def __iadd__(self, other):
        assert other.shape() == self.shape()
        assert isinstance(other, ElasticBundle)
        self.value += other.value
        self.elasticity += other.elasticity
        return self

    def shape(self):
        return self.value.shape

    def set_min_elasticity(self, min_value : float) -> None:
        np.maximum(self.elasticity, min_value, out=self.elasticity)

class ElasticityEstimatingParticipant(Participant, Protocol):
    def participate_and_estimate(self, prices : Prices) -> ElasticBundle:
        ...

    def participate(self, prices : Prices) -> Bundle:
        return self.participate_and_estimate(prices).value


class VolumeReportingParticipant(Participant, Protocol):
    def participate_with_volume(self, prices : Prices) -> Tuple[Bundle,Bundle]:
        ...
        
    def participate(self, prices : Prices) -> Bundle:
        return self.participate_with_volume(prices)[0]

class ElasticityFromVolumeParticipant:
    def __init__(self, inner : VolumeReportingParticipant):
        self.inner = inner
    
    def participate_and_estimate(self, prices : Prices):
        (error, volume) = self.inner.participate_with_volume(prices)
        return ElasticBundle(error, volume / prices)

EEP = ElasticityEstimatingParticipant

AdvancedMarket = Callable[[Iterable[ElasticityEstimatingParticipant],Prices],Prices]


iteration : int = 0

def reset_iterations() -> None:
    global iteration
    iteration = 0

def increment_iterations() -> None:
    global iteration
    iteration += 1

def iterations() -> int:
    global iteration
    return iteration


def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    increment_iterations()
    logging.info(f"at iteration {iterations()}")
    eb = ElasticBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate_and_estimate(prices)
    eb.set_min_elasticity(0.001)
    return eb

def update_prices(prices : Prices, error : ElasticBundle, t : float = 0.9) -> Prices:
    
    return prices - t * (error.value/error.elasticity)

def badness(error : Bundle) -> float:
    return norm(error)

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1, t : float = 0.9) -> Prices:
    logging.info(f"simple market for epsilon = {epsilon}")
    logging.info(f"with prices: {prices}")
    error = one_iteration(participants, prices)
    
    logging.info(f"with error: {error.value}")
    logging.info(f"with badness: {badness(error.value)}")
    logging.info(f"with elasticity: {error.elasticity}")
    while badness(error.value) >= epsilon:
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
    next_error = one_iteration(participants, next_prices)
    logging.info(f"next_prices: {next_prices}")
    assert((next_prices > 0).all())
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

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        (prices, error) = line_search(participants, prices, error)
    return prices

