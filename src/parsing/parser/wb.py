"""Custom wildberries parser with selenium."""

import logging
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup

from src.app.models import MarketPlace
from src.parsing import Parser, ParsingAttributes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

wb_attr = ParsingAttributes(
    title_class="product-card__name-separator",
    price_class="ins.price__lower-price",
    rating_class="address-rate-mini address-rate-mini--sm",
    rating_count_class="product-card__count",
    product_card_selector="a.product-card__link.j-card-link.j-open-full-product-card",
    market=MarketPlace.WB,
)


class WbParser(Parser):
    """Create parser the Wildberries marketplace."""

    def __init__(self, attributes: ParsingAttributes) -> None:
        """Initialize class with base schema for parsing."""
        self.attrs = attributes

    def get_products(self, filename: str, count_products: int) -> dict:
        """Load data from parsed file and convert to DataFrame."""
        products_dict = defaultdict(list)
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
            rating_class = rating_class_elem.text.strip() if title_elem else ""

            rating_count_class_elem = product.select_one(self.attrs.rating_class_count)
            rating_count_class = (
                rating_count_class_elem.text.strip() if title_elem else ""
            )

            url = product.get("href", "")
            price = (
                product.select_one(self.attrs.price_class)
                .text.strip()
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
