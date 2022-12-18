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

