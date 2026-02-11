import pytest
from src.main import main

@pytest.mark.asyncio
async def test_main_example():
    result = await main()
    assert result is None
