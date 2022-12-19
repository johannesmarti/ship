import numpy as np
import logging

from participants.consumer import *
from participants.factory import *
from market.line_search import *

np.set_printoptions(precision=6,suppress=True,threshold=8)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')

farm = Factory(np.array([8,1,0,0]), 10)
mine = Factory(np.array([0,-0.5,1.5,0]), 10)
smith = Factory(np.array([0,-1,-2,2]), 20)

consumers = Consumer(np.array([3,1,0,3]), 10000)

village = [farm,mine,smith,consumers]
lazy_village = list(map(ElasticityFromVolumeParticipant, village))

p0 = np.array([10,10,10,10])

p = line_search_market(lazy_village, p0, 0.0001, t=0.5)
#p = simple_market(village, p0, 0.01)
print("iterations:", get_iteration())
print(p)

