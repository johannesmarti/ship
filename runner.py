import numpy as np
import logging

from participants.consumer import *
from participants.factory import *
from market.base import *
from market.line_search import *
from market.estimating import *

np.set_printoptions(precision=3,suppress=True,threshold=8)
logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')

farm = Factory(np.array([6,1,0,0]), 10)
mine = Factory(np.array([0,-0.5,1.5,0]), 10)
smith = Factory(np.array([0,-1,-2,2]), 20)
woodCutter = Factory(np.array([0,5,0,-0.5]), 10)

consumers = Consumer(np.array([2,1,0,3]), 1000)

village = [farm,mine,smith,woodCutter,consumers]
lazy_village = list(map(ElasticityFromVolumeParticipant, village))

p0 = np.array([10000,10,10,1])
epsilon = 0.001

#p = line_search_market(lazy_village, p0, epsilon, t=0.7)
p = line_search_market(village, p0, epsilon, t=1.5)
#p = estimating_market(village, p0, epsilon, t=0.9, mixing=0.1)
print("iterations:", get_iteration())
print(p)

