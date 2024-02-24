from typing import Dict, List, Optional

from fastapi import File, Query, UploadFile

from fastapi_app.src.schemas import FileMetadata


def valid_file_metadata(
    file_id: int,
    name: Optional[str] = None,
    tag: Optional[str] = None,
    file: UploadFile = File(...),
) -> FileMetadata:
    payload = {
        "id": file_id,
        "name": name if name else str(file_id),
        "tag": tag,
        "size": file.size,
        "mimeType": file.content_type,
    }
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
