from typing import Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi_cache.decorator import cache

from fastapi_app.src.db_service.exceptions import (
    DatabaseError,
    DatabaseServiceError,
    DataLossError,
    MappingError,
    SessionNotSetError,
)
from fastapi_app.src.dependencies import get_query_params, valid_file_metadata
from fastapi_app.src.di_containers import AppContainer
from fastapi_app.src.file_storage.exceptions import (
    FileAlreadyExistsError,
    FileDeletionError,
    FileReadError,
    FileStorageError,
    FileWriteError,
)
from fastapi_app.src.manager import ServiceManager
from fastapi_app.src.schemas import FileMetadata, Message

router = APIRouter(prefix="/api/v1", tags=["file_storage"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@inject
async def create_update_file_handler(
    file_metadata: FileMetadata = Depends(valid_file_metadata),
    file: UploadFile = File(...),
    service_manager: ServiceManager = Depends(
        Provide[AppContainer.services.service_manager_provider]
    ),
):
    try:
        result = await service_manager.create_or_update_file(
            file=file, metadata=file_metadata
        )

        return result
    except (
        ValueError,
        FileAlreadyExistsError,
        FileWriteError,
        FileAlreadyExistsError,
        FileDeletionError,
    ):
        raise HTTPException(
            status_code=500, detail="Error is on the disk repository layer"
        )
    except FileStorageError:
        raise HTTPException(
            status_code=500,
            detail="Error is on the file storage service layer or lower",
        )
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(
            status_code=500, detail="Error is on the database repository layer"
        )
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer or lower"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.get("/get", status_code=status.HTTP_200_OK)
@cache(expire=60)
@inject
async def get_files_info_handler(
    params: Dict[str, List] = Depends(get_query_params),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    service_manager: ServiceManager = Depends(
        Provide[AppContainer.services.service_manager_provider]
    ),
):
    try:
        result_lst = await service_manager.get_files_metadata(
            params=params, limit=limit, offset=offset
        )

        return result_lst
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(
            status_code=500, detail="Error is on the database repository layer"
        )
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.delete(
    "/delete",
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_400_BAD_REQUEST: {"model": Message},
    },
)
@inject
async def delete_files_handler(
    params: Dict[str, List] = Depends(get_query_params),
    service_manager: ServiceManager = Depends(
        Provide[AppContainer.services.service_manager_provider]
    ),
):
    if not any(params.values()):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Message(message="There are no parameters for deletion").dict(),
        )

    try:
        num_deleted_files = await service_manager.remove_files(params=params)

        return Message(message=f"{num_deleted_files} files deleted")
    except DataLossError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Message(message="There are no parameters for deletion").dict(),
        )
    except (ValueError, FileDeletionError):
        raise HTTPException(
            status_code=500, detail="Error is on the disk repository layer"
        )
    except FileStorageError:
        raise HTTPException(
            status_code=500,
            detail="Error is on the file storage service layer or lower",
        )
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(
            status_code=500, detail="Error is on the database repository layer"
        )
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")


@router.get(
    "/download",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@inject
async def download_file_handler(
    file_id: int,
    service_manager: ServiceManager = Depends(
        Provide[AppContainer.services.service_manager_provider]
    ),
):
    payload = await service_manager.download_file(file_id=file_id)
    if not payload:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="The file does not exist").dict(),
        )
    try:
        return FileResponse(**payload, headers={"Custom-Message": "OK"})
    except (ValueError, FileNotFoundError, FileReadError):
        raise HTTPException(
            status_code=500, detail="Error is on the disk repository layer"
        )
    except FileStorageError:
        raise HTTPException(
            status_code=500,
            detail="Error is on the file storage service layer or lower",
        )
    except (SessionNotSetError, MappingError, DatabaseError, AttributeError):
        raise HTTPException(
            status_code=500, detail="Error is on the database repository layer"
        )
    except DatabaseServiceError:
        raise HTTPException(
            status_code=500, detail="Error is on the database service layer"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error is on the controller layer")
