import numpy as np
import logging

from consumer import *
from wage_economy.balanced_producer import *
from wage_economy.village import *
from market.line_search import *
from core.schema import GoodsSchema, TradeGoodsSchema

np.set_printoptions(precision=4,suppress=True,threshold=8)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

production_matrix = np.array([
    [5,1,0,0],
    [0,-0.5,1.5,0],
    [0,-1,-2,2],
    [0,5,0,-0.5] ])

ls = GoodsSchema(["food", "wood", "ore", "tools"])
#ls = TradeGoodsSchema(["food", "wood", "ore", "tools"], [])
pl = ls.placement()

consumer = SalaryConsumer(np.array([2,1,0,2]), pl)
producer = BalancedProducer(200, production_matrix)
village = Village(producer, consumer)

#p0 = np.array([10,10,10,10])
#p0 = np.array([50,1000,30,5])
#p0 = np.array([5,5,11,19])
p0 = np.array([50,1200,30,5])
#p0 = np.array([13,13,27,50])
epsilon = 0.01

def run_once(t : float):
    config = LineSearchConfiguration(price_scaling=ScalingConfiguration(100))
    p = line_search_market([village], p0, epsilon, config)
    print(f"iterations: {get_iteration()}    (t={t})")
    print(p)
    reset_iteration()

run_once(0.6)

"""
run_once(0.2)
run_once(0.3)
run_once(0.4)
run_once(0.5)
run_once(0.6)
run_once(0.7)
run_once(0.8)
run_once(0.9)
run_once(1.0)
"""

