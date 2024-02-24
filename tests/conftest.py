import asyncio
import os
import shutil
from typing import AsyncGenerator, Dict

import pytest
from dependency_injector import containers, providers
from httpx import AsyncClient

from fastapi_app.src.config import DatabaseSettings
from fastapi_app.src.file_storage.repositories import DiskRepository
from fastapi_app.src.main import app
from fastapi_app.src.schemas import FileMetadata


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=False)
def test_storage_dir():
    temp_dir = os.path.join(os.path.dirname(__file__), "storage_test")

    yield temp_dir

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def container(test_storage_dir):
    container = app.container

    test_disk_repository_provider = providers.Factory(
        DiskRepository, storage_dir=test_storage_dir
    )

    container.repositories.disk_repository_provider.override(
        test_disk_repository_provider
    )
    return container


@pytest.fixture(scope="session")
def database_test(container):
    return container.database.database_provider()


@pytest.fixture(scope="session", autouse=False)
def disk_repository_test(container):
    return container.repositories.disk_repository_provider()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(database_test):
    assert DatabaseSettings().mode == "TEST"

    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=False)
def example_domains_entities(container: containers.DeclarativeContainer) -> Dict:
    mapper = container.mappers.file_metadata_mapper_provider()

    payloads = [
        {
            "id": 1,
            "name": "file1.txt",
            "tag": None,
            "size": 1024,
            "mimeType": "text/plain",
        },
        {
            "id": 2,
            "name": "file2.docx",
            "tag": "important",
            "size": 1024,
            "mimeType": "application/msword",
        },
        {
            "id": 3,
            "name": "3",
            "tag": "important",
            "size": 2048,
            "mimeType": "image/jpeg",
        },
        {
            "id": 4,
            "name": "file4.pdf",
            "tag": "presentations",
            "size": 1024,
            "mimeType": "image/jpeg",
        },
    ]

    d = {
        "domains": [FileMetadata(**payload) for payload in payloads],
        "entities": [mapper.to_entity(FileMetadata(**payload)) for payload in payloads],
    }

    return d


@pytest.fixture(scope="function", autouse=False)
async def database_with_data(database_test, example_domains_entities):
    example_entities = example_domains_entities["entities"]

    await database_test.delete_and_create_database()

    async with database_test.get_session_factory() as session:
        session.add_all(example_entities)
        await session.commit()


@pytest.fixture(scope="function", autouse=False)
async def empty_database(database_test):
    await database_test.delete_and_create_database()
