from abc import ABC, abstractmethod
from collections.abc import Iterator


class Good(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def is_tradable(self):
        pass


class Worktask(ABC):
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def location(self):
        pass


class Province(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def population(self):
        pass

    @abstractmethod
    def local_worktasks(self):
        pass


class World(ABC):
    @abstractmethod
    def goods(self):
        pass

    @abstractmethod
    def provinces(self):
        pass

    def worktasks(self):
        for province in self.provinces():
            for local_task in province.local_worktasks():
                yield local_task


class Money(float):
    pass


class Allocation(ABC):
    @abstractmethod
    def world(self):
        pass

    @abstractmethod
    def price(self, province, good):
        pass

    @abstractmethod
    def workforce(self, task):
        pass
