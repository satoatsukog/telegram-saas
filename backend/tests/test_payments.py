from datetime import timedelta

import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.limits import cards_allowed, deck_allowed
from app.core.payments import PRICES, admin_payment_note, apply_payment, process_refund, valid_payment
from app.core.premium import extend, is_premium, shorten
from app.core.timeutil import utcnow
from app.db.models import Base, Payment, User


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


class FakeBot:
    def __init__(self):
        self.refunds = []
        self.cancels = []
        self.order = []

    async def refund_star_payment(self, user_id, charge_id):
        self.order.append("refund")
        self.refunds.append((user_id, charge_id))
        return True

    async def edit_user_star_subscription(self, user_id, charge_id, is_canceled):
        self.order.append("cancel")
        self.cancels.append((user_id, charge_id, is_canceled))
        return True


async def _user(session, uid):
    u = User(id=uid)
    session.add(u)
    await session.commit()
    return u


async def test_duplicate_payment_is_no_op(session):
    user = await _user(session, 1)
    assert await apply_payment(session, user, "ch1", "yearly", 1499) is True
    first = user.premium_until
    assert await apply_payment(session, user, "ch1", "yearly", 1499) is False
    assert user.premium_until == first
    count = await session.scalar(
        select(func.count()).select_from(Payment).where(Payment.telegram_payment_charge_id == "ch1")
    )
    assert count == 1


async def test_yearly_extends_from_future_premium(session):
    user = await _user(session, 2)
    future = utcnow() + timedelta(days=100)
    user.premium_until = future
    await apply_payment(session, user, "ch2", "yearly", 1499)
    assert user.premium_until == future + timedelta(days=365)


async def test_refund_monthly_cancels_subscription(session):
    user = await _user(session, 3)
    await apply_payment(session, user, "chm", "monthly", 199)
    await session.commit()
    bot = FakeBot()
    status, uid = await process_refund(session, bot, "chm")
    await session.commit()
    assert status == "ok" and uid == 3
    assert bot.refunds == [(3, "chm")]
    assert bot.cancels == [(3, "chm", True)]
    payment = await session.scalar(select(Payment).where(Payment.telegram_payment_charge_id == "chm"))
    assert payment.refunded is True


async def test_refund_yearly_does_not_cancel(session):
    user = await _user(session, 4)
    await apply_payment(session, user, "chy", "yearly", 1499)
    await session.commit()
    bot = FakeBot()
    status, _ = await process_refund(session, bot, "chy")
    await session.commit()
    assert status == "ok"
    assert bot.cancels == []


async def test_double_refund_is_no_op(session):
    user = await _user(session, 5)
    await apply_payment(session, user, "chd", "monthly", 199)
    await session.commit()
    bot = FakeBot()
    await process_refund(session, bot, "chd")
    await session.commit()
    after_first = user.premium_until
    status, _ = await process_refund(session, bot, "chd")
    await session.commit()
    assert status == "already_refunded"
    assert len(bot.refunds) == 1
    assert user.premium_until == after_first


async def test_yearly_kept_after_refunding_monthly(session):
    user = await _user(session, 6)
    await apply_payment(session, user, "y1", "yearly", 1499)
    await apply_payment(session, user, "m1", "monthly", 199)
    await session.commit()
    before = user.premium_until
    bot = FakeBot()
    await process_refund(session, bot, "m1")
    await session.commit()
    assert user.premium_until == before - timedelta(days=30)
    assert is_premium(user.premium_until, utcnow()) is True
    ypay = await session.scalar(select(Payment).where(Payment.telegram_payment_charge_id == "y1"))
    assert ypay.refunded is False


async def test_refund_cancels_before_refund(session):
    user = await _user(session, 7)
    await apply_payment(session, user, "cho", "monthly", 199)
    await session.commit()
    bot = FakeBot()
    await process_refund(session, bot, "cho")
    await session.commit()
    assert bot.order == ["cancel", "refund"]


def test_admin_payment_note_format():
    note = admin_payment_note("monthly", 42, 199, "ch_x")
    assert "monthly" in note and "42" in note and "199" in note and "/refund ch_x" in note


def test_shorten_floors_at_now():
    now = utcnow()
    assert shorten(now + timedelta(days=10), now, 30) == now
    assert shorten(None, now, 30) is None
    future = now + timedelta(days=100)
    assert shorten(future, now, 30) == future - timedelta(days=30)


def test_valid_payment_checks():
    assert valid_payment("XTR", "monthly", PRICES["monthly"]) is True
    assert valid_payment("XTR", "yearly", PRICES["yearly"]) is True
    assert valid_payment("XTR", "monthly", PRICES["monthly"] + 1) is False
    assert valid_payment("USD", "monthly", PRICES["monthly"]) is False
    assert valid_payment("XTR", "weekly", PRICES["monthly"]) is False


def test_extend_from_max_now_or_until():
    now = utcnow()
    assert extend(None, now, 365) == now + timedelta(days=365)
    assert extend(now - timedelta(days=5), now, 365) == now + timedelta(days=365)
    future = now + timedelta(days=10)
    assert extend(future, now, 30) == future + timedelta(days=30)


def test_is_premium():
    now = utcnow()
    assert is_premium(now + timedelta(days=1), now) is True
    assert is_premium(now - timedelta(days=1), now) is False
    assert is_premium(None, now) is False


def test_caps_enforced():
    assert deck_allowed(False, 1) is True
    assert deck_allowed(False, 2) is False
    assert deck_allowed(True, 99) is True
    assert cards_allowed(False, 59, 1) is True
    assert cards_allowed(False, 60, 1) is False
    assert cards_allowed(False, 0, 61) is False
    assert cards_allowed(True, 10000, 10000) is True
