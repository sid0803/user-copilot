from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def send(self, message: str):
        pass
