from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from application.parcel_service import ParcelService
from resources.dependencies import get_parcel_service
from core.usd import get_usd_rub_rate
from resources.i18n import translate_parcel_type
from schemas.parcel import ParcelRegisterRequest
from core.settings import auth as auth_settings
import uuid
import logging

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="resources/web")
router = APIRouter(prefix="/web", tags=["Web"])

@router.get("/", response_class=HTMLResponse)
async def web_index(request: Request, service: ParcelService = Depends(get_parcel_service)):
    # debug logging removed
    
    # Если это запрос отладки, принудительно устанавливаем сессию с данными
    session_cookie = auth_settings.session_cookie_name
    if request.query_params.get("debug") == "set_session":
        session_id = "581283af-2523-4a2d-9dd2-1ec8eabf5ac0"
    else:
        session_id = request.cookies.get(session_cookie) or str(uuid.uuid4())
    
    # debug logging removed
    
    types = await service.get_types()
    
    # Берём raw-параметры из запроса, чтобы избежать 422 при пустом type_id
    raw_type = request.query_params.get("type_id")
    raw_has_price = request.query_params.get("has_price")

    try:
        type_id_int = int(raw_type) if (raw_type is not None and str(raw_type).strip() != "") else None
    except ValueError:
        type_id_int = None

    has_price_val = None
    if raw_has_price is not None:
        # checkbox sends '1' when checked
        has_price_val = bool(int(raw_has_price)) if raw_has_price.isdigit() else True

    parcels = await service.list_parcels(session_id, type_id=type_id_int, has_price=has_price_val)
    
    
    usd_rub_rate = None
    try:
        usd_rub_rate = await get_usd_rub_rate()
    except Exception:
        pass
    # Сервис теперь возвращает словари, не нужно сериализовать
    types_data = types
    parcels_data = parcels

    response = templates.TemplateResponse("debug.html", {
        "request": request,
        "types": types_data,
        "parcels": parcels_data,
        "type_id": str(type_id_int) if type_id_int else "",
        "has_price": raw_has_price,
        "usd_rub_rate": usd_rub_rate,
        "message": request.query_params.get("message"),
        "translate_parcel_type": translate_parcel_type,
        "error": request.query_params.get("error"),
    })
    if not request.cookies.get(session_cookie):
        response.set_cookie(session_cookie, session_id, httponly=True, samesite="lax")
    return response

@router.post("/register")
async def web_register(
    request: Request,
    name: str = Form(...),
    weight: float = Form(...),
    type_id: int = Form(...),
    value_usd: float = Form(...),
    service: ParcelService = Depends(get_parcel_service)
):
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie) or str(uuid.uuid4())
    try:
        # Вызываем сервис с отдельными параметрами
        await service.register_parcel(
            name=name,
            weight=weight,
            type_id=type_id,
            value_usd=value_usd,
            session_id=session_id
        )
        resp = RedirectResponse("/web/?message=Посылка+зарегистрирована", status_code=303)
        # Если клиент не прислал cookie, установим её в ответе (чтобы headless клиенты получили session_id)
        if not request.cookies.get(session_cookie):
            resp.set_cookie(session_cookie, session_id, httponly=True, samesite="lax")
        return resp
    except Exception as e:
        resp = RedirectResponse(f"/web/?error={str(e)}", status_code=303)
        if not request.cookies.get(session_cookie):
            resp.set_cookie(session_cookie, session_id, httponly=True, samesite="lax")
        return resp

@router.post("/trigger-calc")
async def web_trigger_calc():
    from services.tasks_delivery import update_delivery_prices
    update_delivery_prices.delay()
    return RedirectResponse("/web/?message=Задача+расчёта+запущена", status_code=303)


@router.get("/debug-json")
async def debug_json(request: Request, service: ParcelService = Depends(get_parcel_service)):
    session_id = "581283af-2523-4a2d-9dd2-1ec8eabf5ac0"
    parcels = await service.list_parcels(session_id, limit=3)
    
    return {
        "session_id": session_id,
        "parcels_count": len(parcels),
        "first_parcel": {
            "id": parcels[0]["id"] if parcels else None,
            "type": parcels[0]["type"] if parcels else None,
            "type_type": str(type(parcels[0]["type"])) if parcels else None,
        } if parcels else None
    }
