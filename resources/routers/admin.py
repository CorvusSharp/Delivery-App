from fastapi import APIRouter, HTTPException
from adapters.messaging.tasks import update_delivery_prices

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/run-delivery-prices-task")
def run_delivery_prices_task():
    """Ручной запуск периодической задачи для расчёта стоимости доставки."""
    try:
        update_delivery_prices.delay()
        return {"detail": "Задача запущена"}
    except Exception as e:
        raise HTTPException(500, str(e))
