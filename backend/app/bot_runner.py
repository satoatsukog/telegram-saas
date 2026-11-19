import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.config import BOT_TOKEN
from app.db.session import init_db


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set; copy .env.example to .env and fill it")
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
