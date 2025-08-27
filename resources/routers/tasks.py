
"""
Роутер для управления фоновыми задачами.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from resources.dependencies import get_messaging_adapter
from repositories.interfaces import TaskQueuePort

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Pydantic-модель для входящего JSON
class PingRequest(BaseModel):
    session_id: str


@router.post("/ping")
async def send_ping(
    data: PingRequest,
    messaging: TaskQueuePort = Depends(get_messaging_adapter)
):
    """Отправить ping задачу в очередь."""
    task_id = messaging.send(
        task_name="tasks.ping",
        payload={"session_id": data.session_id}
    )
    return {"data": {"task_id": task_id}}
