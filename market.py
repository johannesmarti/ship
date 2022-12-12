from typing import Callable,Iterable,List,Protocol,Tuple

#class Market(Protocol):
#    def register_participant(self, participant : MarketParticipant) -> None:
#        ...
#
#    def compute_equilibrium(self, prices : List[float]) -> prices


Prices = List[float]
Bundle = List[float]

class Participant(Protocol):
    def participate(self, prices : Prices) -> Bundle:
        ...

Market = Callable[[Iterable[Participant],Prices],Prices]


Elasticity = List[float]
ElasticBundle = Tuple[Bundle,Elasticity]

class ElasticityEstimatingParticipant(Participant, Protocol):
    def participate_and_estimate(self, prices : Prices) -> ElasticBundle:
        ...

    def participate(self, prices : Prices) -> Bundle:
        return self.participate_and_estimate(prices)[0]

EEP = ElasticityEstimatingParticipant

AdvancedMarket = Callable[[Iterable[ElasticityEstimatingParticipant],Prices],Prices]


def norm(b : Bundle) -> float:
    return 0

iterations : int = 0

def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    n = len(prices)
    b = []
    e = []
    for p in participants:
        (db,de) = p.participate_and_estimate(prices)
        b += db
        e += de
    iterations += 1
    return (b,e)

def update_prices(prices : Prices, error : Bundle, elasticity : Elasticity, t : float = 1) -> Prices:
    return prices #- 0.1 * error

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    (error,elasticity) = one_iteration(participants, prices)
    while norm(error) >= epsilon:
        prices = update_prices(prices, error, elasticity)
        (error, elasticity) = one_iteration(participants, prices)
    return prices

def line_search(participants : Iterable[EEP], prices : Prices, error : Bundle, elasticity : Elasticity, t : float = 1, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,Bundle,Elasticity]:
    next_prices = update_prices(prices, error, elasticity, t)
    (next_error, next_elasticity) = one_iteration(participants, next_prices)
    while next_error >= error: # * alpha:
        t *= beta
        next_prices = update_prices(prices, error, elasticity, t)
        (next_error,next_elasticity) = one_iteration(participants, next_prices)
    return (next_prices, next_error, next_elasticity)

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    (error,elasticity) = one_iteration(participants, prices)
    while norm(error) >= epsilon:
        (prices, error, elasticity) = line_search(participants, prices, error, elasticity)
    return prices

