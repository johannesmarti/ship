from worldview import *
from algodata import *


class IdGood(Good):
    def __init__(self, world, i):
        self.world = world
        self.id = i

    def __eq__(self, other):
        return (
            isinstance(other, IdGood)
            and self.id == other.id
            and self.world is other.world
        )

    def name(self):
        return self.world._goods_config.name_of_index(self.id)

    def is_tradable(self):
        return self.id < self.world._goods_config.num_tradable_goods


class IdWorktask(Worktask):
    def __init__(self, world, province_id, local_id):
        self.world = world
        self.province_id = province_id
        self.local_id = local_id

    def __eq__(self, other):
        return (
            isinstance(other, IdWorktask)
            and self.local_id == other.local_id
            and self.province_id == other.province_id
            and self.world is other.world
        )

    def description(self):
        return f"worktask with local_id {self.local_id} in {self.location().name()}"

    def location(self):
        return IdProvince(self.world, self.province_id)


class IdProvince(Province):
    def __init__(self, world, i):
        self.world = world
        self.id = i

    def __eq__(self, other):
        return (
            isinstance(other, IdProvince)
            and self.id == other.id
            and self.world is other.world
        )

    def name(self):
        return self.world.name_of_index(self.id)

    def population(self):
        return self.world.population(self.id)

    def local_worktasks(self):
        number_of_tasks = self.world.producer(self.id).num_tasks()
        for i in range(0, number_of_tasks):
            yield IdWorktask(self.world, self.id, i)


class WrapperWorld(World):
    def __init__(self, data):
        self.data = data

    def goods(self):
        for i in range(0, self.data.num_goods):
            yield IdGood(self.data, i)

    def provinces(self):
        for i in range(0, self.data.num_provinces):
            yield IdProvince(self.data, i)


class WrapperAllocation(Allocation):
    def __init__(self, world, allocation):
        self.in_world = world
        self.data = allocation

    def world(self):
        return self.in_world

    def price(self, province, good):
        assert province.world is self.in_world
        assert good.world is self.in_world
        return None
