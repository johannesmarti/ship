from abc import ABC, abstractmethod
import numpy as np
import logging

#from typing import Tuple
import numpy.typing as npt

Prices = npt.NDArray
Bundle = npt.NDArray

class VolumeBundle:
    value : Bundle
    volume : Bundle
    def __init__(self, value, volume):
        assert np.all(volume>= 0)
        assert np.shape(value) == np.shape(volume)
        self.value = value
        self.volume = volume

    @classmethod
    def zero(cls, shape):
        return VolumeBundle(np.zeros(shape), np.zeros(shape))

    def __add__(self, other):
        assert isinstance(other, VolumeBundle)
        assert other.shape() == self.shape()
        logging.debug("add creates new volume bundle")
        return VolumeBundle(self.value + other.value,
                            self.volume + other.volume)

    def __iadd__(self, other):
        assert isinstance(other, VolumeBundle)
        assert other.shape() == self.shape()
        self.value += other.value
        self.volume += other.volume
        return self

    def add_at_ix(self, ix : int, value : float):   
        self.value[ix] += value
        self.volume[ix] += abs(value)
    
    def __str__(self):
        return str(self.value) + " with volume " + str(self.volume)

    def shape(self):
        return self.value.shape


class Participant(ABC):
    @abstractmethod
    def participate(self, prices : Prices) -> VolumeBundle:
        ...

