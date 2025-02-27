from src.models import Package
from .common import get_usd_rate


async def calculate_shipping(package: Package) -> float:
    usd_rate = await get_usd_rate()
    result = round(((package.weight / 1000) * 0.5 + package.content_price * 0.01) * usd_rate, 2)
    return result
