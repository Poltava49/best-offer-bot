"""Custom wildberries parser with selenium."""

import logging
from pathlib import Path

from bs4 import BeautifulSoup

from src.app.models import MarketPlace, Product
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.constants import MARKETPLACES_URL_TEMPLATES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def _normalize_href(value: str | None) -> str | None:
    if not value:
        return None
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value)


class OzonParser(Parser):
    """Create parser the Ozon marketplace."""

    def __init__(self, attributes: ParsingAttributes) -> None:
        """Initialize class with base schema for parsing."""
        self.attrs = attributes
        self.me = MarketPlace.OZON

    def get_products(self, query: str, count: int) -> list[Product]:
        """Load data from parsed file and convert to list."""
        filename = self._get_page_with_selenium(
            MARKETPLACES_URL_TEMPLATES[self.me](query)
        )
        products: list[Product] = []

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

            href_value = product.get("href")
            url = _normalize_href(str(href_value) if href_value is not None else None)
            if not url:
                continue

            price_element = product.select_one(self.attrs.price_class)
            price_text = price_element.text.strip() if price_element else ""

            product_item = Product(
                title=title,
                price=int("".join(ch for ch in price_text if ch.isdigit()) or 0),
                rating=float(rating_class.replace(",", ".") or 0.0),
                rating_count=int(
                    "".join(ch for ch in rating_count_class if ch.isdigit()) or 0
                ),
                link=url,
                market=self.attrs.market,
            )
            products.append(product_item)
            logger.info("Total products collected: %s", len(products))
        return products
