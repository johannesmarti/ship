import numpy as np
from abc import ABC, abstractmethod

from core.bundle import VolumeBundle

Prices = np.ndarray

class Participant(ABC):
    @abstractmethod
    def participate(self, prices : Prices) -> VolumeBundle:
        ...

