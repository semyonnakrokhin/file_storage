from contextlib import nullcontext as does_not_raise
from datetime import datetime
from unittest import mock

import pytest

from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    MappingError,
    SessionNotSetError,
)
from fastapi_app.src.db_service.repositories import FileMetadataRepository
from fastapi_app.src.schemas import FileMetadata


class TestDatabaseServiceAdd:
    @pytest.mark.parametrize(
        argnames="data, expected_output, expectation",
        argvalues=[
            (
                FileMetadata(
                    **{
                        "id": 1,
                        "name": "example.txt",
                        "tag": "example",
                        "size": 1024,
                        "mimeType": "text/plain",
                        "modificationTime": None,
                    }
                ),
                FileMetadata(
                    **{
                        "id": 1,
                        "name": "example.txt",
                        "tag": "example",
                        "size": 1024,
                        "mimeType": "text/plain",
                        "modificationTime": datetime.utcnow(),
                    }
                ),
                does_not_raise(),
            ),
        ],
    )
    async def test_add_file_metadata_success(
        self, container, data, expected_output, expectation
    ):
        repository_mock = mock.Mock(spec=FileMetadataRepository)
        repository_mock.insert_one.return_value = expected_output

        with expectation:
            with container.repositories.file_metadata_repository_provider.override(
                repository_mock
            ):
                service = container.services.database_service_provider()
                result = await service.add_file_metadata(metadata=data)

            assert result == expected_output

    @pytest.mark.parametrize(
        argnames="error_type",
        argvalues=[
            SessionNotSetError,
            MappingError,
            DatabaseError,
            AttributeError,
        ],
    )
    async def test_add_file_raising_errors(self, container, error_type):
        repository_mock = mock.Mock(spec=FileMetadataRepository)
        repository_mock.insert_one.side_effect = error_type("Mocked error")
        data = FileMetadata(
            **{
                "id": 1,
                "name": "example.txt",
                "tag": "example",
                "size": 1024,
                "mimeType": "text/plain",
                "modificationTime": None,
            }
        )

        with container.repositories.file_metadata_repository_provider.override(
            repository_mock
        ):
            service = container.services.database_service_provider()

            with pytest.raises(error_type):
                await service.add_file_metadata(metadata=data)
