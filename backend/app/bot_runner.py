import asyncio

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.handlers import router
from app.config import BOT_TOKEN
from app.db.session import init_db
from app.scheduler.reminders import run_due_reminders


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set; copy .env.example to .env and fill it")
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_due_reminders, "cron", minute=0, args=[bot])
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
