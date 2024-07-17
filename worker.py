import asyncio

from backend.worker.worker import app

async def main():
    await app.run()

asyncio.run(main())