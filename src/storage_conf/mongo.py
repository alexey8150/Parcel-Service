from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import MONGO_HOST, MONGO_PORT, MONGO_USER, MONGO_PASS
from src.models.mongo_docs.package import PackageLog, PackageTypeSummaryLog

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"
DATABASE_NAME = "package_service"


async def beanie_init():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    await init_beanie(database=db, document_models=[PackageLog, PackageTypeSummaryLog])
