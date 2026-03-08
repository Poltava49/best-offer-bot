import os
import asyncio
import sys
from src.db.database import connect_to_db
from src.app.telegram_bot import run_bot
from typing import cast
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not isinstance(BOT_TOKEN, str):
    logger.info("BOT_TOKEN not found in .env file")
    sys.exit(1)


async def main() -> None:
    """Async main func"""
    logger.info("Launching a marketplace parser bot...")
    try:
        connect_to_db()
        logger.info("Connection to PostgreSQL successful!")

    except Exception as e:
        logger.info(f"Error connecting to database - {e}")

    # Start bot
    try:
        await run_bot(cast(str, BOT_TOKEN))
    except KeyboardInterrupt:
        logger.info("Stopping the bot...")
    except Exception as e:
        logger.info(f"Error in bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())