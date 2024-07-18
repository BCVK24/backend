from backend.worker.router import broker, app
import asyncio


async def main():
    await app.run()


asyncio.run(main())