import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from fastapi_app.src.config import DatabaseSettings
from fastapi_app.src.main import app


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def container():
    container = app.container
    return container


@pytest.fixture(scope="session")
def database_test(container):
    return container.database.database_provider()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(database_test):
    assert DatabaseSettings().mode == "TEST"

    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
