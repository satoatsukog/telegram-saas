from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, get_user_id
from app.api.schemas import CardIn, DeckIn, GradeIn, PasteIn, SettingsIn, TextIn
from app.core.events import log_event
from app.core.list_parser import parse_list
from app.core.sm2 import SchedulingState, schedule
from app.core.streak import effective_streak
from app.core.timeutil import to_local, utcnow
from app.db.models import Card, Deck, Event, User

router = APIRouter(prefix="/api")


def _cap(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(f[:512], b[:512]) for f, b in pairs]


def _parse_csv(text: str) -> list[tuple[str, str]]:
    out = []
    for line in text.splitlines():
        if "," not in line:
            continue
        front, back = line.split(",", 1)
        front, back = front.strip(), back.strip()
        if front and back:
            out.append((front, back))
    return out


async def _emit_once(session: AsyncSession, uid: int, event: str, source: str | None = None) -> None:
    stmt = select(Event.id).where(Event.user_id == uid, Event.event == event)
    if source is not None:
        stmt = stmt.where(Event.source == source)
    if await session.scalar(stmt.limit(1)) is None:
        await log_event(session, uid, event, source=source)


async def _owned_deck(session: AsyncSession, uid: int, deck_id: int) -> Deck:
    deck = await session.get(Deck, deck_id)
    if deck is None or deck.user_id != uid:
        raise HTTPException(status_code=404, detail="deck not found")
    return deck


async def _due_count(session: AsyncSession, uid: int) -> int:
    now = utcnow()
    return await session.scalar(
        select(func.count())
        .select_from(Card)
        .join(Deck)
        .where(Deck.user_id == uid, Card.due_at <= now)
    ) or 0


async def _streak(session: AsyncSession, user: User) -> int:
    eff = effective_streak(user.streak, user.last_review_on, user.tz)
    if eff != user.streak:
        user.streak = eff
        await session.commit()
    return eff


@router.post("/settings")
async def save_settings(body: SettingsIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    user = await session.get(User, uid)
    user.tz = body.tz
    if body.reminder_hour is not None:
        user.reminder_hour = body.reminder_hour
    await session.commit()
    return {"ok": True}


@router.get("/home")
async def home(uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    now = utcnow()
    user = await session.get(User, uid)
    decks = (await session.execute(select(Deck).where(Deck.user_id == uid).order_by(Deck.id))).scalars().all()
    out = []
    total = 0
    due_total = 0
    for d in decks:
        cards = (await session.execute(select(Card).where(Card.deck_id == d.id))).scalars().all()
        due = sum(1 for c in cards if c.due_at <= now)
        total += len(cards)
        due_total += due
        out.append({"id": d.id, "name": d.name, "due": due, "total": len(cards)})
    return {"streak": await _streak(session, user), "dueToday": due_total, "totalCards": total, "decks": out}


@router.get("/stats")
async def stats(uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    user = await session.get(User, uid)
    week_ago = utcnow() - timedelta(days=7)
    reviews = await session.scalar(
        select(func.count()).select_from(Event).where(Event.user_id == uid, Event.event == "review", Event.ts >= week_ago)
    ) or 0
    total = await session.scalar(select(func.count()).select_from(Card).join(Deck).where(Deck.user_id == uid)) or 0
    return {"streak": await _streak(session, user), "dueToday": await _due_count(session, uid), "totalCards": total, "reviewsThisWeek": reviews}


@router.post("/decks")
async def create_deck(body: DeckIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = Deck(user_id=uid, name=body.name)
    session.add(deck)
    await session.commit()
    return {"id": deck.id, "name": deck.name}


@router.patch("/decks/{deck_id}")
async def rename_deck(deck_id: int, body: DeckIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    deck.name = body.name
    await session.commit()
    return {"ok": True}


@router.delete("/decks/{deck_id}", status_code=204)
async def delete_deck(deck_id: int, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    await session.execute(delete(Card).where(Card.deck_id == deck.id))
    await session.delete(deck)
    await session.commit()


@router.get("/decks/{deck_id}")
async def get_deck(deck_id: int, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    cards = (await session.execute(select(Card).where(Card.deck_id == deck.id).order_by(Card.id))).scalars().all()
    return {"id": deck.id, "name": deck.name, "cards": [{"id": c.id, "front": c.front, "back": c.back} for c in cards]}


@router.post("/paste")
async def paste_new(body: PasteIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    pairs = _cap(parse_list(body.text))
    if not pairs:
        raise HTTPException(status_code=400, detail="no valid pairs found")
    deck = Deck(user_id=uid, name=body.name)
    session.add(deck)
    await session.flush()
    now = utcnow()
    session.add_all([Card(deck_id=deck.id, front=f, back=b, due_at=now) for f, b in pairs])
    await _emit_once(session, uid, "onboarding_done")
    await session.commit()
    return {"deckId": deck.id, "added": len(pairs)}


@router.post("/decks/{deck_id}/cards")
async def add_card(deck_id: int, body: CardIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    card = Card(deck_id=deck.id, front=body.front, back=body.back, due_at=utcnow())
    session.add(card)
    await _emit_once(session, uid, "onboarding_done")
    await session.commit()
    return {"id": card.id}


@router.post("/decks/{deck_id}/paste")
async def paste_into(deck_id: int, body: TextIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    pairs = _cap(parse_list(body.text))
    if not pairs:
        raise HTTPException(status_code=400, detail="no valid pairs found")
    now = utcnow()
    session.add_all([Card(deck_id=deck.id, front=f, back=b, due_at=now) for f, b in pairs])
    await _emit_once(session, uid, "onboarding_done")
    await session.commit()
    return {"added": len(pairs)}


@router.post("/decks/{deck_id}/csv")
async def import_csv(deck_id: int, body: TextIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    deck = await _owned_deck(session, uid, deck_id)
    pairs = _cap(_parse_csv(body.text))
    if not pairs:
        raise HTTPException(status_code=400, detail="no valid pairs found")
    now = utcnow()
    session.add_all([Card(deck_id=deck.id, front=f, back=b, due_at=now) for f, b in pairs])
    await _emit_once(session, uid, "onboarding_done")
    await session.commit()
    return {"added": len(pairs)}


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(card_id: int, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="card not found")
    await _owned_deck(session, uid, card.deck_id)
    await session.delete(card)
    await session.commit()


@router.get("/review/next")
async def review_next(uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    now = utcnow()
    card = await session.scalar(
        select(Card).join(Deck).where(Deck.user_id == uid, Card.due_at <= now).order_by(Card.due_at).limit(1)
    )
    payload = {"id": card.id, "front": card.front, "back": card.back} if card else None
    return {"card": payload, "due": await _due_count(session, uid)}


@router.post("/review/grade")
async def review_grade(body: GradeIn, uid: int = Depends(get_user_id), session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, body.card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="card not found")
    user = await session.get(User, uid)
    await _owned_deck(session, uid, card.deck_id)
    state = schedule(SchedulingState(card.ease, card.interval, card.repetitions), body.grade)
    card.ease, card.interval, card.repetitions = state.ease, state.interval, state.repetitions
    card.due_at = utcnow() + timedelta(days=state.interval)

    today = to_local(utcnow(), user.tz).date()
    if user.last_review_on == today:
        pass
    elif user.last_review_on == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1
    user.last_review_on = today

    await _emit_once(session, uid, "first_review_done")
    await log_event(session, uid, "review")
    first = await session.scalar(
        select(Event.ts).where(Event.user_id == uid, Event.event == "first_review_done").limit(1)
    )
    if first is not None:
        delta = (today - to_local(first, user.tz).date()).days
        if delta in (1, 7):
            await _emit_once(session, uid, "review_day", source=f"d{delta}")
    await session.commit()
    return {"streak": user.streak, "due": await _due_count(session, uid)}
