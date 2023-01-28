import numpy as np
import logging

import tools.derivative as sjd

from participants.consumer import *

np.set_printoptions(precision=4,suppress=True,threshold=8)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')

p = np.array([10.0,20.0])

pops = Consumer(np.array([2,4]), 30)
print(pops.participate_and_estimate(p))

def f(p):
    return pops.participate_and_estimate(p).value[1]

sjd.print_estimation(f, p, 1)
sjd.print_estimation(f, p, 0.1)
sjd.print_estimation(f, p, 0.01)
sjd.print_estimation(f, p, 0.001)
#sjd.print_estimation(f, p, 0.0001)
#sjd.print_estimation(f, p, 0.00001)
#sjd.print_estimation(f, p, 0.000001)
#sjd.print_estimation(f, p, 0.0000001)

