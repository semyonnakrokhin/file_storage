from typing import Dict, List, Mapping

from fastapi import UploadFile

from fastapi_app.src.db_service.services import DatabaseService
from fastapi_app.src.file_storage.services import FileStorageService
from fastapi_app.src.schemas import FileMetadata


class ServiceManager:
    def __init__(
        self,
        file_storage_service: FileStorageService,
        database_service: DatabaseService,
    ):
        self._file_storage_service = file_storage_service
        self._database_service = database_service

    async def create_or_update_file(
        self, file: UploadFile, metadata: FileMetadata
    ) -> FileMetadata:
        file_metadata = await self._database_service.get_file_metadata_by_id(
            file_id=metadata.id
        )

        if not file_metadata:
            """Create scenario"""
            await self._file_storage_service.save_file(file=file, domain_obj=metadata)
            try:
                result = await self._database_service.add_file_metadata(
                    metadata=metadata
                )
            except Exception as e:
                self._file_storage_service.remove_file(domain_obj=metadata)
                raise e
        else:
            """Update scenario"""
            await self._file_storage_service.update_file(
                file=file, domain_obj_new=metadata, domain_obj_old=file_metadata
            )
            try:
                result = await self._database_service.update_file_metadata(
                    new_metadata=metadata
                )
            except Exception as e:
                self._file_storage_service.remove_file(domain_obj=metadata)
                raise e

        return result

    async def get_files_metadata(
        self, params: Dict[str, List], limit: int, offset: int
    ) -> List[FileMetadata]:
        result_lst = await self._database_service.get_file_metadata_by_params(
            params=params, limit=limit, offset=offset
        )

        return result_lst

    async def remove_files(self, params: Dict[str, List]) -> int:
        file_metadata_lst = await self._database_service.get_file_metadata_by_params(
            params=params
        )

        for file_metadata in file_metadata_lst:
            self._file_storage_service.remove_file(domain_obj=file_metadata)

        num_deleted_files = await self._database_service.remove_file_metadata(
            params=params
        )

        return num_deleted_files

    async def download_file(self, file_id: int) -> Mapping:
        file_metadata = await self._database_service.get_file_metadata_by_id(
            file_id=file_id
        )

        if file_metadata:
            payload = self._file_storage_service.get_file(domain_obj=file_metadata)
            return payload
