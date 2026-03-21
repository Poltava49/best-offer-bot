"""Tests for Telegram bot handlers."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Message, Update

from src.app.telegram_bot import (
    build_bot,
    handle_text,
    info,
    parsing,
    start,
    stop,
)
from src.exceptions import MessageHandlerBotError


def make_update(text: str = "test") -> Update:
    """Create mock Update with message."""
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.text = text
    return update


@pytest.mark.asyncio
async def test_start_command() -> None:
    """Test /start command."""
    update = make_update()
    context: MagicMock = MagicMock()

    await start(update, context)

    update.message.reply_text.assert_awaited_once()  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_start_no_message() -> None:
    """Test /start without message raises error."""
    update = make_update()
    update.message = None
    context: MagicMock = MagicMock()

    with pytest.raises(MessageHandlerBotError):
        await start(update, context)


@pytest.mark.asyncio
async def test_stop_command() -> None:
    """Test /stop command."""
    update = make_update()
    context: MagicMock = MagicMock()

    await stop(update, context)

    update.message.reply_text.assert_awaited_once()  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_stop_no_message() -> None:
    """Test /stop without message raises error."""
    update = make_update()
    update.message = None
    context: MagicMock = MagicMock()

    with pytest.raises(MessageHandlerBotError):
        await stop(update, context)


@pytest.mark.asyncio
async def test_info_command() -> None:
    """Test /info command."""
    update = make_update()
    context: MagicMock = MagicMock()

    await info(update, context)

    update.message.reply_text.assert_awaited_once()  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_parsing_no_query() -> None:
    """Test /parsing without saved query."""
    update = make_update()
    context: MagicMock = MagicMock()
    context.user_data = {}

    await parsing(update, context)

    update.message.reply_text.assert_awaited_once_with("Нет сохраненного запроса")  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_parsing_with_query() -> None:
    """Test /parsing with saved query."""
    update = make_update()
    context: MagicMock = MagicMock()
    context.user_data = {"last_message": "iphone 15"}

    mock_df: MagicMock = MagicMock()
    mock_df.iterrows.return_value = []

    with patch(
        "src.app.telegram_bot.start_parsing_wb",
        new_callable=AsyncMock,
        return_value=mock_df,
    ):
        await parsing(update, context)

    update.message.reply_text.assert_awaited()  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_handle_text() -> None:
    """Test text message handling."""
    update = make_update("hello")
    context: MagicMock = MagicMock()
    context.user_data = {}

    await handle_text(update, context)

    update.message.reply_text.assert_awaited_once_with("Вы сказали: hello")  # type: ignore[union-attr]
    assert context.user_data["last_message"] == "hello"


@pytest.mark.asyncio
async def test_handle_text_no_user_data() -> None:
    """Test text handling without user_data."""
    update = make_update("test")
    context: MagicMock = MagicMock()
    context.user_data = None

    await handle_text(update, context)

    assert context.user_data["last_message"] == "test"


def test_build_bot() -> None:
    """Test bot initialization."""
    app: Any = build_bot("test_token")

    assert app is not None
