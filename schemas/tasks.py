"""
Схемы для API задач и фоновых процессов.
"""
from pydantic import BaseModel
from typing import Optional


class PingRequest(BaseModel):
    """Запрос на ping."""
    session_id: str


class TaskStatusResponse(BaseModel):
    """Ответ со статусом задачи."""
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
