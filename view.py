from abc import ABC, abstractmethod
from collections.abc import Iterator

class Money(int):
    pass

class GoodId(int):
    pass

class ProvinceId(int):
    pass

class WorktaskId():
    def __init__(self : 'WorktaskId', province : ProvinceId, task : int):
        self.province = province
        self.task = task

class WorldView(ABC):
    @abstractmethod
    def good_name(self : 'WorldView', good : GoodId) -> str:
        pass
    @abstractmethod
    def goods(self : 'WorldView') -> Iterator[GoodId]:
        pass
    @abstractmethod
    def is_tradable(self : 'WorldView', good : GoodId) -> bool:
        pass

    @abstractmethod
    def province_name(self : 'WorldView', province : ProvinceId) -> str:
        pass
    @abstractmethod
    def population(self : 'WorldView', province : ProvinceId) -> int:
        pass
    @abstractmethod
    def provinces(self : 'WorldView') -> Iterator[ProvinceId]:
        pass

    @abstractmethod
    def worktask_description(self : 'WorldView', wt : WorktaskId) -> str:
        pass
    @abstractmethod
    def worktasks(self : 'WorldView') -> Iterator[WorktaskId]:
        pass
    @abstractmethod
    def worktasks_in_province(self : 'WorldView',
                              province : ProvinceId) -> Iterator[WorktaskId]:
        pass

class AllocationView(ABC):
    @abstractmethod
    def worldview(self : 'AllocationView') -> WorldView:
        pass
    @abstractmethod
    def price(self : 'AllocationView', good : GoodId) -> Money:
        pass
    @abstractmethod
    def workforce(self : 'AllocationView', task: WorktaskId) -> float:
        pass
