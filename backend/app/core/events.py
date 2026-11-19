from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event


async def log_event(
    session: AsyncSession,
    user_id: int,
    event: str,
    source: str | None = None,
    plan: str | None = None,
) -> None:
    session.add(Event(user_id=user_id, event=event, source=source, plan=plan))
