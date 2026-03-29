from src.app.models import Product
from src.parsing import Parser


class BestOfferAnalyzer:
    __slots__ = ["parser"]

    def __init__(self, parser: Parser):
        self.parser = parser

    def get_distribution_of_products_price(self) -> bytes:
        # TODO
        ...

    def get_top_n_products(self, n: int) -> list[Product]:
        # TODO
        ...
