"""
Parsers package for marketplace data extraction.

This package contains parsers for various marketplaces
including Wildberries, Ozon, and other platforms.
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import undetected_chromedriver as uc

from src.app import models

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


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

    def _get_page_with_selenium(self, url: str) -> str:
        """Parse HTML page using undetected-chromedriver to bypass bot detection."""
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")

        chromium_path = os.getenv("CHROMIUM_PATH", "/usr/bin/chromium")
        chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        driver = uc.Chrome(
            options=options,
            driver_executable_path=chromedriver_path,
            browser_executable_path=chromium_path,
            version_main=None,
        )
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        output_file = Path(f"page_{uuid4().hex}.html")
        try:
            driver.get(url)
            logger.info("Open search - %s", url)
            time.sleep(5)
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
            with output_file.open("w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info("HTML saved in %s", output_file)
        finally:
            driver.quit()

        return str(output_file)
