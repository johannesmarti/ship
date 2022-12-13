import numpy as np
from numpy.linalg import norm

from typing import Callable,Iterable,Protocol,Tuple
import numpy.typing as npt


Scalar = np.float32
#ScalarType = float

Prices = npt.NDArray[Scalar]
Bundle = npt.NDArray[Scalar]

class Participant(Protocol):
    def participate(self, prices : Prices) -> Bundle:
        ...

Market = Callable[[Iterable[Participant],Prices],Prices]


Elasticity = npt.NDArray[Scalar]

class ElasticBundle:
    value : Bundle
    elasticity : Elasticity
    def __init__(value, elasticity):
        assert np.all(elasticity > 0)
        assert np.shape(value) == np.shape(elasticity)
        self.value = value
        self.elasticity = elasticity

    @classmethod
    def zero(cls,shape):
        return ElasticBundle(np.zeros(shape), np.zeros(shape))

    def __add__(self, other):
        assert other.shape() == self.shape()
        assert isinstance(other, ElasticBundle)
        print("add creates new object")
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


class ElasticityEstimatingParticipant(Participant, Protocol):
    def participate_and_estimate(self, prices : Prices) -> ElasticBundle:
        ...

    def participate(self, prices : Prices) -> Bundle:
        return self.participate_and_estimate(prices).value


EEP = ElasticityEstimatingParticipant

AdvancedMarket = Callable[[Iterable[ElasticityEstimatingParticipant],Prices],Prices]


iterations : int = 0

def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    eb = ElasticBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate_and_estimate(prices)
    iterations += 1
    return eb

def update_prices(prices : Prices, error : ElasticBundle, t : float = 1) -> Prices:
    return prices - (error.value/error.elasticity)

def badness(error : Bundle) -> Scalar:
    return norm(error)

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        prices = update_prices(prices, error)
        error = one_iteration(participants, prices)
    return prices

def line_search(participants : Iterable[EEP], prices : Prices, error : ElasticBundle, t : float = 1, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,ElasticBundle]:
    next_prices = update_prices(prices, error, t)
    next_error = one_iteration(participants, next_prices)
    while badness(next_error.value) >= alpha * badness(error.value):
        t *= beta
        next_prices = update_prices(prices, error, t)
        next_error = one_iteration(participants, next_prices)
    return (next_prices, next_error)

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        (prices, error) = line_search(participants, prices, error)
    return prices

