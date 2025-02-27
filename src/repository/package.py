from datetime import date, datetime
from typing import List, Dict, Any
from src.utils.repository import BaseMongoRepository
from src.models.mongo_docs.package import PackageLog, PackageTypeSummaryLog


class PackageLogRepository(BaseMongoRepository):
    model = PackageLog

    async def insert_daily_calculated_packages(self, packages: List[Dict[str, Any]]):
        if packages:
            packages = [self.model(**package_type) for package_type in packages]
            await self.model.insert_many(packages)


class PackageTypeSummaryLogRepository(BaseMongoRepository):
    model = PackageTypeSummaryLog

    async def update_daily_sum(self, types: Dict[str, Any]):
        if types:
            if not types:
                return

            collection = self.model.get_motor_collection()
            for type_name, values in types.items():
                today = datetime.combine(date.today(), datetime.min.time())
                package_data = {
                    "package_type": type_name,
                    "date_log": today,
                    "total_cost": values["total_cost"],
                    "package_count": values["package_count"]
                }
                await collection.update_one(
                    {"package_type": type_name, "date_log": today},
                    {"$set": package_data},
                    upsert=True
                )
