from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import PRICE_MONTHLY, PRICE_YEARLY
from app.core.premium import PLAN_DAYS, extend, shorten
from app.core.timeutil import utcnow
from app.db.models import Payment, User

PRICES = {"monthly": PRICE_MONTHLY, "yearly": PRICE_YEARLY}


def valid_payment(currency: str, payload: str, total_amount: int) -> bool:
    return currency == "XTR" and payload in PRICES and total_amount == PRICES[payload]


async def apply_payment(session: AsyncSession, user: User, charge_id: str, plan: str, stars: int) -> bool:
    exists = await session.scalar(
        select(Payment.id).where(Payment.telegram_payment_charge_id == charge_id)
    )
    if exists is not None:
        return False
    session.add(Payment(user_id=user.id, telegram_payment_charge_id=charge_id, plan=plan, stars=stars))
    user.premium_until = extend(user.premium_until, utcnow(), PLAN_DAYS.get(plan, 30))
    return True


async def process_refund(session: AsyncSession, bot: Any, charge_id: str) -> tuple[str, int | None]:
    payment = await session.scalar(
        select(Payment).where(Payment.telegram_payment_charge_id == charge_id)
    )
    if payment is None:
        return "not_found", None
    if payment.refunded:
        return "already_refunded", payment.user_id
    await bot.refund_star_payment(payment.user_id, charge_id)
    if payment.plan == "monthly":
        await bot.edit_user_star_subscription(payment.user_id, charge_id, is_canceled=True)
    payment.refunded = True
    user = await session.get(User, payment.user_id)
    if user is not None:
        user.premium_until = shorten(user.premium_until, utcnow(), PLAN_DAYS.get(payment.plan, 30))
    return "ok", payment.user_id
