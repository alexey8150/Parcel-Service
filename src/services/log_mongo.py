from typing import List, Dict, Any

from src.repository.package import PackageLogRepository, PackageTypeSummaryLogRepository


class PackageMongoLogger:
    def __init__(self, package_repo: PackageLogRepository, daily_type_summary_repo: PackageTypeSummaryLogRepository):
        self.package_repo = package_repo
        self.daily_type_summary_repo = daily_type_summary_repo

    async def update_log(self, packages: List[Dict[str, Any]], sum_shipping_by_type: Dict[str, Any]) -> None:
        await self.package_repo.insert_daily_calculated_packages(packages)
        await self.daily_type_summary_repo.update_daily_sum(sum_shipping_by_type)
