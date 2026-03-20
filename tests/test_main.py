"""Tests for main entry point."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions import DatabaseConnectionError


@pytest.mark.asyncio
async def test_main_keyboard_interrupt() -> None:
    """Test main function with keyboard interrupt."""
    with (
        patch.dict("os.environ", {"BOT_TOKEN": "fake_token"}),
        patch("src.main.connect_to_db"),
        patch("src.main.run_bot", side_effect=KeyboardInterrupt),
        patch("src.main.logger") as mock_logger,
    ):
        import src.main as main_module  # noqa: PLC0415

        await main_module.main()

        mock_logger.info.assert_any_call("Stopping the bot...")


@pytest.mark.asyncio
async def test_main_success() -> None:
    """Test main function successful run."""
    with (
        patch.dict("os.environ", {"BOT_TOKEN": "fake_token"}),
        patch("src.main.connect_to_db"),
        patch("src.main.run_bot", new_callable=AsyncMock),
        patch("src.main.logger") as mock_logger,
    ):
        import src.main as main_module  # noqa: PLC0415

        await main_module.main()

        mock_logger.info.assert_any_call("Launching a marketplace parser bot...")


def test_main_no_bot_token() -> None:
    """Test exit when BOT_TOKEN is not found (lines 26-27)."""
    mock_logger = MagicMock()
    with (
        patch("sys.exit") as mock_exit,
        patch("src.main.os.getenv", return_value=None),
        patch("logging.getLogger", return_value=mock_logger),
    ):
        import importlib  # noqa: PLC0415

        import src.main as main_module  # noqa: PLC0415

        importlib.reload(main_module)

        mock_logger.info.assert_called_with("BOT_TOKEN not found in .env file")
        mock_exit.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_main_db_connection_error() -> None:
    """Test database connection error logging (lines 37-38)."""
    with (
        patch.dict("os.environ", {"BOT_TOKEN": "fake_token"}),
        patch("src.main.connect_to_db", side_effect=DatabaseConnectionError),
        patch("src.main.run_bot", new_callable=AsyncMock),
        patch("src.main.logger") as mock_logger,
    ):
        import src.main as main_module  # noqa: PLC0415

        await main_module.main()

        mock_logger.exception.assert_called_once()


@pytest.mark.asyncio
async def test_main_run_bot_error() -> None:
    """Test run_bot exception logging (lines 44-45)."""
    with (
        patch.dict("os.environ", {"BOT_TOKEN": "fake_token"}),
        patch("src.main.connect_to_db"),
        patch("src.main.run_bot", side_effect=Exception("Test error")),
        patch("src.main.logger") as mock_logger,
    ):
        import src.main as main_module  # noqa: PLC0415

        await main_module.main()

        mock_logger.exception.assert_called_once_with("Error in bot: %s")
