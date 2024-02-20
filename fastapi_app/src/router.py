from typing import Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from fastapi_app.src.db_service.abstract_mappers import AbstractModelDictMapper
from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    DatabaseServiceError,
    DataLossError,
    MappingError,
    SessionNotSetError,
)
from fastapi_app.src.db_service.services import DatabaseService
from fastapi_app.src.dependencies import (
    determine_update_flag,
    file_service,
    get_query_params,
    valid_file_metadata,
)
from fastapi_app.src.di_containers import AppContainer
from fastapi_app.src.schemas import FileMetadata, Message

router = APIRouter(prefix="/v1", tags=["file_storage"])


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
@inject
async def create_update_file_handler(
    file_metadata: FileMetadata = Depends(valid_file_metadata),
    file: UploadFile = File(...),
    is_update: bool = Depends(determine_update_flag),
    database_service: DatabaseService = Depends(
        Provide[AppContainer.services.database_service_provider]
    ),
    mapper: AbstractModelDictMapper = Depends(
        Provide[AppContainer.mappers.file_metadata_dict_mapper_provider]
    ),
):
    try:
        # file_metadata_dict = mapper.to_dict(model_obj=file_metadata)

        file_metadata_saved = await file_service(file_metadata=file_metadata, file=file)
        file_metadata_saved_dict = mapper.to_dict(model_obj=file_metadata_saved)
        if is_update:
            result = await database_service.update_file_metadata(
                new_data=file_metadata_saved_dict
            )
        else:
            result = await database_service.add_file_metadata(
                data=file_metadata_saved_dict
            )

        return mapper.to_model(dict_obj=result)
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(status_code=500, detail="Error is on the repository layer")
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.get("/api/get", status_code=status.HTTP_200_OK)
@inject
async def get_files_info_handler(
    params: Dict[str, List] = Depends(get_query_params),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    database_service: DatabaseService = Depends(
        Provide[AppContainer.services.database_service_provider]
    ),
    mapper: AbstractModelDictMapper = Depends(
        Provide[AppContainer.mappers.file_metadata_dict_mapper_provider]
    ),
):
    try:
        result_lst = await database_service.get_file_metadata_by_params(
            params=params, limit=limit, offset=offset
        )

        return [mapper.to_model(dict_obj=result) for result in result_lst]
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(status_code=500, detail="Error is on the repository layer")
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.delete(
    "/api/delete",
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_400_BAD_REQUEST: {"model": Message},
    },
)
@inject
async def delete_files_handler(
    params: Dict[str, List] = Depends(get_query_params),
    database_service: DatabaseService = Depends(
        Provide[AppContainer.services.database_service_provider]
    ),
):
    if not any(params.values()):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Message(message="There are no parameters for deletion").dict(),
        )

    try:
        num_deleted_files = await database_service.remove_file_metadata(params=params)

        return Message(message=f"{num_deleted_files} files deleted")
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(status_code=500, detail="Error is on the repository layer")
    except DataLossError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Message(message="There are no parameters for deletion").dict(),
        )
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.get(
    "/api/download",
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@inject
async def download_file_handler(
    file_id: int,
):
    if file_id < 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="The file does not exist").dict(),
        )

    return Message(message="OK")
