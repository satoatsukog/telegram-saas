import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.bot_runner import configure_logging, run_bot
from app.config import RUN_BOT
from app.db.session import apply_migrations

logger = logging.getLogger(__name__)
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def bot_task_done(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is None:
        return
    logger.critical("bot task crashed, terminating", exc_info=exc)
    os._exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await apply_migrations()
    task = asyncio.create_task(run_bot()) if RUN_BOT else None
    if task:
        task.add_done_callback(bot_task_done)
    yield
    if task:
        task.remove_done_callback(bot_task_done)
        task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="app")
