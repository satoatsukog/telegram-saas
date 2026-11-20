from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import BigInteger, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    tz: Mapped[str] = mapped_column(String(64), default="UTC")
    reminder_hour: Mapped[int] = mapped_column(default=19)
    last_reminded_on: Mapped[date | None] = mapped_column(default=None)
    last_review_on: Mapped[date | None] = mapped_column(default=None)
    streak: Mapped[int] = mapped_column(default=0)
    premium_until: Mapped[datetime | None] = mapped_column(default=None)
    source: Mapped[str] = mapped_column(String(64), default="direct")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    decks: Mapped[list[Deck]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship(back_populates="decks")
    cards: Mapped[list[Card]] = relationship(
        back_populates="deck", cascade="all, delete-orphan"
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"))
    front: Mapped[str] = mapped_column(String(512))
    back: Mapped[str] = mapped_column(String(512))
    ease: Mapped[float] = mapped_column(default=2.5)
    interval: Mapped[int] = mapped_column(default=0)
    repetitions: Mapped[int] = mapped_column(default=0)
    due_at: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    deck: Mapped[Deck] = relationship(back_populates="cards")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    event: Mapped[str] = mapped_column(String(32))
    source: Mapped[str | None] = mapped_column(String(64), default=None)
    plan: Mapped[str | None] = mapped_column(String(16), default=None)
    ts: Mapped[datetime] = mapped_column(server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    telegram_payment_charge_id: Mapped[str] = mapped_column(String(128), unique=True)
    plan: Mapped[str] = mapped_column(String(16))
    stars: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
