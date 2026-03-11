import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from src.exceptions import DatabaseConnectionError

sys.exit = MagicMock()

with patch("os.getenv", return_value="test_token_123"):
    from src.main import main


@pytest.mark.asyncio
async def test_main_up_db(mocker: MockerFixture) -> None:
    """
    Check catch db error
    """
    mocker.patch.dict("os.environ", {"BOT_TOKEN": "fake"})
    mocker.patch("src.db.database.connect_to_db", side_effect=DatabaseConnectionError)
    mocker.patch("src.main.run_bot", new_callable=AsyncMock)
    await main()


@pytest.mark.asyncio
async def test_main_run_bot(mocker: MockerFixture) -> None:
    """
    Check catch run_bot error
    """
    mocker.patch.dict("os.environ", {"BOT_TOKEN": "fake"})
    mocker.patch("src.db.database.connect_to_db")
    mocker.patch("src.main.run_bot", side_effect=KeyboardInterrupt)
    await main()


@pytest.mark.asyncio
async def test_loggers(mocker: MockerFixture) -> None:
    """
    Check logger works
    """
    mocker.patch.dict("os.environ", {"BOT_TOKEN": "fake"})
    mocker.patch("src.db.database.connect_to_db")
    mocker.patch("src.main.run_bot", new_callable=AsyncMock)
    mock_logger = mocker.patch("src.main.logger")
    await main()
    mock_logger.info.assert_any_call("Launching a marketplace parser bot...")
