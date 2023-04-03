from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, TypeVar
import numpy.typing as npt

from schema import GoodId, ProvinceId, MarketPriceSchema

Bundle = npt.NDArray

@dataclass
class FactoryConfig:
    production_coefficients: Bundle

@dataclass
class TradeConfig:
    good: GoodId
    other_province: ProvinceId
    trade_factor: float

@dataclass
class ProvinceConfig:
    population: int
    utilities: Bundle 
    factories: [FactoryConfig]
    traders: [TradeConfig]

@dataclass
class EconomyConfig:
    goods_schema: MarketPriceSchema
    province_config: [ProvinceConfig]

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
