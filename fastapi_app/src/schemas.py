from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: int
    name: str
    tag: str | None = None
    size: int
    mimeType: str
    modificationTime: str


class FileGetResponse(BaseModel):
    id: int
    name: str
    tag: str | None = None
    size: int
    mimeType: str
    modificationTime: str


class Message(BaseModel):
    message: str
