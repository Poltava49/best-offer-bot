from dataclasses import dataclass


@dataclass
class Product:
    title: str
    price: int
    raiting: float
    raiting_count: int
    link: str
    market: str


@dataclass
class ParsingАttributes:
    title: str
    price: str
    raiting: str
    raiting_count: str
    link: str
    market: str


class Parser:
    def __init__(self, attributes: ParsingАttributes):
        self.attributes = attributes

    def get_products(self, query: str, count: int) -> Product:
        pass


class TelegramBot:
    def __init__(self, bot_token):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def get_user_query(self):
        pass

    def set_message_to_user(self, distr_price, top_products):
        pass

    def _build_bot(self):
        pass

    def _run_bot(self):
        pass


class MessageFormatter:
    def __init__(self):
        pass

    def info(self):
        pass


class PriceDistributionChartGenerator:
    def __init__(self, products):
        pass

    def get_distribution_of_products_price(self) -> Image:
        pass


class TopProductsSelector:
    def __init__(self, products):
        pass

    def get_top_n_products(self, n: int) -> Product:
        pass


bot = TelegramBot(bot_token='111')

bot.get_user_query()

wb_attrs = ParsingAttributes(
    title="aria-label",
    price="ins.price__lower-price.red-price",
    rating="address-rate-mini address-rate-mini--sm",
    rating_count="product-card__count",
    link="href",
    market="WildBerries"
)
wb_parser = Parser(attributes=wb_attrs)

parsed_products = wb_parser.get_products(query=bot.get_user_query(), count=5)
top_products = TopProductsSelector(products=parsed_products)
dist_price_products = PriceDistributionChartGenerator(products=parsed_products)
bot.set_message_to_user(distr_price=dist_price_products, top_products=top_products)
