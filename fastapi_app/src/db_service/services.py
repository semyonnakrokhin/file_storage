import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from fastapi_app.src.db_service.abstract_mappers import AbstractModelDictMapper
from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    DatabaseServiceError,
    DataLossError,
    MappingError,
    NoConditionsError,
    SessionNotSetError,
)
from fastapi_app.src.db_service.repositories import OrmAlchemyRepository

logger = logging.getLogger("app.db_service.services")


class DatabaseService:
    def __init__(
        self,
        repository: OrmAlchemyRepository,
        mapper: AbstractModelDictMapper,
        async_session_factory: async_sessionmaker,
    ):
        self._repository = repository
        self._mapper = mapper
        self._async_session_factory = async_session_factory

    async def add_file_metadata(self, data: Dict) -> Dict:
        file_metadata_input = self._mapper.to_model(dict_obj=data)

        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.insert_one(
                    data=file_metadata_input
                )
                await session.commit()

            return self._mapper.to_dict(model_obj=file_metadata_output)

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            raise DatabaseServiceError(f"Unexpected database service error: {str(e)}")
        finally:
            self._repository.clear_session()

    async def update_file_metadata(self, new_data: Dict) -> Dict:
        file_metadata_input = self._mapper.to_model(dict_obj=new_data)
        file_id = file_metadata_input.id

        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.update_one(
                    id=file_id, new_data=file_metadata_input
                )
                await session.commit()

            return self._mapper.to_dict(model_obj=file_metadata_output)

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            raise DatabaseServiceError(f"Unexpected database service error: {str(e)}")
        finally:
            self._repository.clear_session()

    async def get_file_metadata_by_id(self, file_id: int) -> Optional[Dict]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output = await self._repository.select_one_by_id(
                    id=file_id
                )

            return (
                self._mapper.to_dict(model_obj=file_metadata_output)
                if file_metadata_output
                else None
            )

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            raise DatabaseServiceError(f"Unexpected database service error: {str(e)}")
        finally:
            self._repository.clear_session()

    async def get_file_metadata_by_params(
        self, params: Dict[str, List], limit: Optional[int], offset: Optional[int]
    ) -> List[Dict]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                file_metadata_output_lst = await self._repository.select_some_by_params(
                    params=params, limit=limit, offset=offset
                )

            return [
                self._mapper.to_dict(model_obj=file_metadata_output)
                for file_metadata_output in file_metadata_output_lst
            ]

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            raise DatabaseServiceError(f"Unexpected database service error: {str(e)}")
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
            raise DatabaseServiceError(f"Unexpected database service error: {str(e)}")
        finally:
            self._repository.clear_session()
