from __future__ import annotations
from __future__ import annotations

from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import api
from db.session import engine

import asyncio
from typing import Iterator
@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport: ASGITransport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def _dispose_engine_after_test() -> AsyncIterator[None]:
    yield
    await engine.dispose()

@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    yield loop
    loop.close()