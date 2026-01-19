import asyncio
import logging
from playwright.async_api import async_playwright
from urllib.parse import quote
import random


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ozon_telegram_bot")
MAX_PRODUCTS = 15
PAGES_TO_PARSE = 2

class OzonParser:
    def __init__(self):
        self.playwright = None #переменная для хранения драйвера Playwright.
        self.browser = None # Для хранения экземпляра браузера Chromium
        self.page = None    # для хранения самой вкладки браузера
    async def human_delay(self, min_sec=1, max_sec=3):
        '''функция имитации человеческого поведения'''
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    async def setup_browser(self):
        '''Запуск драйвера playwright'''
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ],
            slow_mo=50
        )

        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            java_script_enabled=True,
            ignore_https_errors=True
        )

        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        self.page = await self.context.new_page()
        self.page.set_default_timeout(15000)
        self.page.set_default_navigation_timeout(20000)

    async def close_browser(self):
        '''Закрываем браузер'''
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def fetch_product_links(self, query, pages=2):
        try:
            encoded_query = quote(query)
            search_url = f"https://www.ozon.ru/search/?text={encoded_query}&from_global=true"

            logger.info(f"Поиск: {query}")
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            await self.human_delay(2, 3)

            current_url = self.page.url
            if "category" in current_url and "text" not in current_url:
                logger.warning("Перенаправление на категорию")
                search_url = f"https://www.ozon.ru/search/?text={encoded_query}"
                await self.page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                await self.human_delay(2, 3)

        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")

        for p in range(1, pages + 1):
            logger.info(f"Страница {p}/{pages}")

        print(self.page)



    async def search_products(self, query, pages=2, max_products=15):

        await self.setup_browser()
        links = await self.fetch_product_links(query, pages)
        print(links)



ozon_parser = OzonParser()


async def test():
    return await ozon_parser.search_products(
                query='Iphone 17',
                pages=PAGES_TO_PARSE,
                max_products=MAX_PRODUCTS
            )
result = asyncio.run(test())
print(result)
