"""Declare marketplaces URL in global variable."""

from src.app.models import MarketPlace
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.wb import WbParser

wb_attr = ParsingAttributes(
    title_class=".product-card__name",
    price_class="ins.price__lower-price",
    rating_class=".address-rate-mini.address-rate-mini--sm",
    rating_count_class=".product-card__count",
    product_card_selector="div.product-card__wrapper",
    market=MarketPlace.WB,
)

MARKETPLACES_PARSERS: dict[MarketPlace, Parser] = {MarketPlace.WB: WbParser(wb_attr)}
