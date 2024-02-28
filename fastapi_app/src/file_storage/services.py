import logging
from typing import Dict

from fastapi import UploadFile

from fastapi_app.src.file_storage.abstract_repositories import AbstractFileRepository
from fastapi_app.src.file_storage.exceptions import (
    FileAlreadyExistsError,
    FileDeletionError,
    FileReadError,
    FileStorageError,
    FileWriteError,
)
from fastapi_app.src.schemas import FileMetadata

logger = logging.getLogger("app.file_storage.file_storage_service")


class FileStorageService:
    def __init__(self, file_repository: AbstractFileRepository):
        self._file_repository = file_repository

    def get_file(self, domain_obj: FileMetadata) -> Dict:
        try:
            return self._file_repository.read_file(domain_obj=domain_obj)
        except (FileNotFoundError, FileReadError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"reading the file payload "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise FileStorageError(error_message)

    async def save_file(self, file: UploadFile, domain_obj: FileMetadata) -> None:
        try:
            await self._file_repository.write_file(file=file, domain_obj=domain_obj)
        except (FileAlreadyExistsError, FileWriteError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"saving the file to storage "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise FileStorageError(error_message)

    async def update_file(
        self,
        file: UploadFile,
        domain_obj_new: FileMetadata,
        domain_obj_old: FileMetadata,
    ) -> None:
        try:
            self._file_repository.delete_file(domain_obj=domain_obj_old)
            await self._file_repository.write_file(file=file, domain_obj=domain_obj_new)
        except (
            FileAlreadyExistsError,
            FileWriteError,
            FileDeletionError,
        ) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"updating the file in storage "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise FileStorageError(error_message)

    def remove_file(self, domain_obj: FileMetadata) -> None:
        try:
            self._file_repository.delete_file(domain_obj=domain_obj)
        except FileDeletionError as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"deleting the file from storage "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise FileStorageError(error_message)
