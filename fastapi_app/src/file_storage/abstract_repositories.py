from abc import ABC, abstractmethod
from typing import Dict, Generic

from fastapi import UploadFile

from fastapi_app.src.app_types import D


class AbstractFileRepository(ABC, Generic[D]):
    @abstractmethod
    async def write_file(self, file: UploadFile, domain_obj: D) -> D:
        pass

    @abstractmethod
    def delete_file(self, domain_obj: D) -> None:
        pass

    @abstractmethod
    def read_file(self, domain_obj: D) -> Dict:
        pass
