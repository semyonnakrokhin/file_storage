from typing import Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Query, UploadFile

from fastapi_app.src.db_service.services import DatabaseService
from fastapi_app.src.di_containers import AppContainer
from fastapi_app.src.schemas import FileMetadata


async def file_service(file_metadata: FileMetadata, file: UploadFile) -> FileMetadata:
    # file_path = os.path.join(out_file_path, f"{file.filename}")
    # async with aiofiles.open(file_path, 'wb') as out_file:
    #     content = await file.read()
    #     await out_file.write(content)

    file_metadata.mimeType = file.content_type
    content = await file.read()
    file_metadata.size = len(content)
    return file_metadata


@inject
async def determine_update_flag(
    file_id: int,
    database_service: DatabaseService = Depends(
        Provide[AppContainer.services.database_service_provider]
    ),
) -> FileMetadata:
    file_metadata = await database_service.get_file_metadata_by_id(file_id=file_id)

    return bool(file_metadata)


async def valid_file_metadata(
    file_id: int,
    name: Optional[str] = None,
    tag: Optional[str] = None,
) -> FileMetadata:
    payload = {"id": file_id, "name": name if name else str(file_id), "tag": tag}
    return FileMetadata(**payload)


def get_query_params(
    file_id: List[int] = Query(None),
    name: List[str] = Query(None),
    tag: List[str] = Query(None),
) -> Dict[str, List]:
    return {"id": file_id, "name": name, "tag": tag}


if __name__ == "__main__":
    d = get_query_params()
    print(d)
