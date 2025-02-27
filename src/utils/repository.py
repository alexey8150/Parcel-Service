from beanie import Document
from typing import TypeVar, List

T = TypeVar("T", bound=Document)


class BaseMongoRepository:
    model = None

    async def get_by_id(self, id: str) -> T | None:
        return await self.model.get(id)

    async def find_all(self) -> List[T]:
        return await self.model.find_all().to_list()
