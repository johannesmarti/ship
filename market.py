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

class ElasticBundle:
    value : Bundle
    elasticity : Elasticity
    def __init__(value, elasticity):
        self.value = value
        self.elasticity = elasticity

    @classmethod
    def zero(cls,zero_base):
        return ElasticBundle(zero_base, zero_base)

    def __add__(self, other):
        if isinstance(other, ElasticBundle):
            return ElasticBundle(self.value + other.value,
                                 self.elasticity + other.elasticity)
        else:
            raise ValueError("ElasticBundles can only be added to other ElasticBundles");


class ElasticityEstimatingParticipant(Participant, Protocol):
    def participate_and_estimate(self, prices : Prices) -> ElasticBundle:
        ...

    def participate(self, prices : Prices) -> Bundle:
        return self.participate_and_estimate(prices).value


EEP = ElasticityEstimatingParticipant

AdvancedMarket = Callable[[Iterable[ElasticityEstimatingParticipant],Prices],Prices]


def norm(b : Bundle) -> float:
    return 0

iterations : int = 0

def one_iteration(participants : Iterable[EEP], prices : Prices) -> ElasticBundle:
    n = len(prices)
    eb = ElasticBundle.zero([0])
    for p in participants:
        eb += p.participate_and_estimate(prices)
    iterations += 1
    return eb

def update_prices(prices : Prices, error : ElasticBundle, t : float = 1) -> Prices:
    return prices #- 0.1 * error

def simple_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while norm(error.value) >= epsilon:
        prices = update_prices(prices, error)
        error = one_iteration(participants, prices)
    return prices

def line_search(participants : Iterable[EEP], prices : Prices, error : ElasticBundle, t : float = 1, alpha : float = 1, beta : float = 0.5) -> Tuple[Prices,ElasticBundle]:
    next_prices = update_prices(prices, error, t)
    next_error = one_iteration(participants, next_prices)
    while next_error.value >= error.value: # * alpha:
        t *= beta
        next_prices = update_prices(prices, error, t)
        next_error = one_iteration(participants, next_prices)
    return (next_prices, next_error)

def line_search_market(participants : Iterable[EEP], prices : Prices, epsilon : float = 0.1) -> Prices:
    error = one_iteration(participants, prices)
    while norm(error.value) >= epsilon:
        (prices, error) = line_search(participants, prices, error)
    return prices

