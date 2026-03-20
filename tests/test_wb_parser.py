"""Tests for Wildberries parser."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.parsers.wb import get_products, parse_wb, start_parsing_wb


def test_get_products() -> None:
    """Test parsing HTML file to DataFrame."""
    result = get_products(filename="src/parsers/wb_page.html")

    assert isinstance(result, pd.DataFrame)
    assert "model" in result.columns
    assert "price" in result.columns
    assert "url" in result.columns


def test_get_products_empty_file(tmp_path: Path) -> None:
    """Test parsing empty HTML file."""
    empty_file = tmp_path / "empty.html"
    empty_file.write_text("<html></html>")

    result = get_products(filename=str(empty_file))

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_parse_wb() -> None:
    """Test async parse_wb function."""
    with patch("src.parsers.wb._parse_wb_with_selenium") as mock_parse:
        mock_parse.return_value = "wb_page.html"

        result = await parse_wb("iphone")

        assert result == "wb_page.html"
        mock_parse.assert_called_once_with("iphone")


@pytest.mark.asyncio
async def test_start_parsing_wb() -> None:
    """Test start_parsing_wb function."""
    mock_df = pd.DataFrame(
        {"model": ["Test"], "price": ["100"], "url": ["http://test"]}
    )

    with (
        patch("src.parsers.wb.parse_wb", return_value="wb_page.html"),
        patch("src.parsers.wb.get_products", return_value=mock_df),
    ):
        result = await start_parsing_wb("iphone", count_products=5)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
