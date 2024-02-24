import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    DatabaseServiceError,
    DataLossError,
    MappingError,
    NoConditionsError,
    SessionNotSetError,
)
from fastapi_app.src.db_service.repositories import OrmAlchemyRepository
from fastapi_app.src.schemas import FileMetadata

logger = logging.getLogger("app.db_service.services")


class DatabaseService:
    def __init__(
        self,
        repository: OrmAlchemyRepository,
        async_session_factory: async_sessionmaker,
    ):
        self._repository = repository
        self._async_session_factory = async_session_factory

    async def add_file_metadata(self, metadata: FileMetadata) -> FileMetadata:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.insert_one(data=metadata)
                await session.commit()

            return file_metadata_output

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"adding the metadata to database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def update_file_metadata(self, new_metadata: FileMetadata) -> FileMetadata:
        file_id = new_metadata.id

        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.update_one(
                    id=file_id, new_data=new_metadata
                )
                await session.commit()

            return file_metadata_output

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"updating the metadata with id={file_id} in database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def get_file_metadata_by_id(self, file_id: int) -> Optional[FileMetadata]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.select_one_by_id(
                    id=file_id
                )

            return file_metadata_output if file_metadata_output else None

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"getting the metadata with id={file_id} from database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def get_file_metadata_by_params(
        self,
        params: Dict[str, List],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[FileMetadata]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output_lst = await self._repository.select_some_by_params(
                    params=params, limit=limit, offset=offset
                )

            return file_metadata_output_lst

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"getting some metadata by params from database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def remove_file_metadata(self, params: Dict[str, List]) -> int:
        if not any(params.values()):
            raise DataLossError("Removing all file metadata would result in data loss")

        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                ids_list = await self._repository.delete_some_by_params(params=params)
                await session.commit()

            return len(ids_list)

        except (
            SessionNotSetError,
            MappingError,
            DatabaseError,
            AttributeError,
            NoConditionsError,
        ) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"removing some metadata by params from database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()
