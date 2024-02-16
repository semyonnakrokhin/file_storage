from typing import Optional

from fastapi import UploadFile

from fastapi_app.src.schemas import FileMetadataDto


async def file_service(
    file_metadata: FileMetadataDto, file: UploadFile
) -> FileMetadataDto:
    # file_path = os.path.join(out_file_path, f"{file.filename}")
    # async with aiofiles.open(file_path, 'wb') as out_file:
    #     content = await file.read()
    #     await out_file.write(content)

    file_metadata.mimeType = file.content_type
    content = await file.read()
    file_metadata.size = len(content)
    return file_metadata


async def valid_file_metadata(
    file_id: int,
    name: Optional[str] = None,
    tag: Optional[str] = None,
) -> FileMetadataDto:
    payload = {"id": file_id, "name": name if name else str(file_id), "tag": tag}
    return FileMetadataDto(**payload)
