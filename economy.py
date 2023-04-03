from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, TypeVar, List
import numpy.typing as npt

from schema import GoodId, ProvinceId, TradeGoodsSchema, ProvinceSchema

Bundle = npt.NDArray

@dataclass
class FactoryConfig:
    production_coefficients: Bundle

@dataclass
class TradeConfig:
    good: GoodId
    from_province: ProvinceId
    to_province: ProvinceId
    trade_factor: float

@dataclass
class ProvinceConfig:
    population: int
    utilities: Bundle 
    factories: List[FactoryConfig]
    traders: List[TradeConfig]

@dataclass
class EconomyConfig:
    goods_schema: TradeGoodsSchema
    province_schema: ProvinceSchema
    province_configs: List[ProvinceConfig]

T = TypeVar("T", bound="Economy")
class Economy(ABC):
    """Interface to implementations of the core economic functionality.
    Implementations set up the market participants and run the market."""

    @classmethod
    @abstractmethod
    def from_config(cls: Type[T], config: EconomyConfig) -> T:
        pass

    @abstractmethod
    def population_in_province(self, province: ProvinceId) -> int:
        pass
