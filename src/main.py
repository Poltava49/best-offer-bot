import os
import asyncio
import sys
from src.db.database import connect_to_db
from src.app.telegram_bot import run_bot
from dotenv import load_dotenv
from typing import cast

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not isinstance(BOT_TOKEN, str):
    print("BOT_TOKEN не найден в .env файле")
    sys.exit(1)


async def main() -> None:
    """Async main func"""
    print("Запуск бота-парсера маркетплейсов...")
    try:
        connect_to_db()
        print("Подключение к PostgreSQL успешно!")

    except Exception as e:
        print(f"Ошибка подключения к базе - {e}")

    # Запуск бота
    try:
        await run_bot(cast(str, BOT_TOKEN))
    except KeyboardInterrupt:
        print("Остановка бота...")
    except Exception as e:
        print(f"Ошибка в боте: {e}")


if __name__ == "__main__":
    asyncio.run(main())
