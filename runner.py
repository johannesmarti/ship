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

farm = Factory(np.array([5,1,0,0]), 10)
mine = Factory(np.array([0,-0.5,1.5,0]), 10)
smith = Factory(np.array([0,-1,-2,2]), 20)
woodCutter = Factory(np.array([0,5,0,-0.5]), 10)

consumers = FixedBudgetConsumer(np.array([2,1,0,2]), 1000)

village = [farm,mine,smith,woodCutter,consumers]

p0 = np.array([50,1000,30,5])
p1 = np.array([13,13,27,50])
epsilon = 0.01

p = line_search_market(village, p0, epsilon, t=0.6)
#p = line_search_market(village, p0, epsilon, t=0.71)

print("iterations:", get_iteration())
print(p)

