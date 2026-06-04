"""
Selenium application package.

This package contains the Selenium methods and  initialization logic.
"""

import logging

from src.parsing import Parser
from src.parsing.parser.config import MARKETPLACES_PARSERS

from . import models

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_parser(marketplace: models.MarketPlace) -> Parser:
    """Return parser instance for the specified marketplace."""
    match marketplace:
        case models.MarketPlace.WB:
            return MARKETPLACES_PARSERS[models.MarketPlace.WB]
        case models.MarketPlace.OZON:
            return MARKETPLACES_PARSERS[models.MarketPlace.OZON]
        case _:
            msg = f"Unknown marketplace: {marketplace}"
            raise ValueError(msg)


def find_best_offer(
    query: str, marketplaces: list[models.MarketPlace], count_products: int = 10
) -> list[models.Product]:
    """Start selenium and parse products from marketlace."""
    finall_results: list[models.Product] = []
    for marketplace in marketplaces:
        try:
            parser = get_parser(marketplace)
            finall_results.extend(parser.get_products(query, count=count_products))
        except Exception:
            logger.exception("Error parsing %s", marketplace)
    return finall_results
