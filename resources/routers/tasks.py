from fastapi import APIRouter, Depends
from core.di import command_bus, container
from domain.commands.tasks import SendPingCommand
from resources.dependencies import get_session_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/ping")
async def send_ping(session_id: str = Depends(get_session_id)):
    # создаём команду и исполняем её через шину с адаптером из контейнера
    queue_port = container.resolve("task_queue")
    cmd = SendPingCommand(session_id=session_id)
    task_id = cmd.execute(bus=queue_port)
    return {"data": {"task_id": task_id}}
