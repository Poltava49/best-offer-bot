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

from src.parsing import Parser
from src.parsing.parser.wb import WbParser, wb_attr

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

wb_parser = WbParser(attributes=wb_attr)


def get_parser(marketplace: str) -> Parser:
    """Return parser instance for the specified marketplace."""
    if marketplace == "WB":
        return WbParser(attributes=wb_attr)
    msg = f"Unknown marketplace: {marketplace}"
    raise ValueError(msg)


async def parse(query: str) -> str:
    """Async wrapper for Selenium."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,  # use ThreadPoolExecutor defolt
        _parse_with_selenium,  # sync func
        query,
    )


def _parse_with_selenium(query: str, link: str) -> str:
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
        url = f"{link}{quote(query)}"
        driver.get(url)
        logger.info("Open search - %s", url)

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


async def start_parsing(query: str, marketplace: str, count_products: int = 10) -> dict:
    """Async call corotine."""
    filename = await parse(query=query)
    parser = get_parser(marketplace)
    try:
        return parser.get_products(filename=filename, count_products=count_products)
    finally:
        await anyio.Path(filename).unlink(missing_ok=True)
