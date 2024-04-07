from typing import Iterable, Optional, cast

from core.placement import Placement, LaborPlacement

# These schema classes are tightly coupled. They extendend each other and make
# assumptions about each others implementation. This is not nice but should be
# fine for now!
GoodId = int

class GoodsSchema:
    def __init__(self, good_names : list[str]):
        self._good_names = good_names
        self._num_goods = len(self._good_names)

    def valid_id(self, good_id: GoodId) -> bool:
        return 0 <= good_id < self.width()

    def width(self) -> int:
        return self._num_goods

    def name_of_good(self, good : GoodId) -> str:
        assert good < self.width()
        return self._good_names[good]

    ix_to_str = name_of_good

    def good_of_name(self, name : str) -> GoodId:
        return self._good_names.index(name)

    def placement(self) -> Placement:
        return Placement(self.__num_goods, slice(0, self._num_goods))


class TradeGoodsSchema(GoodsSchema):
    def __init__(self, num_trade_goods: int, num_fixed_goods: int, good_names: list[str]):
        #self._good_names = list(goods);
        self._num_trade_goods = num_trade_goods
        self._num_fixed_goods = num_fixed_goods
        super().__init__(good_names)

    @classmethod
    def from_lists(cls, trade_good_names : list[str], fixed_good_names : list[str]):
        num_trade_goods = len(trade_good_names)
        num_fixed_goods = len(fixed_good_names)
        return cls(num_trade_goods, num_fixed_goods, trade_good_names + fixed_good_names)

    def is_trade_good(self, good : GoodId) -> bool:
        return good < self._num_trade_goods

    def trade_slice(self) -> slice:
        return slice(0, self._num_trade_goods)

    def trade_goods(self) -> Iterable[GoodId]:
        ts = self.trade_slice()
        return range(ts.start, ts.stop)

    def production_slice(self) -> slice:
        return slice(0,self.width())

class LaborTradeGoodsSchema(TradeGoodsSchema):
    def __init__(self, base: TradeGoodsSchema):
        extended_names = base._good_names + ["labor"]
        super().__init__(base._num_trade_goods, base._num_fixed_goods + 1, extended_names)

    @classmethod
    def from_lists(cls, trade_good_names: list[str], fixed_good_names: list[str]):
        return LaborTradeGoodsSchema(TradeGoodsSchema.from_lists(trade_good_names,
                                                                 fixed_good_names))

    def labour(self) -> GoodId:
        return self.width() - 1

    def production_slice(self) -> slice:
        return slice(0,self.width() - 1)
    
    def labour_placement(self) -> LaborPlacement:
        return LaborPlacement(self.width(), self.production_slice(),
                               self.labour())

ProvinceId = int

class ProvinceSchema:
    def __init__(self, province_names : Iterable[str]):
        self._province_names = list(province_names);
        self._num_provinces = len(self._province_names)

    def valid_id(self, province_id: ProvinceId) -> bool:
        return 0 <= province_id < self.num_provinces()

    def num_provinces(self) -> int:
        return self._num_provinces

    def name_of_province(self, province : ProvinceId) -> str:
        assert province < self._num_provinces
        return self._province_names[province]

    def province_of_name(self, name : str) -> ProvinceId:
        return self._province_names.index(name)

ListingId = int

class MarketPriceSchema:
    def __init__(self, local_schema : TradeGoodsSchema, province_schema : ProvinceSchema):
        self._local_schema = local_schema
        self._province_schema = province_schema

    def local_width(self) -> int:
        return self._local_schema.width()

    def global_width(self) -> int:
        return self.local_width() * self._province_schema.num_provinces()
    
    def province_schema(self) -> ProvinceSchema:
        return self._province_schema

    def start_of_province(self, province : ProvinceId) -> int:
        assert province < self._province_schema.num_provinces()
        return province * self.local_width()
    
    def slice_of_province(self, province : ProvinceId) -> slice:
        offset = self.start_of_province(province)
        return slice(offset,offset + self.local_width())

    def local_schema(self) -> TradeGoodsSchema:
        return self._local_schema

    def good_in_province(self, good: GoodId, province: ProvinceId) -> ListingId:
        assert self._local_schema.valid_id(good)
        assert self._province_schema.valid_id(province)
        return self.start_of_province(province) + good

    def listing_of_good_in_province(self, good: str, province: str) -> ListingId:
        good_id = self.local_schema().good_of_name(good)
        province_id = self.province_schema().province_of_name(province)
        return self.good_in_province(good_id, province_id)

    
    def slice_in_province(self, province : ProvinceId, sl : slice) -> slice:
        offset = self.start_of_province(province)
        return slice(offset + sl.start, offset + sl.stop, sl.step)

    def production_slice_in_province(self, province : ProvinceId) -> slice:
        return self.slice_in_province(province,
                                      self.local_schema().production_slice())

    def placement_of_province(self, province : ProvinceId) -> Placement:
        return Placement(self.global_width(),
                         self.production_slice_in_province(province))

    def decompose(self, listingId: ListingId) -> tuple[ProvinceId, GoodId]:
        w = self.local_width()
        (provinceId,goodId) = divmod(listingId, w)
        return (provinceId, goodId)

    def ix_to_str(self, listing: int) -> str:
        (provinceId, goodId) = self.decompose(listing)
        provinceName = self.province_schema().name_of_province(provinceId)
        goodName = self.local_schema().name_of_good(goodId)
        return goodName + " in " + provinceName

    def list_goods_in_provinces(self,
                                goods: Optional[Iterable[str]],
                                provinces: Optional[Iterable[str]]) -> Iterable[ListingId]:
        if goods == None:
            goods = self.local_schema()._good_names
        if provinces == None:
            provinces = self.province_schema()._province_names
        for province_name in provinces:
            province_id = self.province_schema().province_of_name(province_name)
            for good_name in goods:
                good_id = self.local_schema().good_of_name(good_name)
                yield self.good_in_province(good_id, province_id)

    def list_provinces_over_goods(self,
                                  goods: Optional[Iterable[str]],
                                  provinces: Optional[Iterable[str]]) -> Iterable[ListingId]:
        if goods == None:
            goods = self.local_schema()._good_names
        if provinces == None:
            provinces = self.province_schema()._province_names
        for good_name in goods:
            good_id = self.local_schema().good_of_name(good_name)
            for province_name in provinces:
                province_id = self.province_schema().province_of_name(province_name)
                yield self.good_in_province(good_id, province_id)

    #def ix_list_provinces_major():

class LaborMarketPriceSchema(MarketPriceSchema):
    def __init__(self, local_schema : LaborTradeGoodsSchema, province_schema : ProvinceSchema):
        super().__init__(local_schema, province_schema)

    # This is an override just to have the more specific types
    def local_schema(self) -> LaborTradeGoodsSchema:
        return cast(LaborTradeGoodsSchema, self._local_schema)

    def labour_in_province(self, province : ProvinceId) -> ListingId:
        return self.good_in_province(self.local_schema().labour(), province)

    def labor_placement_of_province(self, province : ProvinceId) -> LaborPlacement:
        return LaborPlacement(self.global_width(),
                         self.production_slice_in_province(province),
                         self.labour_in_province(province))
