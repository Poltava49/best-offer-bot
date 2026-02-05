import os
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from .parsers import wb_parser


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

start_keyboard = [['/parsing', '/info']]
stop_keyboard = [['/stop']]
start_markup = ReplyKeyboardMarkup(
    keyboard=start_keyboard,
    resize_keyboard=True,
    one_time_keyboard=False
)
stop_markup = ReplyKeyboardMarkup(
    keyboard=stop_keyboard,
    resize_keyboard=True,
    one_time_keyboard=False
)


async def start(update, context):
    text = (
        "Привет! Я — твой цифровой шпион на маркетплейсах.\n"
        "Я в реальном времени отслеживаю цены на Wildberries и Ozon.\n"
        "Просто скажи, какие товары или артикулы интересуют,\n"
        "и я начну мониторить конкурентов, скидки и динамику. Данные — твоя суперсила!"
    )
    await update.message.reply_text(text, reply_markup=start_markup)


async def stop(update, context):
    await update.message.reply_text(
        "Пока! Клавиатура удалена.",
        reply_markup=ReplyKeyboardRemove()
    )


async def parsing(update, context):
    query = update.message.text
    context.user_data['query'] = query
    await send_dataframe_as_html(user_query=query)
    await update.message.reply_text("Парсинг запущен...", reply_markup=stop_markup)


async def info(update, context):
    await update.message.reply_text("Информация о боте...", reply_markup=stop_markup)


async def handle_text(update, context):
    await update.message.reply_text(f"Вы сказали: {update.message.text}")


async def send_dataframe_as_html(query):
    print(get_products(filename=parse_wb_with_selenium(query='iphone 17 терабайт'), count_products=10))
    df =
    html_table = df.to_html(index=False, classes='table table-striped')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Результаты парсинга Wildberries</h2>
        {html_table}
    </body>
    </html>
    """

    bio = io.BytesIO(html_content.encode('utf-8'))
    bio.name = 'products.html'

    await update.message.reply_document(
        document=bio,
        caption='HTML таблица с товарами'
    )



def build_bot():
    """Создает и настраивает Telegram бота"""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('parsing', parsing))
    app.add_handler(CommandHandler('info', info))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Бот инициализирован")
    return app




async def run_bot(bot_token: str):
    """Запускает бота в режиме polling"""
    app = build_bot(bot_token)
    logger.info("Бот запущен и ожидает сообщений...")
    await app.run_polling()

