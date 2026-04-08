"""
Selenium application package.

This package contains the Selenium methods and  initialization logic.
"""

import asyncio
import logging
import os
import time
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import anyio
from selenium import webdriver

from src.parsing.parser import Parser
from src.parsing.parser.wb import WbParser, wb_attr

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

wb_parser = WbParser(attributes=wb_attr)


def get_parser(marketplace: str) -> Parser:
    """Return parser instance for the specified marketplace."""
    if marketplace == "wildberries":
        return WbParser(attributes=wb_attr)
    msg = f"Unknown marketplace: {marketplace}"
    raise ValueError(msg)


async def parse(query: str, marketplace: str) -> str:
    """Async wrapper for Selenium."""
    loop = asyncio.get_event_loop()
    url = ""
    if marketplace == "wildberries":
        url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
    elif marketplace == "ozon":
        url = f"https://www.ozon.ru/search/?text={query}"
    elif marketplace == "yandex.market":
        url = f"https://market.yandex.ru/search?text={query}"
    else:
        raise ValueError(f"Unsupported marketplace: {marketplace}")
    return await loop.run_in_executor(
        None,  # use ThreadPoolExecutor defolt
        _parse_with_selenium,  # sync func
        url
    )


def _parse_with_selenium(url: str) -> str:
    """Parse HTML page Wildberries by Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-webrtc")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", value=False)

    selenium_url = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")
    driver = webdriver.Remote(command_executor=selenium_url, options=options)
    try:
        # Add URL
        driver.get(url)
        logger.info("Open search - %s", link)

        # Wait for loading
        time.sleep(5)

        # Rolling page to load products
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)

        # Save HTML
        output_file = Path(f"page_{uuid4().hex}.html")
        with output_file.open("w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("HTML saved in %s", output_file)
    finally:
        driver.quit()

    return str(output_file)


async def start_parsing(query: str, marketplaces: list, count_products: int = 10) -> dict:
    """Async call corotine."""
    finall_results = list()
    filenames = list()
    try:
        for marketplace in marketplaces:
            try:
                filename = await parse(query=query, marketplace=marketplace)
                filenames.append(filename)
                parser = get_parser(marketplace)
                finall_results.append(parser.get_products(filename=filename, count_products=count_products))
            except Exception as e:
                logger.error(f"Error parsing {marketplace}: {e}")
                final_results[marketplace] = {"error": str(e), "products": []}
    finally:
        for filename in filenames:
            try:
                await anyio.Path(filename).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete {filename}: {e}")
    return final_results
