from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd



def parse_wb_with_selenium(query, max_products=10):
    """
    Parse Wildberries by Selenium
    """
    # Prepair Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)


    driver = webdriver.Chrome(options=options)

    try:
        # Add URL
        url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={quote(query)}"
        print(f"Открываю: {url}")
        driver.get(url)

        # Wait for loading
        time.sleep(5)

        # Rolling page to load products
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)

        # Save HTML
        with open('../cache/wb_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"HTML сохранен в wb_page.html")
    finally:
        driver.quit()

    return '../cache/wb_page.html'





def get_products(filename, count_products):
    """
       Load data from parsed file
    """
    products_dict = { 'model' : [],
                      'full_title': [],
                      'rating': [],
                      'grade': [],
                      'price': [],
                      'url': []
                      }
    with open(filename, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    product_links_title = soup.select('a.product-card__link.j-card-link.j-open-full-product-card')
    brands = soup.select('span.product-card__brand')
    prices = soup.select('ins.price__lower-price.red-price')
    grades = soup.select('span.product-card__count')
    grades_counts = [element.text.strip() for element in grades]
    ratings = soup.select('span.address-rate-mini.address-rate-mini--sm')
    ratings_list = [element.text.strip() for element in ratings]

    for i, product in enumerate(product_links_title):
        if i >= count_products:
            break

        aria_label = product.get('aria-label', '')
        url = product.get('href', '')

        # Get brand and price by index
        model = brands[i].text.strip() if i < len(brands) else ''
        price = prices[i].text.strip().replace('\xa0', ' ').replace('₽','').replace(' ','') if i < len(prices) else ''
        grade = grades_counts[i]
        rating = ratings_list[i]

        products_dict['model'].append(model)
        products_dict['full_title'].append(aria_label)
        products_dict['rating'].append(rating)
        products_dict['grade'].append(grade)
        products_dict['price'].append(price)
        products_dict['url'].append(url)

    df = pd.DataFrame(products_dict)
    return df


















# import random
# import requests
# import json
# from urllib.parse import quote
# import time
#
#
#
# query = "iphone 15"
#
# # encoded_query = quote(query)
#
# url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
#
# params = {
#     'query': query,
#     'resultset': 'catalog',
#     'sort': 'popular',
#     'page': 1,
#     'appType': 1,
#     'curr': 'rub',
#     'dest': -1257786,
#     'spp': 30,
#     'regions': '80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,114',
# }
#
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Accept': 'application/json, text/plain, */*',
#     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Referer': 'https://www.wildberries.ru/',
#     'Origin': 'https://www.wildberries.ru',
# }
#
#
# print(f"🔍 Поиск: '{query}'")
#
# delay = 1
# for i in range(5):
#     print(f"Попытка {i+1}, ждем {delay} сек.")
#     time.sleep(delay)
#     response = requests.get(url, params=params, headers=headers, timeout=40)
#     print(type(response))
#     print(response.status_code)
#     print(response.json())
#     # data = response.json()
#     # products = data.get('products', [])
#     # print(product.get('brand', ''))
#     delay *= 2
#
#
#
# # print(f"📊 Статус: {response.status_code}")
# #
# # print(response)
