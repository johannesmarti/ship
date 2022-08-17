from abc import ABC, abstractmethod
from collections.abc import Iterator

class Good(ABC):
    @abstractmethod
    def name(self : 'Good') -> str:
        pass
    @abstractmethod
    def is_tradable(self : 'Good') -> bool:
        pass


class Worktask(ABC):
    @abstractmethod
    def description(self : 'Worktask') -> str:
        pass
    @abstractmethod
    def location(self : 'Worktask') -> 'Province':
        pass

class Province(ABC):
    @abstractmethod
    def name(self : 'Province') -> str:
        pass
    @abstractmethod
    def population(self : 'Province') -> int:
        pass
    @abstractmethod
    def local_worktasks(self : 'Province') -> Iterator[Worktask]:
        pass

class World(ABC):
    @abstractmethod
    def goods(self : 'World') -> Iterator[Good]:
        pass
    @abstractmethod
    def provinces(self : 'World') -> Iterator[Province]:
        pass

    def worktasks(self : 'World') -> Iterator[Worktask]:
        for province in self.provinces():
            for local_task in province.local_worktasks():
                yield local_task
    
class Money(float):
    pass

class Allocation(ABC):
    @abstractmethod
    def world(self : 'Allocation') -> World:
        pass
    @abstractmethod
    def price(self : 'Allocation', province : Province, good : Good) -> Money:
        pass
    @abstractmethod
    def workforce(self : 'Allocation', task : Worktask) -> float:
        pass
