import logging.config
import os

from dependency_injector import containers, providers

from fastapi_app.logging_config import LOGGING_CONFIG
from fastapi_app.src.config import DatabaseSettings, merge_dicts
from fastapi_app.src.database import Database
from fastapi_app.src.db_service.mappers import FileMetadataMapper
from fastapi_app.src.db_service.repositories import FileMetadataRepository
from fastapi_app.src.db_service.services import DatabaseService
from fastapi_app.src.file_storage.repositories import DiskRepository
from fastapi_app.src.file_storage.services import FileStorageService
from fastapi_app.src.manager import ServiceManager


class CoreContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging_provider = providers.Resource(
        logging.config.dictConfig,
        config=config,
    )


class DatabaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    database_provider = providers.Singleton(Database, db_url=config.dsn)


class MapperContainer(containers.DeclarativeContainer):
    file_metadata_mapper_provider = providers.Factory(FileMetadataMapper)


class RepositoryContainer(containers.DeclarativeContainer):
    mappers = providers.DependenciesContainer()

    file_metadata_repository_provider = providers.Factory(
        FileMetadataRepository, mapper=mappers.file_metadata_mapper_provider
    )

    disk_repository_provider = providers.Factory(
        DiskRepository,
        storage_dir=os.path.join(os.path.dirname(__file__), os.path.pardir, "storage"),
    )


class ServicesContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    database = providers.DependenciesContainer()

    database_service_provider = providers.Factory(
        DatabaseService,
        repository=repositories.file_metadata_repository_provider,
        async_session_factory=database.database_provider.provided.get_session_factory,
    )

    file_storage_service_provider = providers.Factory(
        FileStorageService, file_repository=repositories.disk_repository_provider
    )

    service_manager_provider = providers.Factory(
        ServiceManager,
        file_storage_service=file_storage_service_provider,
        database_service=database_service_provider,
    )


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(CoreContainer, config=config.logging)

    database = providers.Container(DatabaseContainer, config=config.database)

    mappers = providers.Container(MapperContainer)

    repositories = providers.Container(RepositoryContainer, mappers=mappers)

    services = providers.Container(
        ServicesContainer, repositories=repositories, database=database
    )


if __name__ == "__main__":
    db_settings = DatabaseSettings()
    log_settings_dict = LOGGING_CONFIG
    settings_dict = merge_dicts(
        {"database": db_settings.model_dump()}, {"logging": log_settings_dict}
    )

    container = AppContainer()
    container.config.from_dict(settings_dict)
    container.core.init_resources()

    db = container.database.database_provider()
    database_service = container.services.database_service_provider()
    c = 1
