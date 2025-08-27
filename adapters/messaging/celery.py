from typing import Mapping, Any, Optional

from repositories.interfaces import TaskQueuePort
from adapters.messaging.celery_app import celery


class CeleryTaskQueueAdapter(TaskQueuePort):
    """Адаптер порта TaskQueuePort под Celery (RabbitMQ)."""

    def send(self, task_name: str, payload: Mapping[str, Any], *, queue: Optional[str] = None) -> str:
        """Send a task to Celery and return task id.

        Args:
            task_name: Celery task name (e.g. 'tasks.ping').
            payload: kwargs mapping to pass to the task.
            queue: optional queue name; defaults to 'celery'.

        Returns:
            Celery task id as string.
        """
        sig = celery.send_task(task_name, kwargs=dict(payload), queue=queue or "celery")
        return sig.id
