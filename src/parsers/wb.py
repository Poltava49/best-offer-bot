"""Custom wildberries parser with selenium."""

import asyncio
import logging
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame
from uuid import uuid4
from selenium import webdriver

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def parse_wb(query: str) -> str:
    """Async wrapper for Selenium."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,  # use ThreadPoolExecutor defolt
        _parse_wb_with_selenium,  # sync func
        query,
    )


def _parse_wb_with_selenium(query: str) -> str:
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
        url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={quote(query)}"
        driver.get(url)
        logger.info("Open search - %s", url)

        # Wait for loading
        time.sleep(5)

        # Rolling page to load products
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)

        # Save HTML
        output_file = Path(f"wb_page_{uuid4().hex}.html")
        with output_file.open("w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("HTML saved in %s", output_file)
    finally:
        driver.quit()

    return str(output_file)


def get_products(filename: str, count_products: int = 10) -> DataFrame:
    """Load data from parsed file and convert to DataFrame."""
    products_dict = defaultdict(list)
    with Path(filename).open(encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    product_links_title = soup.select(
        "a.product-card__link.j-card-link.j-open-full-product-card"
    )
    brands = soup.select("span.product-card__brand")
    prices = soup.select("ins.price__lower-price.red-price")
    for i, product in enumerate(product_links_title):
        if i >= count_products:
            break

        aria_label = product.get("aria-label", "")
        url = product.get("href", "")

        # Get brand and price by index
        model = brands[i].text.strip() if i < len(brands) else ""
        price = (
            prices[i]
            .text.strip()
            .replace("\xa0", " ")
            .replace("₽", "")
            .replace(" ", "")
            if i < len(prices)
            else ""
        )

        products_dict["model"].append(model)
        products_dict["full_title"].append(aria_label)
        products_dict["price"].append(price)
        products_dict["url"].append(url)
    return pd.DataFrame(products_dict)


async def start_parsing_wb(query: str, count_products: int = 10) -> DataFrame:
    """Async call corotine."""
    filename = await parse_wb(query=query)
    try:
        return get_products(filename=filename, count_products=count_products)
    finally:
        Path(filename).unlink(missing_ok=True)
