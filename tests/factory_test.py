import pytest

import numpy as np

from participants.factory import *

@pytest.fixture
def farm():
    return Factory(np.array([2,1]), 30)

def test_factory(farm):
    prices = np.array([10,10])
    bundle = farm.participate(prices)

    assert np.isclose(np.array([2., 1.]), bundle.value).all()

