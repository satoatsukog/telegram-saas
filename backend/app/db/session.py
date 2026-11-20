from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

_BACKEND = Path(__file__).resolve().parents[2]


def _upgrade(connection: Connection) -> None:
    cfg = Config(str(_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def apply_migrations() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(_upgrade)
