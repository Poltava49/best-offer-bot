"""Custom wildberries parser with selenium."""

import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.app.models import MarketPlace, Product
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.constants import MARKETPLACES_URL_TEMPLATES

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

    def get_products(self, query: str, count: int) -> list[Product]:
        """Load data from parsed file and convert to DataFrame."""
        filename = self._get_page_with_selenium(
            MARKETPLACES_URL_TEMPLATES[self.me](query)
        )
        products: list[Product] = []

        def _to_int(value: str) -> int:
            digits = re.sub(r"\D", "", value)
            return int(digits) if digits else 0

        def _to_float(value: str) -> float:
            normalized = value.replace(",", ".").strip()
            match = re.search(r"\d+(?:\.\d+)?", normalized)
            return float(match.group(0)) if match else 0.0

        with Path(filename).open(encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        product_links_title = soup.select(self.attrs.product_card_selector)
        for i, product in enumerate(product_links_title):
            if i >= count:
                break
            title_elem = product.select_one(self.attrs.title_class)
            title = title_elem.text.strip() if title_elem else ""

            rating_class_elem = product.select_one(self.attrs.rating_class)
            rating_class = rating_class_elem.text.strip() if rating_class_elem else ""

            rating_count_class_elem = product.select_one(self.attrs.rating_count_class)
            rating_count_class = (
                rating_count_class_elem.text.strip() if rating_count_class_elem else ""
            )

            raw_url = product.get("href")
            if not raw_url:
                continue
            url = raw_url[0] if isinstance(raw_url, list) else str(raw_url)

            price_element = product.select_one(self.attrs.price_class)
            price_text = price_element.text.strip() if price_element else ""

            product_item = Product(
                title=title,
                price=_to_int(price_text),
                rating=_to_float(rating_class),
                rating_count=_to_int(rating_count_class),
                link=url,
                market=self.attrs.market,
            )
            products.append(product_item)
            logger.info("Total products collected: %s", len(products))
        return products
