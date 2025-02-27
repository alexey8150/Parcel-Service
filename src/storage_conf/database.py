from tortoise.contrib.fastapi import Tortoise

from src.config import DB_NAME, DB_PASS, DB_USER, DB_HOST, DB_PORT

DATABASE_URL = f"mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db() -> None:
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["src.models"]})
