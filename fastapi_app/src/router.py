from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, Query, Response, UploadFile, status
from fastapi.responses import JSONResponse

from fastapi_app.src.schemas import FileGetResponse, FileUploadResponse, Message

router = APIRouter(prefix="/v1", tags=["file_storage"])


@router.post("/api/upload", status_code=status.HTTP_201_CREATED)
async def create_update_file_handler(
    file_id: int,
    name: str | None = None,
    tag: str | None = None,
    file: UploadFile = File(...),
):
    # file_path = os.path.join(out_file_path, f"{file.filename}")
    # async with aiofiles.open(file_path, 'wb') as out_file:
    #     content = await file.read()
    #     await out_file.write(content)

    content = await file.read()
    # content = (1, 2, 3)

    payload = {
        "id": file_id or 1,
        "name": name or file_id,
        "tag": tag,
        "size": len(content),
        "mimeType": file.content_type,
        "modificationTime": datetime.utcnow().isoformat(),
    }

    return FileUploadResponse(**payload)


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
        "modificationTime": datetime.utcnow().isoformat(),
    }
    return FileGetResponse(**payload)


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
