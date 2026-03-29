from dataclasses import dataclass
from enum import Enum


class MarketPlace(Enum):
    OZON = "Ozon"
    WB = "Wildberries"
    YANDEX = "YandexMarket"


@dataclass(frozen=True, slots=True)
class Product:
    title: str
    price: int
    raiting: float
    raiting_count: int
    link: str
    market: MarketPlace
