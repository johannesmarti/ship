import pytest

import numpy as np

from participants.consumer import *
from participants.factory import *
from market.line_search import *

@pytest.fixture
def village():
    farm = Factory(np.array([8,1,0,0]), 10)
    mine = Factory(np.array([0,-0.5,1.5,0]), 10)
    smith = Factory(np.array([0,-1,-2,2]), 20)
    consumers = Consumer(np.array([3,1,0,3]), 10000)
    return [farm,mine,smith,consumers]

equilibrium = [30.20319, 58.366023, 65.199585, 145.845051]

def test_line_search(village):
    p0 = np.array([10,1000,10,10])

    p = line_search_market(village, p0, epsilon=0.0001, t=0.5)
    assert np.isclose(p, equilibrium).all()

def test_line_search2(village):
    p0 = np.array([10,1000,10,10])

    e1 = line_search_market(village, p0, t=0.5)
    e2 = line_search_market(village, p0, t=0.2)
    assert np.isclose(e1, e2).all()

def test_line_search3(village):
    p0 = np.array([10,10,10,10])
    p1 = np.array([10,1,10,10000])

    e1 = line_search_market(village, p0, t=0.5)
    e2 = line_search_market(village, p1, t=0.5)
    assert np.isclose(e1, e2).all()

