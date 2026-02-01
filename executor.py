import asyncio
import random

async def place_order(supplier):

    for _ in range(3):
        await asyncio.sleep(0.5)

        if random.random() < supplier["reliability"]:
            return True

    return False
