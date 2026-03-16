from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from telegram import KeyboardButton, Message, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.app.telegram_bot import (
    build_bot,
    handle_text,
    info,
    parsing,
    run_bot,
    start,
    stop,
)
from src.exceptions import MessageHandlerBotError


@pytest.fixture
def mock_context(mocker: MockerFixture) -> MagicMock:
    """Create mock Telegram context."""
    context: MagicMock = mocker.MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    return context


@pytest.fixture
def mock_update(mocker: MockerFixture) -> MagicMock:
    """Create mock Telegram update."""
    update: MagicMock = mocker.MagicMock(spec=Update)
    mock_message: AsyncMock = mocker.AsyncMock(spec=Message)
    mock_message.reply_text = mocker.AsyncMock()
    mock_message.text = "тестовое сообщение"
    update.message = mock_message
    return update


@pytest.fixture
def mock_start_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("/parsing"), KeyboardButton("/info")]],
        resize_keyboard=True,
    )


@pytest.fixture
def mock_stop_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("/stop")]], resize_keyboard=True
    )


@pytest.mark.asyncio
async def test_start_bot(
    mock_update: MagicMock,
    mock_context: MagicMock,
    mock_start_markup: ReplyKeyboardMarkup,
) -> None:
    """
    Check starting bot.
    """
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        "Привет! Я — твой цифровой шпион на маркетплейсах.\n"
        "Я в реальном времени отслеживаю цены на Wildberries и Ozon.\n"
        "Просто скажи, какие товары или артикулы интересуют,\n"
        "и я начну мониторить конкурентов, скидки и динамику. Данные — твоя суперсила!",
        reply_markup=mock_start_markup,
    )

    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await start(mock_update, mock_context)


@pytest.mark.asyncio
async def test_stop(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """
    Check bot stoping
    """
    await stop(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once()
    args, _kwargs = mock_update.message.reply_text.await_args
    assert args[0] == "Пока! Клавиатура удалена."
    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await stop(mock_update, mock_context)


@pytest.mark.asyncio
async def test_parsing(
    mock_update: MagicMock,
    mock_context: MagicMock,
    mock_stop_markup: ReplyKeyboardMarkup,
) -> None:
    """
    Check start parsing.
    """
    await parsing(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Парсинг запущен...", reply_markup=mock_stop_markup
    )

    bad_update = MagicMock()
    bad_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await parsing(bad_update, mock_context)


@pytest.mark.asyncio
async def test_info(
    mock_update: MagicMock,
    mock_context: MagicMock,
    mock_stop_markup: ReplyKeyboardMarkup,
) -> None:
    """
    Check pull info to user.
    """
    await info(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Информация o боте...", reply_markup=mock_stop_markup
    )

    bad_update = MagicMock()
    bad_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await info(bad_update, mock_context)


@pytest.mark.asyncio
async def test_handle_text(mock_update: MagicMock, mock_context: MagicMock) -> None:
    """
    Check pull info  to user
    """
    text_message = "тестовое сообщение"
    await handle_text(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        f"Вы сказали: {text_message}"
    )
    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await handle_text(mock_update, mock_context)


@pytest.mark.asyncio
async def test_create_and_prepare_bot_simple(mocker: MockerFixture) -> None:
    """
    Simple test for bot creation
    """
    mock_app = mocker.MagicMock()
    mocker.patch(
        "telegram.ext.Application.builder",
        return_value=mocker.MagicMock(
            token=lambda _: mocker.MagicMock(build=lambda: mock_app)
        ),
    )
    result = build_bot("test_token")
    assert result is not None


@pytest.mark.asyncio
async def test_run_bot_normal(mocker: MockerFixture) -> None:
    """Spec 1: bot work and stop"""
    mock_app = mocker.MagicMock()
    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch("src.app.telegram_bot.build_bot", return_value=mock_app)

    mock_logger = mocker.patch("src.app.telegram_bot.logger")

    await run_bot("test_token")

    mock_logger.info.assert_any_call("Stop signal received...")
    mock_app.stop.assert_called_once()
    mock_app.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_run_bot_keyboard_interrupt(mocker: MockerFixture) -> None:
    """Spec 2: user set Ctrl+C"""
    mock_app = mocker.MagicMock()
    # Log when call run_polling, take KeyboardInterrupt
    mock_app.run_polling.side_effect = KeyboardInterrupt()
    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch("src.app.telegram_bot.build_bot", return_value=mock_app)
    mock_logger = mocker.patch("src.app.telegram_bot.logger")

    await run_bot("test_token")
    # Check when received Ctrl+C
    mock_logger.info.assert_any_call("Stop signal received...")
    mock_app.stop.assert_called_once()


@pytest.mark.asyncio
async def test_run_bot_error(mocker: MockerFixture) -> None:
    """Spec 3: error while works"""
    mock_app = mocker.MagicMock()
    error_msg = "Test connection error"
    mock_app.run_polling.side_effect = Exception(error_msg)

    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch("src.app.telegram_bot.build_bot", return_value=mock_app)
    mock_logger = mocker.patch("src.app.telegram_bot.logger")

    await run_bot("test_token")

    mock_logger.exception.assert_called_once()

    # Check what bot is stopping
    mock_app.stop.assert_called_once()
    mock_app.shutdown.assert_called_once()

    # Check finish logs
    mock_logger.info.assert_any_call("Bot shutdown...")
    mock_logger.info.assert_any_call("Bot stopped")
