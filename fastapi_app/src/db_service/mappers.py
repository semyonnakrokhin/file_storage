import logging
from typing import Dict

from fastapi_app.src.db_service.abstract_mappers import (
    AbstractDomainEntityMapper,
    AbstractModelDictMapper,
)
from fastapi_app.src.db_service.entities import FileOrm
from fastapi_app.src.db_service.exceptions import (
    DictConversionError,
    DomainModelCreationError,
    MappingError,
)
from fastapi_app.src.schemas import FileMetadata

logger = logging.getLogger("app.db_service.mappers")


class FileMetadataMapper(AbstractDomainEntityMapper[FileMetadata, FileOrm]):
    def to_entity(self, domain_obj: FileMetadata) -> FileOrm:
        try:
            payload = {
                "id": domain_obj.id,
                "name": domain_obj.name,
                "tag": domain_obj.tag,
                "size": domain_obj.size,
                "mime_type": domain_obj.mimeType,
            }
            return FileOrm(**payload)
        except Exception as e:
            error_message = (
                f"An error occurred during mapping domain model to db entity: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: FileOrm) -> FileMetadata:
        try:
            payload = {
                "id": entity_obj.id,
                "name": entity_obj.name,
                "tag": entity_obj.tag,
                "size": entity_obj.size,
                "mimeType": entity_obj.mime_type,
                "modificationTime": entity_obj.modification_time,
            }
            return FileMetadata(**payload)
        except Exception as e:
            error_message = (
                f"An error occurred during mapping entity model to domain: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)


class FileMetadataDictMapper(AbstractModelDictMapper[FileMetadata]):
    def to_dict(self, model_obj: FileMetadata) -> Dict:
        try:
            return model_obj.model_dump()
        except Exception as e:
            error_message = (
                f"Failed to convert model object to dictionary. " f"Error: {e}"
            )
            logger.error(error_message)
            DictConversionError(error_message)

    def to_model(self, dict_obj: Dict) -> FileMetadata:
        try:
            return FileMetadata(**dict_obj)
        except Exception as e:
            error_message = (
                f"Failed to create or update "
                f"file metadata "
                f"with provided data: {dict_obj}. Error: {e}"
            )
            logger.error(error_message)
            raise DomainModelCreationError(error_message)
