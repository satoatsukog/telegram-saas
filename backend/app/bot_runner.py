import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.handlers import router
from app.bot.payments import router as payments_router
from app.config import BOT_TOKEN, WEBAPP_URL
from app.db.session import apply_migrations
from app.scheduler.reminders import run_due_reminders

COMMANDS = [
    BotCommand(command="start", description="Open the app"),
    BotCommand(command="help", description="How it works"),
    BotCommand(command="paysupport", description="Payment support"),
]


async def _configure(bot: Bot) -> None:
    await bot.set_my_commands(COMMANDS)
    if WEBAPP_URL.startswith("https://"):
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open", web_app=WebAppInfo(url=WEBAPP_URL))
        )


async def run_bot() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set; copy .env.example to .env and fill it")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(payments_router)
    await _configure(bot)
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_due_reminders, "cron", minute=0, args=[bot])
    scheduler.start()
    await dp.start_polling(bot)


async def main() -> None:
    await apply_migrations()
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
