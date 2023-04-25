from abc import ABC, abstractmethod
from typing import Generic, Hashable, MutableMapping, TypeVar, Optional


KT = TypeVar('KT', bound=Hashable)
VT = TypeVar('VT')


class AbcStorage(ABC, Generic[KT, VT]):
    @abstractmethod
    async def put(self, k: KT, v: Optional[VT]) -> None:
        pass

    @abstractmethod
    async def get(self, k: KT) -> Optional[VT]:
        pass

    @abstractmethod
    async def rm(self, k: KT) -> None:
        pass

    @abstractmethod
    async def __aiter__(self):
        pass


class MemIdStorage(AbcStorage[int, type(None)]):
    db: MutableMapping[KT, VT]

    def __init__(self) -> None:
        self.db = {}
        self._it = iter(self.db)

    async def put(self, k: KT, v: Optional[VT]) -> None:
        self.db[k] = v

    async def get(self, k: KT) -> Optional[VT]:
        return self.db[k]

    async def rm(self, k: KT) -> None:
        del self.db[k]

    def __aiter__(self):
        return self.aiter_wrapper()

    async def aiter_wrapper(self):
        for _ in iter(self.db):
            yield _
