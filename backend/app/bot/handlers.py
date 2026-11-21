from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.bot.keyboards import open_app_kb
from app.config import ADMIN_ID, SUPPORT_EMAIL, WEBAPP_URL
from app.core.deep_link import parse_source
from app.core.events import log_event
from app.core.stats import compute_funnel, format_funnel
from app.core.timeutil import utcnow
from app.db.models import Event, User
from app.db.session import async_session

router = Router()

GREETING = "Welcome to RecallDeck — learn any words or terms, one quick review a day."

HELP = (
    "RecallDeck helps you memorize any words or terms with spaced repetition.\n"
    "Paste a list (one per line: word - meaning), then review a little each day; "
    "cards you find hard come back sooner.\n"
    "Open the app from the menu button or /start. Payment questions: /paysupport."
)


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


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(HELP)


@router.message(Command("paysupport"))
async def paysupport(message: Message) -> None:
    await message.answer(
        f"For payment issues email {SUPPORT_EMAIL}, include your Telegram ID: {message.from_user.id}"
    )


@router.message(Command("stats"))
async def stats_command(message: Message) -> None:
    if not ADMIN_ID or message.from_user.id != ADMIN_ID:
        return
    async with async_session() as session:
        events = (await session.execute(select(Event.user_id, Event.event, Event.source, Event.ts))).all()
        users = (await session.execute(select(User.id, User.source))).all()
    user_source = {uid: src for uid, src in users}
    result = compute_funnel([tuple(e) for e in events], user_source, utcnow())
    await message.answer(format_funnel(result))
