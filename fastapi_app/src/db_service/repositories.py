import logging
from typing import Dict, Generic, List, Optional, Type

from sqlalchemy import BinaryExpression, and_, delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_app.src.app_types import D, E
from fastapi_app.src.db_service.abstract_mappers import AbstractDomainEntityMapper
from fastapi_app.src.db_service.abstract_repositories import AbstractDatabaseRepository
from fastapi_app.src.db_service.entities import FileOrm
from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    InvalidAttributeError,
    NoConditionsError,
    SessionNotSetError,
)
from fastapi_app.src.schemas import FileMetadataDto

logger = logging.getLogger("app.db_service.repositories")


class OrmAlchemyRepository(AbstractDatabaseRepository, Generic[E, D]):
    model: Optional[Type[E]] = None

    def __init__(self, mapper: AbstractDomainEntityMapper):
        self._session: Optional[AsyncSession] = None
        self._mapper = mapper

    def set_session(self, session: AsyncSession):
        if type(session) is not AsyncSession:
            error_message = (
                f"Session cannot be {type(session)}. Provide a valid AsyncSession."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

        self._session = session

    def clear_session(self):
        self._session = None

    def __validate_session_is_set(self):
        if self._session is None:
            error_message = (
                "Session not set. Call set_session() before using the repository."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

    async def insert_one(self, data: D) -> D:
        self.__validate_session_is_set()

        entity = self._mapper.to_entity(domain_obj=data)

        stmt = insert(self.model).values(**entity.to_dict()).returning(self.model)
        try:
            result = await self._session.execute(stmt)
            entity_db = result.scalars().one()
        except Exception as e:
            error_message = (
                f"An error occurred while insert one file-metadata "
                f"to session and executing statement: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        domain = self._mapper.to_domain(entity_obj=entity_db)

        return domain

    async def update_one(self, new_data: D) -> D:
        self.__validate_session_is_set()

        id_for_modification = new_data.id
        old_data = await self.select_one_by_id(id=id_for_modification)

        old_entity = self._mapper.to_entity(domain_obj=old_data)
        new_entity = self._mapper.to_entity(domain_obj=new_data)

        old_entity_dict = old_entity.to_dict()
        old_entity_dict.update(new_entity.to_dict())
        modified_entity_dict = old_entity_dict

        stmt = (
            update(self.model)
            .values(**modified_entity_dict)
            .filter_by(id=id_for_modification)
            .returning(self.model)
        )

        try:
            result = await self._session.execute(stmt)
            entity_db = result.scalars().one()
        except Exception as e:
            error_message = (
                f"An error occurred while update process of one file-metadata "
                f"got by its id and executing statement: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        domain = self._mapper.to_domain(entity_obj=entity_db)

        return domain

    async def select_one_by_id(self, id: int) -> D:
        self.__validate_session_is_set()

        query = select(self.model).filter_by(id=id)
        try:
            result = await self._session.execute(query)
            entity_db = result.scalars().one()
        except Exception as e:
            error_message = (
                f"An error occurred while selecting one file-metadata "
                f"by its id and executing query: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        domain = self._mapper.to_domain(entity_obj=entity_db)

        return domain

    async def select_some_by_params(
        self,
        params: Dict[str, List],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[D]:
        self.__validate_session_is_set()

        query = (
            select(self.model)
            .filter(self.get_filter_expression(params=params))
            .limit(limit)
            .offset(offset)
        )
        try:
            result = await self._session.execute(query)
            entity_list = result.scalars().all()
        except Exception as e:
            error_message = (
                f"An error occurred while selecting one file-metadata "
                f"by its id and executing query: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        return [self._mapper.to_domain(entity_obj=entity) for entity in entity_list]

    async def delete_some_by_params(
        self,
        params: Dict[str, List],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[int]:
        self.__validate_session_is_set()

        if not params:
            error_message = (
                "No conditions provided. "
                "At least one condition is required "
                "to avoid deleting all files."
            )
            logger.error(error_message)
            raise NoConditionsError(error_message)

        stmt = (
            delete(self.model).filter(self.get_filter_expression(params=params))
            # .limit(limit)
            # .offset(offset)
            .returning(self.model.id)
        )

        try:
            result = await self._session.execute(stmt)
            ids_list = result.scalars().all()
            return ids_list
        except Exception as e:
            error_message = (
                f"An error occurred while selecting one file-metadata "
                f"by its id and executing query: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

    def get_filter_expression(self, params: Dict[str, List]) -> BinaryExpression:
        and_items = []

        for k, v_list in params.items():
            attr = getattr(self.model, k, None)
            if not attr:
                error_message = (
                    f"The parameter '{k}' does not correspond "
                    f"to any attribute in the model."
                )
                logger.error(error_message)
                raise InvalidAttributeError(error_message)

            and_items.append(or_(*(attr == v for v in v_list)))

        return and_(*and_items)


class FileMetadataRepository(OrmAlchemyRepository[FileOrm, FileMetadataDto]):
    model = FileOrm
