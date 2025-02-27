from datetime import datetime, timezone

from tortoise.transactions import in_transaction

from src.models.sql_models.package import Package
from src.services.log_mongo import PackageMongoLogger
from src.utils import calculate_shipping


async def calculate_shipping_price_async(log_service: PackageMongoLogger):
    """Запрашивает все посылки у которых не расчитана цена доставки, расчитывет и добавляет логи о расчете через
    log_service.
        Args:
            log_service: PackageMongoLogger: сервис для логирования расчитанных посылок
            и суммы расчетов по типам посылок
        Returns:
            Ничего не возвращает
        """
    async with in_transaction():
        packages = await Package.filter(is_calculated=False).select_related('type')

        if not packages:
            return None

        packages_for_log = []
        sum_shipping_by_type = {}

        for package in packages:
            shipping_price = await calculate_shipping(package)
            package.shipping_price = shipping_price
            package.is_calculated = True

            packages_for_log.append(
                {"package_id": package.id,
                 "package_type": package.type.name,
                 "timestamp": datetime.now(timezone.utc),
                 "shipping_price": package.shipping_price})

            if package.type.name in sum_shipping_by_type:
                sum_shipping_by_type[package.type.name]["total_cost"] += shipping_price
                sum_shipping_by_type[package.type.name]["package_count"] += 1
            else:
                sum_shipping_by_type[package.type.name] = {
                    "total_cost": shipping_price,
                    "package_count": 1
                }

        await Package.bulk_update(packages, ['shipping_price', 'is_calculated'])

    await log_service.update_log(packages_for_log, sum_shipping_by_type)
