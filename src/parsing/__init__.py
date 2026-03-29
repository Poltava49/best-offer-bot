"""
Parsers package for marketplace data extraction.

This package contains parsers for various marketplaces
including Wildberries, Ozon, and other platforms.
"""

from abc import ABC
from dataclasses import dataclass

from src.app import models


@dataclass(frozen=True, slots=True)
class ParsingАttributes:
    title_class: str
    price_class: str
    raiting_class: str
    raiting_count_class: str
    product_card_selector: str
    market: models.MarketPlace


class Parser(ABC):
    def __init__(self, attributes: ParsingАttributes):
        self.attributes = attributes

    def get_products(self, query: str, count: int) -> list[models.Product]: ...
