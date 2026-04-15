"""Custom wildberries parser with selenium."""

import logging
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from src.app.models import MarketPlace
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.config import MARKETPLACES_URL_TEMPLATES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class WbParser(Parser):
    """Create parser the Wildberries marketplace."""

    def __init__(self, attributes: ParsingAttributes) -> None:
        """Initialize class with base schema for parsing."""
        self.attrs = attributes
        self.me = MarketPlace.WB

    def get_products(self, query: str, count_products: int) -> dict[str, list[Any]]:
        """Load data from parsed file and convert to DataFrame."""
        filename = self._get_page_with_selenium(
            MARKETPLACES_URL_TEMPLATES[self.me](query)
        )
        products_dict: dict[str, list[Any]] = {
            "title": [],
            "url": [],
            "rating_class": [],
            "rating_count_class": [],
            "price": [],
        }
        with Path(filename).open(encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        product_links_title = soup.select(self.attrs.product_card_selector)
        for i, product in enumerate(product_links_title):
            if i >= count_products:
                break
            title_elem = product.select_one(self.attrs.title_class)
            title = title_elem.text.strip() if title_elem else ""

            rating_class_elem = product.select_one(self.attrs.rating_class)
            rating_class = rating_class_elem.text.strip() if rating_class_elem else ""

            rating_count_class_elem = product.select_one(self.attrs.rating_count_class)
            rating_count_class = (
                rating_count_class_elem.text.strip() if rating_count_class_elem else ""
            )

            url = product.get("href", "")
            price_element = product.select_one(self.attrs.price_class)
            if price_element:
                price = (
                    price_element.text.strip()
                    .replace("\xa0", " ")
                    .replace("₽", "")
                    .replace(" ", "")
                )
            products_dict["title"].append(title)
            products_dict["url"].append(url)
            products_dict["rating_class"].append(rating_class)
            products_dict["rating_count_class"].append(rating_count_class)
            products_dict["price"].append(price)
        return products_dict
