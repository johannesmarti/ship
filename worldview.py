from abc import ABC, abstractmethod
from collections.abc import Iterator

class Good(ABC):
    @abstractmethod
    def name(self : 'Good') -> str:
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

class GoodId(int):
    pass

class World(ABC):
    @abstractmethod
    def goods(self : 'World') -> Iterator[Good]:
        pass
    @abstractmethod
    def worktasks(self : 'World') -> Iterator[Worktask]:
        pass
    @abstractmethod
    def provinces(self : 'World') -> Iterator[Province]:
        pass

class Money(int):
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
