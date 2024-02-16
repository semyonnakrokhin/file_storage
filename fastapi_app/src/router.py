from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.responses import JSONResponse

from fastapi_app.src.dependencies import file_service, valid_file_metadata
from fastapi_app.src.schemas import FileMetadataDto, Message

router = APIRouter(prefix="/v1", tags=["file_storage"])


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def create_update_file_handler(
    file_metadata: FileMetadataDto = Depends(valid_file_metadata),
    file: UploadFile = File(...),
):
    file_metadata_saved = await file_service(file_metadata=file_metadata, file=file)
    return file_metadata_saved


@router.get("/api/get", status_code=status.HTTP_200_OK)
async def get_files_info_handler(
    file_id: List[int] = Query(None),
    name: List[str] = Query(None),
    tag: List[str] = Query(None),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    print(file_id, name, tag, limit, offset)
    payload = {
        "id": 1,
        "name": "Nakrokh",
        "tag": "Hello World!",
        "size": 500,
        "mimeType": "img",
        "modificationTime": datetime.utcnow(),
    }
    print(payload["modificationTime"].tzinfo)
    return FileMetadataDto(**payload)


@router.delete(
    "/api/delete",
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_400_BAD_REQUEST: {"model": Message},
    },
)
async def delete_files_handler(
    response: Response,
    file_id: List[int] = Query(None),
    name: List[str] = Query(None),
    tag: List[str] = Query(None),
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    if not file_id and not name and not tag:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=Message(message="There are no parameters for deletion").dict(),
        )

    num_deleted_files = 4

    return Message(message=f"{num_deleted_files} files deleted")


@router.get(
    "/api/download",
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
async def download_file_handler(
    file_id: int,
):
    if file_id < 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=Message(message="The file does not exist").dict(),
        )

    return Message(message="OK")
