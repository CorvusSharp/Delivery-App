
from fastapi import APIRouter
from pydantic import BaseModel
from core.di import command_bus, container
from domain.commands.tasks import SendPingCommand

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Pydantic-модель для входящего JSON
class PingRequest(BaseModel):
    session_id: str

@router.post("/ping")
async def send_ping(data: PingRequest):
    # создаём команду и исполняем её через шину с адаптером из контейнера
    queue_port = container.resolve("task_queue")
    cmd = SendPingCommand(session_id=data.session_id)
    task_id = cmd.execute(bus=queue_port)
    return {"data": {"task_id": task_id}}
