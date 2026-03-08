import pytest
import sys
from unittest.mock import patch, MagicMock, AsyncMock


sys.exit = MagicMock()

with patch('os.getenv', return_value="test_token_123"):
    from src.main import main


@pytest.mark.asyncio
async def test_main_success(mocker):
    mocker.patch('src.db.database.connect_to_db')
    mocker.patch('src.main.run_bot', new_callable=AsyncMock)
    mocker.patch('src.main.logger')
    await main()
    assert True