import asyncio
from vendors import VENDORS

async def fetch_all(qty):
    tasks = [v(qty) for v in VENDORS]
    return await asyncio.gather(*tasks)
