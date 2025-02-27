from datetime import datetime, timezone, date

from beanie import Document
from enum import Enum


class PackageType(Enum):
    CLOTHING = "clothes"
    ELECTRONICS = "electronics"
    OTHER = "other"


class PackageLog(Document):
    package_id: int
    package_type: PackageType
    timestamp: datetime = datetime.now(timezone.utc)
    shipping_price: float

    class Settings:
        name = "package_logs"


class PackageTypeSummaryLog(Document):
    package_type: PackageType
    date_log: date = date.today()
    total_cost: float = 0.0
    package_count: int = 0

    class Settings:
        name = "package_type_summaries"
        indexes = [
            [("package_type", 1), ("date_log", 1)],
        ]
