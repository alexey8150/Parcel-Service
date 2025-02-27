from src.services.log_mongo import PackageMongoLogger
from src.repository.package import PackageLogRepository, PackageTypeSummaryLogRepository

logger_service = PackageMongoLogger(package_repo=PackageLogRepository(),
                                    daily_type_summary_repo=PackageTypeSummaryLogRepository())
