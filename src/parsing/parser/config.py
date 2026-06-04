"""Declare marketplaces URL in global variable."""

from src.app.models import MarketPlace
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.ozon import OzonParser
from src.parsing.parser.wb import WbParser

wb_attr = ParsingAttributes(
    title_class="product-card__name-separator",
    price_class="price__lower-price",
    rating_class="address-rate-mini address-rate-mini--sm",
    rating_count_class="product-card__count",
    product_card_selector="a.product-card__link.j-card-link.j-open-full-product-card",
    market=MarketPlace.WB,
)

ozon_attr = ParsingAttributes(
    title_class="tsBody500Medium",
    price_class="tsHeadline500Medium",
    rating_class="tsBodyControl300XSmall",
    rating_count_class="c7w1_5_1-a0",
    product_card_selector="a.tile-clickable-element",
    market=MarketPlace.OZON,
)

MARKETPLACES_PARSERS: dict[MarketPlace, Parser] = {
    MarketPlace.WB: WbParser(wb_attr)
}
