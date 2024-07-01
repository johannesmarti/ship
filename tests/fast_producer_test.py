import pytest

import numpy as np

import fast_labor_economy.producer as p


@pytest.fixture
def producers():
    pm = np.array([[ 1, 0, 0, 0], 
                   [ 0, 0, 1, 0], 
                   [-1, 0, 1, 0]])
    li = np.array([1, 3, 3])
    producer = p.Producers(pm, li)
    return producer


def test_fast_labor_producers(producers):
    prices = np.array([15, 10, 20, 10])
    vb = producers.participate(prices)

    assert np.isclose(vb.error, np.array([1, -2.25, 2.5, -4.25])).all()
    assert np.isclose(vb.volume, np.array([2, 2.25, 2.5, 4.25])).all()

