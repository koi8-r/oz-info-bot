import asyncio
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Generic, TypeVar, Optional, Type, Union

from oz_info_bot.storage import AbcStorage
from oz_info_bot.svc import AbcBotSvc


Q = TypeVar('Q')


class AppExample(ABC, Generic[Q]):
    queue: asyncio.Queue[Q]
    sleep: Union[float, int, None] = None
    svc: AbcBotSvc

    def __init__(
            self,
            token: str,
            storage: AbcStorage,
            svc: Type[AbcBotSvc[Q]],
            sleep: Union[float, int, None] = None,
    ) -> None:
        self.queue = asyncio.Queue()
        self.sleep = sleep
        self.svc = svc(token, storage, self.queue)

    @abstractmethod
    async def worker(self) -> Optional[Q]:
        pass

    async def _worker(self) -> None:
        while True:
            o = await self.worker()
            if o is not None:
                self.queue.put_nowait(o)
            if self.sleep is not None:
                await asyncio.sleep(self.sleep)

    async def on_start(self) -> None:
        pass

    async def on_finish(self) -> None:
        pass

    async def run(self) -> None:
        tasks = [
            asyncio.create_task(self._worker()),
            asyncio.create_task(self.svc.run()),
        ]
        await self.on_start()
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        # Wait finished tasks to propagate unhandled exceptions
        await asyncio.gather(*done)
        await self.on_finish()
