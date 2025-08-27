from fastapi import APIRouter, HTTPException, Depends
from domain.repositories.interfaces import TaskQueuePort
from resources.dependencies import get_messaging_adapter

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/run-delivery-prices-task")
def run_delivery_prices_task(messaging: TaskQueuePort = Depends(get_messaging_adapter)):
    """Ручной запуск периодической задачи для расчёта стоимости доставки."""
    try:
        task_id = messaging.send("adapters.messaging.tasks.update_delivery_prices", payload={})
        return {"detail": "Задача запущена", "task_id": task_id}
    except Exception as e:
        raise HTTPException(500, str(e))
