from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pytz import UTC


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        # dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        dt = dt.replace(tzinfo=UTC)

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )


class FileMetadataDto(CustomModel):
    id: int
    name: str
    tag: Optional[str] = None
    size: int = None
    mimeType: str = None
    modificationTime: Optional[datetime] = None


class FileUploadResponse(CustomModel):
    id: int
    name: str
    tag: Optional[str]
    size: int
    mimeType: str
    modificationTime: Optional[datetime]


class FileGetResponse(CustomModel):
    id: int
    name: str
    tag: Optional[str]
    size: int
    mimeType: str
    modificationTime: Optional[datetime]


class Message(CustomModel):
    message: str
