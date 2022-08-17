from worldview import *
from algodata import *

class IdGood(Good):
    def __init__(self : 'IdGood', world : AlgoData, i : int):
        self.world = world
        self.id = i

    def __eq__(self: 'IdGood', other: object):
        return isinstance(other, IdGood) and \
                self.id == other.id and self.world is other.world

    def name(self : 'IdGood') -> str:
        return self.world._goods_config.name_of_index(self.id)

    def is_tradable(self : 'IdGood') -> bool:
        return self.id < self.world._goods_config.num_tradable_goods

class IdWorktask(Worktask):
    def __init__(self: 'IdWorktask', world : AlgoData,
                 province_id : int, local_id : int):
        self.world = world
        self.province_id = province_id
        self.local_id = local_id

    def __eq__(self: 'IdWorktask', other: object):
        return isinstance(other, IdWorktask) and \
                 self.local_id == other.local_id and \
                 self.province_id == other.province_id and \
                 self.world is other.world

    def description(self: 'IdWorktask'):
        return f"worktask with local_id {self.local_id} in {self.location().name()}"
    
    def location(self: 'IdWorktask'):
        return IdProvince(self.world, self.province_id)

class IdProvince(Province):
    def __init__(self : 'IdProvince', world : AlgoData, i : int):
        self.world = world
        self.id = i

    def __eq__(self: 'IdProvince', other: object):
        return isinstance(other, IdProvince) and \
                self.id == other.id and self.world is other.world

    def name(self : 'IdProvince') -> str:
        return self.world.name_of_index(self.id)

    def population(self : 'IdProvince') -> int:
        return self.world.population(self.id)

    def local_worktasks(self : 'IdProvince') -> Iterator[Worktask]:
        number_of_tasks = self.world.producer(self.id).num_tasks()
        for i in range(0, number_of_tasks):
            yield IdWorktask(self.world, self.id, i)

class WrapperWorld(World):
    def __init__(self : 'WrapperWorld', data : AlgoData):
        self.data = data

    def goods(self : 'WrapperWorld') -> Iterator[Good]:
        for i in range(0, self.data.num_goods):
            yield IdGood(self.data, i)

    def provinces(self : 'WrapperWorld') -> Iterator[Province]:
        for i in range(0, self.data.num_provinces):
            yield IdProvince(self.data, i)

class WrapperAllocation(Allocation):
    def __init__(self: 'WrapperAllocation', world: WrapperWorld,
                 allocation: AllocationAtPrices):
        self.in_world = world
        self.data = allocation

    def world(self: 'WrapperAllocation') -> World:
        return self.in_world

    def price(self: 'WrapperAllocation', province: 'IdProvince', good: 'IdGood') -> Money:
        return None
