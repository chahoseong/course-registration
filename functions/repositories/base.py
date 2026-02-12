from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar, Optional

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    def save(self, data: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        pass
