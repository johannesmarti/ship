import numpy as np
import logging

from participants.consumer import *
from participants.factory import *
from market.base import *
from market.line_search import *

np.set_printoptions(precision=4,suppress=True,threshold=8)
logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')

farm = Factory("farm", np.array([5,1,0,0]), 10)
mine = Factory("mine", np.array([0,-0.5,1.5,0]), 10)
smith = Factory("smith", np.array([0,-1,-2,2]), 20)
woodCutter = Factory("wood cutter", np.array([0,5,0,-0.5]), 10)

consumers = FixedBudgetConsumer(np.array([2,1,0.001,2]), 1000)

village = [farm,mine,smith,woodCutter,consumers]

p0 = np.array([50,1000,30,5])
#p0 = np.array([50,1200,30,5])
#p0 = np.array([13,13,27,50])
epsilon = 0.000001

def run_once(t : float):
    p = line_search_market(village, p0, epsilon, t=t)
    print(f"iterations: {get_iteration()}    (t={t})")
    print(p)
    reset_iteration()

run_once(0.2)
run_once(0.3)
run_once(0.4)
run_once(0.5)
run_once(0.6)
run_once(0.7)
run_once(0.8)
run_once(0.9)
run_once(1.0)
run_once(1.1)
run_once(1.2)
run_once(1.3)
run_once(1.4)
