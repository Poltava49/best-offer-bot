"""
Telegram bot handlers module.

This module contains all command handlers and bot initialization functions
for the Telegram bot including start, stop, parsing, info commands and
message handling.
"""

import asyncio
import logging
from typing import Any

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ExtBot,
    JobQueue,
    MessageHandler,
    filters,
)

from src.app import find_best_offer
from src.app.models import MarketPlace
from src.exceptions import MessageHandlerBotError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

start_keyboard = [["/parsing", "/info"]]
marketplace_keyboard = [
    [MarketPlace.WB.value, MarketPlace.OZON.value, MarketPlace.YANDEX.value, "/parsing"]
]
stop_keyboard = [["/stop"]]
start_markup = ReplyKeyboardMarkup(
    keyboard=start_keyboard, resize_keyboard=True, one_time_keyboard=False
)
marketplace_markup = ReplyKeyboardMarkup(
    keyboard=marketplace_keyboard, resize_keyboard=True, one_time_keyboard=True
)
stop_markup = ReplyKeyboardMarkup(
    keyboard=stop_keyboard, resize_keyboard=True, one_time_keyboard=False
)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Start bot."""
    text = (
        "Привет! Я — твой цифровой шпион на маркетплейсах.\n"
        "Я в реальном времени отслеживаю цены на Wildberries и Ozon.\n"
        "Просто скажи, какие товары или артикулы интересуют,\n"
        "и я начну мониторить конкурентов, скидки и динамику. Данные — твоя суперсила!"
    )
    if not update.message:
        raise MessageHandlerBotError

    await update.message.reply_text(text, reply_markup=start_markup)


async def stop(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop bot."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text(
        "Пока! Клавиатура удалена.", reply_markup=ReplyKeyboardRemove()
    )


async def parsing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start parsing."""
    if not update.message:
        raise MessageHandlerBotError
    if not context.user_data:
        await update.message.reply_text("Dont make any actions. Context user is empty.")
        return
    query = context.user_data.get("last_message")
    if not query or not isinstance(query, str):
        await update.message.reply_text("Нет сохраненного запроса")
        return

    marketplaces = context.user_data.get("choosen_markets")
    if not marketplaces or not isinstance(marketplaces, list):
        await update.message.reply_text("Нет выбранных маркетплейсов")
        return

    await update.message.reply_text("Start parsing...", reply_markup=stop_markup)
    products = await find_best_offer(
        query=query, marketplaces=marketplaces, count_products=5
    )

    message = f"<b>Результаты для '{query}':</b>\n\n"
    for idx, product in enumerate(products, start=1):
        message += f"<b>{idx}. {product.title}</b>\n"
        message += f"🔗 Ссылка: {product.link}\n\n"
        message += f"💫 Рейтинг: {product.rating}\n\n"
        message += f"🧮 Количество оценок: {product.rating_count}\n\n"
        message += f"💰 Цена: {product.price} ₽\n"

    await update.message.reply_text(message, parse_mode="HTML")
    context.user_data["choosen_markets"] = []


async def info(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Get info."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text("Информация o боте...", reply_markup=stop_markup)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    if not update.message:
        raise MessageHandlerBotError
    if context.user_data is None:
        context.user_data = {}
    if "last_message" not in context.user_data:
        context.user_data["last_message"] = update.message.text
    if update.effective_chat:
        context.user_data["chat_id"] = update.effective_chat.id
    await update.message.reply_text(
        f"Ищем: {context.user_data.get('last_message')} на каких маркептлейсах?",
        reply_markup=marketplace_markup,
    )
    if "choosen_markets" not in context.user_data:
        context.user_data["choosen_markets"] = []
    text = update.message.text
    try:
        market = MarketPlace(text)
    except ValueError:
        return
    context.user_data["choosen_markets"].append(market)
    logger.info("Marketplace chosen - %s", market)


def build_bot(
    token: str,
) -> Application[
    ExtBot[None],
    ContextTypes.DEFAULT_TYPE,
    dict[Any, Any],
    dict[Any, Any],
    dict[Any, Any],
    JobQueue[ContextTypes.DEFAULT_TYPE],
]:
    """Create and prepare Telegram bot."""
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("parsing", parsing))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("The bot has been initialized")
    return app


async def run_bot(bot_token: str) -> None:
    """Launch the bot in the polling mode."""
    app = build_bot(bot_token)
    stop_event = asyncio.Event()
    try:
        await app.initialize()
        await app.start()
        logger.info("Bot launched. Press Ctrl+C to stop.")
        if app.updater is None:
            logger.error("Updater is not initialized")
            return
        await app.updater.start_polling()
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("Stop signal received...")
    except Exception:
        logger.exception("An error occurred while running the bot: %s")
    finally:
        logger.info("Bot shutdown...")
        await app.stop()
        await app.shutdown()
        logger.info("Bot stopped")
