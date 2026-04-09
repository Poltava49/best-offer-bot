"""
Selenium application package.

This package contains the Selenium methods and  initialization logic.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
from . import models

import anyio
from selenium import webdriver

from src.parsing.parser import Parser
from src.parsing.parser.wb import WbParser, wb_attr

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

wb_parser = WbParser(attributes=wb_attr)


def get_parser(marketplace: models.MarketPlace) -> Parser:
    """Return parser instance for the specified marketplace."""
    makrets = {
            models.MarketPlace.WB: WbParser,
            }
    p = markets.get(marketplace)
    if not p:
        raise ValueError(msg)

    return p()


async def find_best_offer(query: str, marketplaces: list[models.MarketPlace], count_products: int = 10) -> dict:
    """Async call corotine."""
    finall_results = list()
    filenames = list()
    try:
        for marketplace in marketplaces:
            try:
                parser = get_parser(marketplace)
                finall_results.append(parser.get_products(query, count=count_products))
            except Exception as e:
                logger.error(f"Error parsing {marketplace}: {e}")
                final_results[marketplace] = {"error": str(e), "products": []}
    finally:
        for filename in filenames:
            try:
                await anyio.Path(filename).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete {filename}: {e}")
    return final_results
