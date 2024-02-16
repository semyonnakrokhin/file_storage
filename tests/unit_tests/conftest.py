from typing import Dict

import pytest
from dependency_injector import containers

from fastapi_app.src.schemas import FileMetadataDto


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
        "domains": [FileMetadataDto(**payload) for payload in payloads],
        "entities": [
            mapper.to_entity(FileMetadataDto(**payload)) for payload in payloads
        ],
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
