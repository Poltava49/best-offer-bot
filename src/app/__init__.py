"""
Selenium application package.

This package contains the Selenium methods and  initialization logic.
"""

import logging
from typing import Any

from src.parsing import Parser
from src.parsing.parser.config import MARKETPLACES_PARSERS

from . import models

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_parser(marketplace: models.MarketPlace) -> Parser:
    """Return parser instance for the specified marketplace."""
    parser = MARKETPLACES_PARSERS.get(marketplace)
    if not parser:
        msg = f"Unknown marketplace: {marketplace}"
        raise ValueError(msg)
    return parser


async def find_best_offer(
    query: str, marketplaces: list[models.MarketPlace], count_products: int = 10
) -> list[dict[str, Any]]:
    """Start selenium and parse products from marketlace."""
    finall_results = []
    for marketplace in marketplaces:
        try:
            parser = get_parser(marketplace)
            finall_results.append(
                parser.get_products(query, count_products=count_products)
            )
        except Exception:
            logger.exception("Error parsing %s", marketplace)
    return finall_results
