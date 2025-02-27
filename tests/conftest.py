import asyncio

import pytest
from contextlib import asynccontextmanager

from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from src.main import app


@asynccontextmanager
async def client_manager(fastapi_app):
    fastapi_app.state.testing = True
    async with LifespanManager(fastapi_app):
        transport = ASGITransport(fastapi_app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as c:
            yield c


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client(event_loop):
    async with client_manager(app) as c:
        yield c
