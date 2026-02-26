import pytest
from telegram import Message, Update
from telegram.ext import (
    ContextTypes,
)

from app.telegram_bot import handle_text, info, parsing, start, stop
from exceptions import MessageHandlerBotError


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
def mock_start_markup(mocker):
    markup = mocker.MagicMock()
    mocker.patch("src.app.telegram_bot.start_markup", markup)
    return markup


@pytest.fixture
def mock_stop_markup(mocker):
    markup = mocker.MagicMock()
    mocker.patch("src.app.telegram_bot.stop_markup", markup)
    return markup


@pytest.mark.asyncio
async def test_start_bot(mock_update, mock_context, mock_start_markup) -> None:
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
async def test_stop(mock_update, mock_context) -> None:
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
async def test_parsing(mock_update, mock_context, mock_stop_markup) -> None:
    """
    Check start parsing
    """
    await parsing(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        "Парсинг запущен...", reply_markup=mock_stop_markup
    )
    mock_update.message = None
    with pytest.raises(MessageHandlerBotError):
        await parsing(mock_update, mock_context)


@pytest.mark.asyncio
async def test_info(mock_update, mock_context, mock_stop_markup) -> None:
    """
    Check pull info  to user
    """
    await info(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with(
        "Информация о боте...", reply_markup=mock_stop_markup
    )
    with pytest.raises(MessageHandlerBotError):
        mock_update.message = None
        await info(mock_update, mock_context)


@pytest.mark.asyncio
async def test_handle_text(mock_update, mock_context) -> None:
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
