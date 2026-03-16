import pandas as pd

from src.parsers.wb import _parse_wb_with_selenium, get_products, parse_wb, start_parsing_wb


def test_parse_wb_with_selenium() -> None:
    assert _parse_wb_with_selenium(query="Iphone 17") == "wb_page.html"


def test_get_products() -> None:
    result = get_products(filename="src/parsers/wb_page.html")
    assert isinstance(result,pd.DataFrame)


async def test_parse_wb() -> None:
    result = await parse_wb(query='Iphone 17')
    assert result == "wb_page.html"



