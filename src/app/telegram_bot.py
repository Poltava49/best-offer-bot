"""
Telegram bot handlers module.

This module contains all command handlers and bot initialization functions
for the Telegram bot including start, stop, parsing, info commands and
message handling.
"""

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

from src.exceptions import MessageHandlerBotError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

start_keyboard = [["/parsing", "/info"]]
stop_keyboard = [["/stop"]]
start_markup = ReplyKeyboardMarkup(
    keyboard=start_keyboard, resize_keyboard=True, one_time_keyboard=False
)
stop_markup = ReplyKeyboardMarkup(
    keyboard=stop_keyboard, resize_keyboard=True, one_time_keyboard=False
)


async def start(update: Update) -> None:
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


async def stop(update: Update) -> None:
    """Stop bot."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text(
        "Пока! Клавиатура удалена.", reply_markup=ReplyKeyboardRemove()
    )


async def parsing(update: Update) -> None:
    """Start parsing."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text("Парсинг запущен...", reply_markup=stop_markup)


async def info(update: Update) -> None:
    """Get info."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text("Информация o боте...", reply_markup=stop_markup)


async def handle_text(update: Update) -> None:
    """Handle text messages."""
    if not update.message:
        raise MessageHandlerBotError
    await update.message.reply_text(f"Вы сказали: {update.message.text}")


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
    try:
        logger.info("Bot launched. Press Ctrl+C to stop.")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Stop signal received...")
    except Exception:
        logger.exception("An error occurred while running the bot: %s")
    finally:
        logger.info("Bot shutdown...")
        await app.stop()
        await app.shutdown()
        logger.info("Bot stopped")
