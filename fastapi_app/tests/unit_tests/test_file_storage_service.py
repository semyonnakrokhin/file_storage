import io
from contextlib import nullcontext as does_not_raise
from unittest import mock

import pytest
from fastapi import UploadFile

from fastapi_app.src.file_storage.exceptions import (
    FileAlreadyExistsError,
    FileWriteError,
)
from fastapi_app.src.file_storage.repositories import DiskRepository
from fastapi_app.src.schemas import FileMetadata


class TestFileStorageServiceSave:
    @pytest.mark.parametrize(
        argnames="file, metadata, expectation",
        argvalues=[
            (
                UploadFile(filename="example.txt", file=io.BytesIO(b"Hello World!")),
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
                does_not_raise(),
            ),
        ],
    )
    async def test_save_file_success(self, container, file, metadata, expectation):
        repository_mock = mock.Mock(spec=DiskRepository)

        with expectation:
            with container.repositories.disk_repository_provider.override(
                repository_mock
            ):
                service = container.services.file_storage_service_provider()
                await service.save_file(file=file, domain_obj=metadata)

    @pytest.mark.parametrize(
        argnames="error_type",
        argvalues=[ValueError, FileAlreadyExistsError, FileWriteError],
    )
    async def test_add_file_raising_errors(self, container, error_type):
        repository_mock = mock.Mock(spec=DiskRepository)
        repository_mock.write_file.side_effect = error_type("Mocked error")
        metadata = FileMetadata(
            **{
                "id": 1,
                "name": "example.txt",
                "tag": "example",
                "size": 1024,
                "mimeType": "text/plain",
                "modificationTime": None,
            }
        )
        file = UploadFile(filename="example.txt", file=io.BytesIO(b"Hello World!"))

        with container.repositories.disk_repository_provider.override(repository_mock):
            service = container.services.file_storage_service_provider()

            with pytest.raises(error_type):
                await service.save_file(file=file, domain_obj=metadata)
