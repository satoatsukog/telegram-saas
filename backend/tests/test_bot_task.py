import asyncio
import os

from app.main import bot_task_done


async def test_exception_terminates(monkeypatch):
    codes = []
    monkeypatch.setattr(os, "_exit", codes.append)

    async def boom():
        raise RuntimeError("down")

    task = asyncio.create_task(boom())
    try:
        await task
    except RuntimeError:
        pass
    bot_task_done(task)
    assert codes == [1]


async def test_cancellation_does_not_terminate(monkeypatch):
    codes = []
    monkeypatch.setattr(os, "_exit", codes.append)

    async def hang():
        await asyncio.sleep(10)

    task = asyncio.create_task(hang())
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    bot_task_done(task)
    assert codes == []


async def test_clean_exit_does_not_terminate(monkeypatch):
    codes = []
    monkeypatch.setattr(os, "_exit", codes.append)

    async def done():
        return None

    task = asyncio.create_task(done())
    await task
    bot_task_done(task)
    assert codes == []
