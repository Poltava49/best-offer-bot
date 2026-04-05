"""
Parsers package for marketplace data extraction.

This package contains parsers for various marketplaces
including Wildberries, Ozon, and other platforms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.app import models


@dataclass(frozen=True, slots=True)
class ParsingAttributes:
    """Create constants tied to parser attributes."""

    title_class: str
    price_class: str
    rating_class: str
    rating_count_class: str
    product_card_selector: str
    market: models.MarketPlace


class Parser(ABC):
    """Create parser abstract classes."""

    @abstractmethod
    def __init__(self, attributes: ParsingAttributes) -> None:
        """Initialize parser with parsing attributes."""

    @abstractmethod
    def get_products(self, query: str, count: int) -> list[models.Product]:
        """Get product of parsing and take to bot."""
