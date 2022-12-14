import numpy as np
from numpy.linalg import norm

from typing import Callable,Iterable,Protocol,Tuple
import numpy.typing as npt


Scalar = np.float64

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


iterations = 0

def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    global iterations
    iterations += 1
    print(iterations)
    eb = ElasticBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate_and_estimate(prices)
    return eb

def update_prices(prices : Prices, error : ElasticBundle, t : float = 0.9) -> Prices:
    
    return prices - t * (error.value/error.elasticity)

def badness(error : Bundle) -> Scalar:
    return norm(error)

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1, t : float = 0.9) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        prices = update_prices(prices, error, t)
        error = one_iteration(participants, prices)
    return prices

def line_search(participants : Iterable[EEP], prices : Prices, error : ElasticBundle, t : float = 0.9, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,ElasticBundle]:
    next_prices = update_prices(prices, error, t)
    print("starting line search")
    #print(f"error: ", error.value, error.elasticity)
    #print(f"badness: ", badness(error.value))
    print(f"next_prices: ", next_prices)
    assert((next_prices > 0).all())
    next_error = one_iteration(participants, next_prices)
    #print(f"next_error: ", next_error.value, next_error.elasticity)
    #print(f"badness: ", badness(next_error.value))
    while badness(next_error.value) >= alpha * badness(error.value):
        t *= beta
        if (t < 0.01):
            print("giving up on line search")
            break
        print("next iteration of line search with t =", t)
        print(f"next_error: ", next_error.value)
        print(f"old_error: ", error.value, error.elasticity)
        print(f"badness: ", badness(next_error.value), "vs old:", badness(error.value))
        print(f"next_prices: ", next_prices)
        next_prices = update_prices(prices, error, t)
        assert((next_prices > 0).all())
        next_error = one_iteration(participants, next_prices)
    return (next_prices, next_error)

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while badness(error.value) >= epsilon:
        (prices, error) = line_search(participants, prices, error)
        print(f"prices: ", prices)
        print(f"error: ", error.value, error.elasticity)
        print(f"badness: ", badness(error.value))
    return prices

