"""Declare marketplaces URL in global variable."""

from src.app.models import MarketPlace
from src.parsing import Parser, ParsingAttributes
from src.parsing.parser.wb import WbParser
from src.parsing.parser.yandex import YandexParser

wb_attr = ParsingAttributes(
    title_class=".product-card__name",
    price_class="ins.price__lower-price",
    rating_class=".address-rate-mini.address-rate-mini--sm",
    rating_count_class=".product-card__count",
    product_card_selector="div.product-card__wrapper",
    market=MarketPlace.WB,
)

yandex_attr = ParsingAttributes(
    title_class='[data-auto="snippet-title"]',
    price_class='[data-auto="snippet-price-current"]',
    rating_class=".ds-rating__value",
    rating_count_class='[data-auto="reviews"] .ds-text_color_text-secondary',
    product_card_selector='article[data-auto="searchOrganic"]',
    market=MarketPlace.YANDEX,
)

MARKETPLACES_PARSERS: dict[MarketPlace, Parser] = {
    MarketPlace.WB: WbParser(wb_attr),
    MarketPlace.YANDEX: YandexParser(yandex_attr),
}
