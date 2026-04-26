"""Constants for parsers."""

from src.app.models import MarketPlace

MARKETPLACES_URL_TEMPLATES = {
    MarketPlace.WB: lambda query: (
        f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
    ),
    MarketPlace.OZON: lambda query: f"https://www.ozon.ru/search/?text={query}",
    MarketPlace.YANDEX: lambda query: f"https://market.yandex.ru/search?text={query}",
}
