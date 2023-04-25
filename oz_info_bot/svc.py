import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from types import MethodType
from typing import Callable, Set, Any, Generic, TypeVar

from aiogram import Bot, Router, Dispatcher
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from aiogram.filters import Command
from aiogram.types import Message

from oz_info_bot.storage import AbcStorage

logger = logging.getLogger(__name__)


Q = TypeVar('Q')


class AbcBotSvc(ABC, Generic[Q]):
    queue: asyncio.Queue[Q]

    def __init__(
            self, token: str, storage: AbcStorage, queue: asyncio.Queue[Q],
    ) -> None:
        self.bot = Bot(token, parse_mode=None)
        self.router = Router()
        self.dispatcher = Dispatcher()
        self.dispatcher.include_router(self.router)
        self.queue = queue
        self.storage = storage
        self.init_2()

    async def q_worker(self) -> None:
        while True:
            m = await self.q.get()  # CanceledError
            await self.handle_q(m)

    @abstractmethod
    async def handle_q(self, o: Q) -> None:
        pass

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            task_1 = tg.create_task(self.dispatcher.start_polling(self.bot))
            task_2 = tg.create_task(self.q_worker())
            # asyncio.Event: task_f = tg.create_task(self._stop_signal.wait())

    async def run(self) -> None:
        tasks: Set[asyncio.Task] = {
            asyncio.create_task(self.dispatcher.start_polling(self.bot)),
            asyncio.create_task(self.q_worker()),
        }
        for t in tasks:
            t.add_done_callback(tasks.discard)
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        # Wait finished tasks to propagate unhandled exceptions
        await asyncio.gather(*done)

    def init_2(self) -> None:
        for k, fn in ((k, getattr(self, k)) for k in self.__dir__()):
            _cmd = getattr(fn, '__bot_command__', None)
            _ic = getattr(fn, '__bot_command_ic__', True)
            if isinstance(fn, Callable) and _cmd is not None:
                fn = fn if isinstance(fn, MethodType) else MethodType(fn, self)
                cmd = tuple()
                if _cmd:
                    cmd += Command(commands=_cmd, ignore_case=_ic),
                self.m(*cmd)(fn)

    @property
    def r(self) -> Router:
        return self.router

    @property
    def m(self) -> TelegramEventObserver:
        return self.r.message

    @property
    def q(self) -> asyncio.Queue:
        return self.queue


Handler = Callable[[AbcBotSvc, Message], None]


def register(*cmd: str) -> Callable[[Handler], Handler]:
    def w(fn: Handler):
        fn.__bot_command__ = cmd
        return fn
    return w
