from dataclasses import dataclass
from typing import Mapping, Any
from domain.ports.messaging import TaskQueuePort

@dataclass(frozen=True)
class SendPingCommand:
    """Command (паттерн): поставить тестовую таску в брокер."""
    session_id: str
    queue: str = "default"

    def execute(self, bus: TaskQueuePort | None = None) -> str:
        if bus is None:
            raise RuntimeError("TaskQueuePort is required")
        payload: Mapping[str, Any] = {"session_id": self.session_id}
        return bus.send(task_name="tasks.ping", payload=payload, queue=self.queue)


