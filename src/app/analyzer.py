"""
Analyzer module.

This module build simple visualization and analitics on parsing data
"""

from src.app.models import Product
from src.parsing import Parser


class BestOfferAnalyzer:
    """Analyzes parsed product data to generate insights and visualizations."""

    __slots__ = ["parser"]

    def __init__(self, parser: Parser) -> None:
        """Initialize analyzer with object Parser."""
        self.parser = parser

    def get_distribution_of_products_price(self) -> bytes:
        """Generate plot figure with price distribution by user query."""
        ...  # noqa: PIE790

    def get_top_n_products(self, n: int) -> list[Product]:
        """Calculate top-5 products by weighted scores."""
        ...  # noqa: PIE790
