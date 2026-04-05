"""
Schema of dataclasses.

This module describes and fixes scheme of data which use in parsing web pages
"""

from dataclasses import dataclass
from enum import Enum


class MarketPlace(Enum):
    """Create constants tied to uniq values."""

    OZON = "Ozon"
    WB = "Wildberries"
    YANDEX = "YandexMarket"


@dataclass(frozen=True, slots=True)
class Product:
    """Create constants tied to product attributes."""

    title: str
    price: int
    rating: float
    rating_count: int
    link: str
    market: MarketPlace
