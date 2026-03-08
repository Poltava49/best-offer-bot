import pytest
from telegram import Update, Message, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
from src.app.telegram_bot import start, stop, parsing, info, handle_text, build_bot, run_bot
from src.exceptions import MessageHandlerBotError
from unittest.mock import MagicMock


@pytest.fixture
def mock_update(mocker):
    update = mocker.MagicMock(spec=Update)
    mock_message = mocker.AsyncMock(spec=Message)
    mock_message.reply_text = mocker.AsyncMock()
    mock_message.text = "тестовое сообщение"
    update.message = mock_message
    return update


@pytest.fixture
def mock_context(mocker):
    return mocker.MagicMock(spec=ContextTypes.DEFAULT_TYPE)


@pytest.fixture
def mock_start_markup():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("/parsing"), KeyboardButton("/info")]],
        resize_keyboard=True
    )


@pytest.fixture
def mock_stop_markup():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("/stop")]],
        resize_keyboard=True
    )


@pytest.mark.asyncio
async def test_start_bot(mock_update, mock_context, mock_start_markup):
    """
    Сheck starting bot
    """
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        "Привет! Я — твой цифровой шпион на маркетплейсах.\n"
        "Я в реальном времени отслеживаю цены на Wildberries и Ozon.\n"
        "Просто скажи, какие товары или артикулы интересуют,\n"
        "и я начну мониторить конкурентов, скидки и динамику. Данные — твоя суперсила!",
        reply_markup=mock_start_markup,
    )
    with pytest.raises(MessageHandlerBotError):
        mock_update.message = None
        await start(mock_update, mock_context)


@pytest.mark.asyncio
async def test_stop(mock_update, mock_context):
    """
    Check bot stoping
    """
    await stop(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once()
    args, kwargs = mock_update.message.reply_text.await_args
    assert args[0] == "Пока! Клавиатура удалена."
    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await stop(mock_update, mock_context)


@pytest.mark.asyncio
async def test_parsing(mock_update, mock_context, mock_stop_markup):
    """
    Check start parsing
    """
    await parsing(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Парсинг запущен...", reply_markup=mock_stop_markup
    )
    bad_update = MagicMock()
    bad_update.message = None
    print(f"bad_update.message = {bad_update.message}")

    with pytest.raises(MessageHandlerBotError) as exc_info:
        await parsing(bad_update, mock_context)


@pytest.mark.asyncio
async def test_info(mock_update, mock_context, mock_stop_markup):
    """
    Check pull info  to user
    """
    await info(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "Информация о боте...", reply_markup=mock_stop_markup
    )
    mock_update = MagicMock()
    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await info(mock_update, mock_context)


@pytest.mark.asyncio
async def test_handle_text(mock_update, mock_context):
    """
    Check pull info  to user
    """
    text_message = "тестовое сообщение"
    await handle_text(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        f"Вы сказали: {text_message}"
    )
    with pytest.raises(MessageHandlerBotError):
        mock_update.message = None
        await handle_text(mock_update, mock_context)


@pytest.mark.asyncio
async def test_create_and_prepare_bot_simple(mocker):
    """
    Simple test for bot creation
    """
    mock_app = mocker.MagicMock()
    mocker.patch('telegram.ext.Application.builder', return_value=mocker.MagicMock(
        token=lambda x: mocker.MagicMock(build=lambda: mock_app)
    ))
    result = build_bot("test_token")
    assert result is not None


@pytest.mark.asyncio
async def test_run_bot_normal(mocker):
    """Spec 1: bot work and stop"""
    mock_app = mocker.MagicMock()
    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch('src.app.telegram_bot.build_bot', return_value=mock_app)

    mock_logger = mocker.patch('src.app.telegram_bot.logger')

    await run_bot("test_token")

    mock_app.run_polling.assert_called_once()
    mock_logger.info.assert_any_call("Bot launched. Press Ctrl+C to stop.")
    mock_app.stop.assert_called_once()


@pytest.mark.asyncio
async def test_run_bot_keyboard_interrupt(mocker):
    """Spec 2: user set Ctrl+C"""
    mock_app = mocker.MagicMock()
    # Log when call run_polling, take KeyboardInterrupt
    mock_app.run_polling.side_effect = KeyboardInterrupt()
    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch('src.app.telegram_bot.build_bot', return_value=mock_app)
    mock_logger = mocker.patch('src.app.telegram_bot.logger')

    await run_bot("test_token")
    # Check when received Ctrl+C
    mock_logger.info.assert_any_call("Stop signal received...")
    mock_app.stop.assert_called_once()


@pytest.mark.asyncio
async def test_run_bot_error(mocker):
    """Spec 3: error while works"""
    mock_app = mocker.MagicMock()
    error_msg = "Test connection error"
    mock_app.run_polling.side_effect = Exception(error_msg)

    mock_app.stop = mocker.AsyncMock()
    mock_app.shutdown = mocker.AsyncMock()

    mocker.patch('src.app.telegram_bot.build_bot', return_value=mock_app)
    mock_logger = mocker.patch('src.app.telegram_bot.logger')

    await run_bot("test_token")

    # Check correct logs
    expected_error_msg = f"An error occurred while running the bot: {error_msg}"
    mock_logger.error.assert_called_once_with(expected_error_msg)

    # Check what bot is stopping 
    mock_app.stop.assert_called_once()
    mock_app.shutdown.assert_called_once()

    # Check finish logs
    mock_logger.info.assert_any_call("Bot shutdown...")
    mock_logger.info.assert_any_call("Bot stopped")
