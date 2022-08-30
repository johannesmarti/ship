from abc import ABC, abstractmethod

class World(ABC):
    @abstractmethod
    def goods(self):
        pass

    @abstractmethod
    def good_name(self, good):
        pass
    @abstractmethod
    def is_tradable(self, good):
        pass

    def worktasks(self):
        for province in self.provinces():
            for local_task in self.local_worktasks(province):
                yield local_task
    @abstractmethod
    def description(self, worktask):
        pass
    @abstractmethod
    def location(self, worktask):
        pass

    @abstractmethod
    def provinces(self):
        pass
    @abstractmethod
    def province_name(self, province):
        pass
    @abstractmethod
    def population(self, province):
        pass
    @abstractmethod
    def local_worktasks(self, province):
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

    @abstractmethod
    def wages(self, province):
        pass

    @abstractmethod
    def utility(self, province):
        pass
