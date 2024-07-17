import time
import asyncio
from faststream.redis.fastapi import RedisRouter, Logger


router = RedisRouter("redis://redis:6379/0")

@router.subscriber("test")
@router.publisher("response")
async def hello(logger: Logger):
    time.sleep(10)
    logger.info("HELLO")
    return {"response": "Hello, Redis!"}
