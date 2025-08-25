from abc import ABC, abstractmethod
from typing import Mapping, Any, Optional

class TaskQueuePort(ABC):
    """Порт брокера сообщений (RabbitMQ через конкретный адаптер)."""
    @abstractmethod
    def send(self, task_name: str, payload: Mapping[str, Any], *, queue: Optional[str] = None) -> str:
        """Поставить сообщение в очередь и вернуть task_id."""
        raise NotImplementedError
