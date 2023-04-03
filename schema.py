from typing import Iterable

from placement import Placement, LabourPlacement

# These schema classes are tightly coupled. They extendend each other and make
# assumptions about each others implementation. This is not nice but should be
# fine for now!
GoodId = int

class GoodsSchema:
    def __init__(self, good_names : Iterable[str]):
        self._good_names = list(good_names);
        self._num_goods = len(self._good_names)
        
    def valid_id(self, good_id: GoodId) -> bool:
        return 0 <= good_id and good_id < self.num_goods()

    def num_goods(self) -> int:
        return self._num_goods

    def name_of_good(self, good : GoodId) -> str:
        assert good < self.num_goods()
        return self._good_names[good]

    def good_of_name(self, name : str) -> GoodId:
        return self._good_names.index(name)
    
    def placement(self) -> Placement:
        return Placement(self.num_goods(), slice(0, self._num_goods))


class TradeGoodsSchema(GoodsSchema):
    def __init__(self, trade_good_names : Iterable[str], fixed_good_names : Iterable[str]):
        #self._good_names = list(goods);
        self._num_trade_goods = len(trade_good_names)
        self._num_fixed_goods = len(fixed_good_names)
        good_names = trade_good_names + fixed_good_names
        super().__init__(good_names)

    def is_trade_good(self, good : GoodId) -> bool:
        return good < self._num_trade_goods

    def trade_slice(self) -> slice:
        return slice(0, self._num_trade_goods)
    
    def trade_goods(self) -> Iterable[GoodId]:
        ts = self.trade_slice()
        return range(ts.start, ts.stop)

class LabourTradeGoodsSchema(TradeGoodsSchema):
    def __init__(self, trade_good_names : Iterable[str], fixed_good_names : Iterable[str]):
        extended_fixed_good_names = list(fixed_good_names) + ["labour"]
        super().__init__(trade_good_names, extended_fixed_good_names)

    def labour(self) -> GoodId:
        return self.num_goods() - 1

    def production_slice(self) -> slice:
        return slice(0,self.num_goods() - 1)
    
    def labour_placement(self) -> LabourPlacement:
        return LabourPlacement(self.num_goods(), self.production_slice(),
                               self.labour())

ProvinceId = int

class ProvinceSchema:
    def __init__(self, province_names : Iterable[str]):
        self._province_names = list(province_names);
        self._num_provinces = len(self._province_names)

    def valid_id(self, province_id: ProvinceId) -> bool:
        return 0 <= province_id and province_id < self.num_provinces()

    def num_provinces(self) -> int:
        return self._num_provinces

    def name_of_province(self, province : ProvinceId) -> str:
        assert province < self._num_provinces
        return self._province_names[province]

    def province_of_name(self, name : str) -> ProvinceId:
        return self._province_names.index(name)

MarketPriceId = int

class MarketPriceSchema:
    def __init__(self, local_schema : GoodsSchema, province_schema : ProvinceSchema):
        self._local_schema = local_schema
        self._province_schema = province_schema

    def local_width(self) -> int:
        return self._local_schema.num_goods()

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

    def local_schema(self) -> GoodsSchema:
        return self._local_schema

    def good_in_province(self, province: ProvinceId, good: GoodId) -> MarketPriceId:
        assert self._local_schema.valid_id(good)
        assert self._province_schema.valid_id(province)
        return self.start_of_province(province) + good
    
    def slice_in_province(self, province : ProvinceId, sl : slice) -> slice:
        offset = self.start_of_province(province)
        return slice(offset + sl.start, offset + sl.stop, sl.step)

    def labour_in_province(self, province : ProvinceId) -> MarketPriceId:
        assert isinstance(self.local_schema(), LabourTradeGoodsSchema)
        return self.good_in_province(province, self.local_schema().labour())

    def production_slice_in_province(self, province : ProvinceId) -> slice:
        assert isinstance(self.local_schema(), LabourTradeGoodsSchema)
        return self.slice_in_province(province,
                                      self.local_schema().production_slice())

    def placement_in_province(self, province : ProvinceId) -> Placement:
        return Placement(self.global_width(),
                         self.production_slice_in_province(province))
    
    def labour_placement_in_province(self, province : ProvinceId) -> Placement:
        return LabourPlacement(self.global_width(),
                         self.production_slice_in_province(province),
                         self.labour_in_province(province))
