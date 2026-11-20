from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, PreCheckoutQuery

from app.config import ADMIN_ID
from app.core.events import log_event
from app.core.payments import apply_payment, process_refund, valid_payment
from app.db.models import User
from app.db.session import async_session

router = Router()

REFUND_MESSAGES = {
    "not_found": "No payment found for that charge id.",
    "already_refunded": "That payment was already refunded.",
}


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    if valid_payment(query.currency, query.invoice_payload, query.total_amount):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Payment could not be validated. Please try again.")


@router.message(F.successful_payment)
async def on_paid(message: Message) -> None:
    sp = message.successful_payment
    uid = message.from_user.id
    if not valid_payment(sp.currency, sp.invoice_payload, sp.total_amount):
        async with async_session() as session:
            await log_event(session, uid, "pay_invalid", plan=sp.invoice_payload)
            await session.commit()
        return
    async with async_session() as session:
        user = await session.get(User, uid)
        if user is None:
            user = User(id=uid)
            session.add(user)
        created = await apply_payment(session, user, sp.telegram_payment_charge_id, sp.invoice_payload, sp.total_amount)
        if created:
            await log_event(session, uid, "pay", plan=sp.invoice_payload)
        await session.commit()
    if created:
        await message.answer("✅ Premium is active — unlimited decks and cards. Thank you!")


@router.message(Command("refund"))
async def refund(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    charge_id = (command.args or "").strip()
    if not charge_id:
        await message.answer("Usage: /refund <charge_id>")
        return
    async with async_session() as session:
        try:
            status, uid = await process_refund(session, bot, charge_id)
        except Exception as error:
            await message.answer(f"Refund failed: {error}")
            return
        await session.commit()
    await message.answer(REFUND_MESSAGES.get(status, f"Refunded {charge_id}; premium adjusted for user {uid}."))
