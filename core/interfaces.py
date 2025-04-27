from abc import ABC, abstractmethod

class BotHandler(ABC):
    @abstractmethod
    def can_handle(self, task_description: str) -> bool:
        pass

    @abstractmethod
    def handle(self, task_description: str) -> str:
        pass
