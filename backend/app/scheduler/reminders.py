from aiogram import Bot
from sqlalchemy import func, select

from app.bot.keyboards import open_app_kb
from app.config import WEBAPP_URL
from app.core.streak import effective_streak
from app.core.timeutil import to_local, utcnow
from app.db.models import Card, Deck, User
from app.db.session import async_session


async def run_due_reminders(bot: Bot) -> None:
    now = utcnow()
    markup = open_app_kb(WEBAPP_URL, "Review now") if WEBAPP_URL.startswith("https://") else None
    async with async_session() as session:
        users = (await session.execute(select(User))).scalars().all()
        for user in users:
            local = to_local(now, user.tz)
            if local.hour != user.reminder_hour or user.last_reminded_on == local.date():
                continue
            due = await session.scalar(
                select(func.count())
                .select_from(Card)
                .join(Deck)
                .where(Deck.user_id == user.id, Card.due_at <= now)
            )
            if not due:
                continue
            streak = effective_streak(user.streak, user.last_review_on, user.tz)
            if streak != user.streak:
                user.streak = streak
            try:
                await bot.send_message(
                    user.id,
                    f"{due} cards due 🔥 streak {streak} — review now",
                    reply_markup=markup,
                )
            except Exception:
                pass
            user.last_reminded_on = local.date()
        await session.commit()
