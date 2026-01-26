import os
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

load_dotenv('../.env')
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
    await update.message.reply_text("Парсинг запущен...", reply_markup=stop_markup)


async def info(update, context):
    await update.message.reply_text("Информация о боте...", reply_markup=stop_markup)


async def handle_text(update, context):
    await update.message.reply_text(f"Вы сказали: {update.message.text}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('parsing', parsing))
    app.add_handler(CommandHandler('info', info))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()