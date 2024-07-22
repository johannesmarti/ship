import numpy as np

Bundle = np.ndarray

class VolumeBundle:
    def __init__(self, error, volume):
        assert np.shape(error) == np.shape(volume)
        # TODO: assert that volume is positive
        self.error = error
        self.volume = volume

    @classmethod
    def zero(cls, shape):
        return VolumeBundle(np.zeros(shape), np.zeros(shape))

    def shape(self):
        return self.error.shape

    def __add__(self, other):
        assert isinstance(other, VolumeBundle)
        assert other.shape() == self.shape()
        return VolumeBundle(self.error + other.error,
                            self.volume + other.volume)

    def __iadd__(self, other):
        assert isinstance(other, VolumeBundle)
        assert other.shape() == self.shape()
        self.error += other.error
        self.volume += other.volume
        return self

    def __mul__(self, other):
        assert isinstance(other, (int,float))
        return VolumeBundle(other * self.error, other * self.volume)

    def __rmul__(self, other):
        assert isinstance(other, (int,float))
        return VolumeBundle(other * self.error, other * self.volume)

    def __imul__(self, other):
        assert isinstance(other, (int,float))
        self.error *= other
        self.volume *= other
        return self

    def add_at_ix(self, ix : int, error : float):   
        self.error[ix] += error
        self.volume[ix] += abs(error)

    def add_at_slice(self, sl : slice, other):
        assert isinstance(other, VolumeBundle)
        assert other.shape() == self.error[sl].shape
        self.error[sl] += other.error
        self.volume[sl] += other.volume
    
    def sold(self) -> Bundle:
        return (self.volume + self.error) / 2

    def bought(self) -> Bundle:
        return (self.volume - self.error) / 2

    def update_term(self) -> np.ndarray:
        MIN_VOLUME : float = 0.001
        return (self.error/(self.volume + MIN_VOLUME))

    def __str__(self):
        return str(self.error) + " with volume " + str(self.volume)

