import asyncio
from celery import Celery, signals
from src.config import REDIS_URL, CELERY_BEAT_CONF
from src.storage_conf.database import init_db
from src.storage_conf.mongo import beanie_init
from .tasks import calculate_shipping_price_async
from .dependencies import logger_service

app = Celery(
    'parcel_service',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['src.tasks.celery_app'],
)

app.conf.beat_schedule = CELERY_BEAT_CONF
app.conf.timezone = 'UTC'

loop = asyncio.get_event_loop()


async def initialize_databases():
    await init_db()
    await beanie_init()


@signals.worker_process_init.connect
def init_worker(**kwargs):
    loop.run_until_complete(initialize_databases())


@app.task
def calculate_shipping_price_task():
    loop.run_until_complete(calculate_shipping_price_async(log_service=logger_service))
