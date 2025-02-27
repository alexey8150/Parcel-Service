import json
from typing import Optional, Any, Dict, List
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist

from src.models import Package
from src.models import PackageType
from src.utils import get_redis


class PackageService:
    model = Package

    async def _lock_package_record(self, package_id: int, **data) -> bool:
        """Получает id посылки  и данные для того чтобы заблокировать определенную запись на изменение на 30 секунл.
            Args:
                package_id: int : id посылки для которуб необходимо заблокировать
                **data: данные о блокировке
            Returns:
                bool: возвращает False если запись заблокирована в противном случае True.
            """
        async with get_redis() as redis_client:
            lock_key = f"lock:package:{package_id}"
            lock_ttl_seconds = 30
            lock_acquired = await redis_client.setnx(lock_key, json.dumps(data))
            if not lock_acquired:
                return True
            await redis_client.expire(lock_key, lock_ttl_seconds)
            return False

    async def add_package(self, package_data: Dict[str, Any], user_uuid: str) -> int:
        """Получает dict  посылки c валидированными данными для добавления в базу данных
         и user_uuid чтобы привязать посылку к конкретному пользователю.
            Args:
                package_data: dict[str, Any]: запись о посылке
                user_uuid: str : uuid пользователя который добавил посылку
            Returns:
                int: возвращает id добавленной посылки
            """
        package_type_name = package_data.pop('type')

        package_type, _ = await PackageType.get_or_create(name=package_type_name)
        package = await self.model.create(**package_data, type=package_type, user_uuid=user_uuid)

        return package.id

    async def bind_delivery_company(self, package_id: int, delivery_data: Dict[str, Any]) -> bool:
        """Привязывает к послыке данные о компании доставки. После добавления запись посылки блокируется на изменение
        с помощью  _lock_package_record.
            Args:
                package_id: int: посылка к которой нужно привязать компанию доставки
                delivery_data: dict[str, Any]: данные о компании доставки
            Returns:
                bool: возвращает True если послыка успешно прявязана к компании доставки, если уже привязана False
            """
        is_locked = await self._lock_package_record(package_id, company_id=delivery_data['company_id'])
        if is_locked:
            return True

        package = await self.model.get(id=package_id)

        if package.transport_company:
            return True

        await self.model.filter(id=package_id).update(transport_company=delivery_data['company_id'])

        return False

    async def get_all_packages(self) -> List[Dict[str, Any]]:
        """Возвращает список всех посылок из базы данных.
            Args:
            Returns:
                list[dict[str, Any]]: возвращает список с посылками(каждая запись послыки это dict)
            """
        packages = await self.model.all().select_related('type')
        return [await package.to_dict() for package in packages]

    async def get_one_package(self, package_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает посылку по ее id.
            Args:
                package_id: int
            Returns:
                Optional[Dict[str, Any]]: Если послыка найдена вернет ее в формате dict, иначе None
            """
        try:
            package = await self.model.get(id=package_id).select_related('type')
            return await package.to_dict()
        except DoesNotExist:
            return None

    async def get_user_packages(self, user_uuid: str,
                                package_type: Optional[str],
                                is_calculated: Optional[bool],
                                offset: int,
                                count: int) -> Optional[List[Dict[str, Any]]]:
        """Возвращает посылки пользователя фильтруя по user_uuid, и отфильтрует посылки по типу и по наличию
        цены доставки если эти параметры переданы в запросе.
            Args:
                user_uuid: str,
                package_type: Optional[str],
                is_calculated: Optional[bool],
                offset: int,
                count: int
            Returns:
                Optional[List[Dict[str, Any]]] Если послыки найдены вернет их в формате list[dict], иначе None
            """

        query = Q(user_uuid=user_uuid)

        if package_type:
            query &= Q(type__name=package_type)
        if is_calculated is not None:
            query &= Q(is_calculated=is_calculated)

        packages = await self.model.filter(query).select_related('type').offset(offset).limit(count)

        if not packages:
            return None

        return [await package.to_dict() for package in packages]
