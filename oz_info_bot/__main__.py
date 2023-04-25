import asyncio
import logging
from contextlib import suppress
from typing import Optional

import aiohttp

from oz_info_bot.simple_svc import SimpleBotSvc
from oz_info_bot.storage import MemIdStorage
from oz_info_bot.worker import worker
from oz_info_bot.conf import TOKEN
from oz_info_bot.app import AppExample
from oz_info_bot.models import Result, Response


async def _main() -> None:
    queue = asyncio.Queue()
    storage = MemIdStorage()
    svc = SimpleBotSvc(TOKEN, storage, queue)
    tasks = [
        asyncio.create_task(worker(svc.q)),
        asyncio.create_task(svc.run()),
    ]
    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    # Wait finished tasks to propagate unhandled exceptions
    await asyncio.gather(*done)


async def main() -> None:

    class App(AppExample[Result]):
        ua: aiohttp.ClientSession

        async def on_start(self) -> None:
            self.ua = aiohttp.ClientSession(
                base_url='https://some.org', raise_for_status=True,
            )

        async def on_finish(self) -> None:
            await self.ua.close()

        async def worker(self) -> Optional[Result]:
            async with self.ua.get(
                '/'
            ) as resp:
                r: Response = Response.parse_obj(await resp.json())
                for rr in (
                    _ for _ in r.result if 'IVANOV' in _.name.upper()
                ):
                    if 1 or rr.free_participants or rr.free_tickets:
                        return rr

    app = App(TOKEN, MemIdStorage(), SimpleBotSvc, sleep=10.0)
    await app.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    asyncio.run(main())
