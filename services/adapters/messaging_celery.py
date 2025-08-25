from typing import Mapping, Any, Optional
from domain.ports.messaging import TaskQueuePort
from core.celery import celery

class CeleryTaskQueueAdapter(TaskQueuePort):
    """Адаптер порта TaskQueuePort под Celery (RabbitMQ)."""
    def send(self, task_name: str, payload: Mapping[str, Any], *, queue: Optional[str] = None) -> str:
        sig = celery.send_task(task_name, kwargs=dict(payload), queue=queue or "default")
        return sig.id
