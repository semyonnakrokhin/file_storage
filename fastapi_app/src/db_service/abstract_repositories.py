from abc import ABC, abstractmethod
from typing import Dict, Generic, List

from fastapi_app.src.app_types import D


class AbstractDatabaseRepository(ABC, Generic[D]):
    @abstractmethod
    async def insert_one(self, data: D) -> D:
        pass

    @abstractmethod
    async def update_one(self, id: int, new_data: D) -> D:
        pass

    @abstractmethod
    async def select_one_by_id(self, id: int) -> D:
        pass

    @abstractmethod
    async def select_some_by_params(
        self, limit: int, offset: int, params: Dict[str, List]
    ) -> List[D]:
        pass

    @abstractmethod
    async def delete_some_by_params(
        self, limit: int, offset: int, params: Dict[str, List]
    ) -> List[int]:
        pass
