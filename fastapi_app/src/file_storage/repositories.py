import logging
import os
from typing import Dict, Optional

import aiofiles
from fastapi import UploadFile

from fastapi_app.src.file_storage.abstract_repositories import AbstractFileRepository
from fastapi_app.src.file_storage.exceptions import (
    DirectoryError,
    FileAlreadyExistsError,
    FileDeletionError,
    FileReadError,
    FileWriteError,
)
from fastapi_app.src.schemas import FileMetadata

logger = logging.getLogger("app.file_storage.repositories")


class DiskRepository(AbstractFileRepository[FileMetadata]):
    def __init__(self, storage_dir: str):
        self._storage_dir = storage_dir
        self.__check_storage_directory_exists()

    def __check_storage_directory_exists(self):
        try:
            if not os.path.exists(self._storage_dir):
                os.makedirs(self._storage_dir)
        except Exception as e:
            raise DirectoryError(
                f"Failed to check storage directory existence: {str(e)}"
            )

    def __get_file_path(self, domain_obj: FileMetadata) -> Optional[str]:
        target_filename = domain_obj.name
        for filename in os.listdir(self._storage_dir):
            if filename == target_filename:
                return os.path.join(self._storage_dir, filename)

        return None

    def __validate_file_does_not_exist(self, domain_obj: FileMetadata):
        file_path = self.__get_file_path(domain_obj=domain_obj)

        if file_path:
            raise FileAlreadyExistsError(f"File '{domain_obj.name}' already exists.")

    async def write_file(self, file: UploadFile, domain_obj: FileMetadata) -> None:
        self.__validate_file_does_not_exist(domain_obj=domain_obj)

        file_path = os.path.join(self._storage_dir, domain_obj.name)

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)
            logger.info(
                f"File '{domain_obj.name}' successfully written to '{file_path}'"
            )
        except Exception as e:
            error_message = f"Failed to write file '{domain_obj.name}'"
            logger.error(f"{error_message}: {e}")
            raise FileWriteError(f"{error_message}: {e}")

    def read_file(self, domain_obj: FileMetadata) -> Dict:
        file_path = self.__get_file_path(domain_obj)

        if not file_path:
            error_message = (
                f"File with name '{domain_obj.name}' "
                f"and MIME type '{domain_obj.mimeType}' "
                f"not found in the storage directory."
            )
            logger.error(error_message)
            raise FileNotFoundError(error_message)

        try:
            payload = {
                "path": file_path,
                "media_type": domain_obj.mimeType,
                "filename": domain_obj.name,
            }
            logger.info(
                f"Successfully read file '{domain_obj.name}' payload from '{file_path}'"
            )
            return payload
        except Exception as e:
            error_message = f"Failed to read file '{domain_obj.name}' payload"
            logger.error(f"{error_message}: {e}")
            raise FileReadError(f"{error_message}: {e}")

    def delete_file(self, domain_obj: FileMetadata) -> None:
        file_path = self.__get_file_path(domain_obj=domain_obj)
        try:
            if file_path:
                os.remove(file_path)
                logger.info(f"File '{domain_obj.name}' successfully deleted")
            else:
                logger.warning(
                    f"There are no file with name '{domain_obj.name}' "
                    f"and MIME type '{domain_obj.mimeType}' "
                    f" in the storage directory."
                )
        except Exception as e:
            error_message = f"Failed to delete file '{domain_obj.name}': {e}"
            logger.error(error_message)
            raise FileDeletionError(error_message)
