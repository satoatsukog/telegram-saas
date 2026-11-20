from collections.abc import AsyncIterator
from datetime import timezone

from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AUTH_MAX_AGE_SECONDS, BOT_TOKEN
from app.core.timeutil import utcnow
from app.db.models import User
from app.db.session import async_session


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def get_user_id(authorization: str = Header(default="")) -> int:
    raw = authorization.removeprefix("tma ").strip()
    if not raw:
        raise HTTPException(status_code=401, detail="missing init data")
    try:
        data = safe_parse_webapp_init_data(BOT_TOKEN, raw)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid init data")
    if data.user is None:
        raise HTTPException(status_code=401, detail="no user in init data")
    auth_date = data.auth_date
    if auth_date.tzinfo is not None:
        auth_date = auth_date.astimezone(timezone.utc).replace(tzinfo=None)
    if (utcnow() - auth_date).total_seconds() > AUTH_MAX_AGE_SECONDS:
        raise HTTPException(status_code=401, detail="init data expired")
    uid = data.user.id
    async with async_session() as session:
        if await session.get(User, uid) is None:
            session.add(User(id=uid))
            await session.commit()
    return uid
