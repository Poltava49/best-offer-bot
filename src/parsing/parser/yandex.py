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


def _normalize_href(value: str | None) -> str | None:
    if not value:
        return None
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value)


class YandexParser(Parser):
    """Create parser the Ozon marketplace."""

    def __init__(self, attributes: ParsingAttributes) -> None:
        """Initialize class with base schema for parsing."""
        self.attrs = attributes
        self.me = MarketPlace.YANDEX

    def get_products(self, query: str, count: int) -> list[Product]:
        """Load data from parsed file and convert to list."""
        filename = self._get_page_with_selenium(
            MARKETPLACES_URL_TEMPLATES[self.me](query)
        )
        products: list[Product] = []

        with Path(filename).open(encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.select(self.attrs.product_card_selector)
        for i, card in enumerate(cards):
            if i >= count:
                break

            base_url = "https://market.yandex.ru"
            link_elem = card.select_one('a[data-auto="snippet-link"]')
            if not link_elem:
                continue
            href = link_elem.get("href")
            if not href:
                continue
            url = base_url + href if href.startswith("/") else href

            title_elem = card.select_one(self.attrs.title_class)
            title = title_elem.text.strip() if title_elem else ""

            price_elem = card.select_one(self.attrs.price_class)
            price_text = price_elem.text.strip() if price_elem else ""
            price_digits = re.sub(r"\D", "", price_text)
            price = int(price_digits) if price_digits else 0

            rating_elem = card.select_one(self.attrs.rating_class)
            rating = (
                float(rating_elem.text.strip().replace(",", "."))
                if rating_elem
                else 0.0
            )

            reviews_elem = card.select_one('[data-auto="reviews"]')
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                match = re.search(r"\(([\d.]+)K?\)", reviews_text)
                if match:
                    rating_count = float(match.group(1))
                    if "K" in reviews_text and "K" in match.group(0):
                        rating_count = int(rating_count * 1000)
                    else:
                        rating_count = int(rating_count)
                else:
                    rating_count = 0
            else:
                rating_count = 0

            products.append(
                Product(
                    title=title,
                    price=price,
                    rating=rating,
                    rating_count=rating_count,
                    link=url,
                    market=self.attrs.market,
                )
            )
            logger.info("Total products collected: %s", len(products))
        return products
