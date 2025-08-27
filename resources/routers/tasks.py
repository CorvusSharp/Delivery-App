
"""
Роутер для управления фоновыми задачами.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from resources.dependencies import get_messaging_adapter
from domain.repositories.interfaces import TaskQueuePort
from adapters.messaging.celery_app import celery

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Pydantic-модели для входящего JSON
class PingRequest(BaseModel):
    session_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None


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


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Получить статус задачи Celery по ID."""
    try:
        result = celery.AsyncResult(task_id)
        
        status = result.status
        task_result = None
        error = None
        
        if status == "SUCCESS":
            task_result = result.result
        elif status == "FAILURE":
            error = str(result.result)
        
        return TaskStatusResponse(
            task_id=task_id,
            status=status,
            result=task_result,
            error=error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")
