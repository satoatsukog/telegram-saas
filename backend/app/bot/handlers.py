from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.bot.keyboards import open_app_kb
from app.config import SUPPORT_EMAIL, WEBAPP_URL
from app.core.deep_link import parse_source
from app.core.events import log_event
from app.db.models import User
from app.db.session import async_session

router = Router()

GREETING = "Welcome to RecallDeck — drill your vocabulary in one tap a day."


@router.message(CommandStart())
async def start(message: Message, command: CommandObject) -> None:
    source = parse_source(command.args)
    user_id = message.from_user.id
    async with async_session() as session:
        if await session.get(User, user_id) is None:
            session.add(User(id=user_id, source=source))
        await log_event(session, user_id, "start", source=source)
        await session.commit()
    if WEBAPP_URL.startswith("https://"):
        await message.answer(GREETING, reply_markup=open_app_kb(WEBAPP_URL))
    else:
        await message.answer(f"{GREETING}\nThe Mini App opens here once it's deployed.")


@router.message(Command("paysupport"))
async def paysupport(message: Message) -> None:
    await message.answer(
        f"For payment issues email {SUPPORT_EMAIL}, include your Telegram ID: {message.from_user.id}"
    )
