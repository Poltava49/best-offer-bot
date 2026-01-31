try:
    from db.database import connect_to_db
    from app.telegram_bot import run_bot
except ImportError as e:
    print(f" Ошибка импорта: {e}")


BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("BOT_TOKEN не найден в .env файле")




async def main():
    """Асинхронная основная функция"""
    print("Запуск бота-парсера маркетплейсов...")
    try:
        conn = connect_to_db()
        print("Подключение к PostgreSQL успешно!")

    except Exception as e:
        print(f"Ошибка подключения к базе - {e}")

    #Запуск бота
    try:
        await run_bot(BOT_TOKEN)
    except KeyboardInterrupt:
        print("Остановка бота...")
    except Exception as e:
        print(f"Ошибка в боте: {e}")


def main():
    """Точка входа"""
    asyncio.run(main_async())




if __name__ == "__main__":
    main()

