"""
Роутер для операций с посылками.
Презентационный слой - тонкая обертка над use-cases.
"""
from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
from schemas import ParcelRegisterRequest, ParcelResponse, ParcelTypeResponse
from application.parcel_service import ParcelService
from resources.dependencies import get_parcel_service
import uuid
from core.settings import auth as auth_settings

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post("/register", response_model=ParcelResponse)
async def register_parcel(
    data: ParcelRegisterRequest,
    request: Request,
    response: Response,
    service: ParcelService = Depends(get_parcel_service)
):
    """Регистрация новой посылки."""
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        session_id = str(uuid.uuid4())
        # Определяем безопасность куки на основе окружения
        import os
        is_production = os.getenv("ENV_FOR_DYNACONF", "development") == "production"
        response.set_cookie(
            session_cookie, 
            session_id, 
            httponly=True, 
            samesite="lax",
            secure=is_production  # HTTPS только в продакшене
        )
    
    try:
        # Сервис теперь принимает отдельные параметры и возвращает словарь
        parcel_data = await service.register_parcel(
            name=data.name,
            weight=data.weight,
            type_id=data.type_id,
            value_usd=data.value_usd,
            session_id=session_id
        )
        return ParcelResponse(**parcel_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=list[ParcelTypeResponse])
async def get_types(service: ParcelService = Depends(get_parcel_service)):
    """Получение списка типов посылок."""
    try:
        types_data = await service.get_types()
        return [ParcelTypeResponse(**type_data) for type_data in types_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[ParcelResponse])
async def list_parcels(
    request: Request,
    service: ParcelService = Depends(get_parcel_service),
    type_id: int = Query(None, description="Filter by type ID"),
    has_price: bool = Query(None, description="Filter by presence of delivery price"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    order_by: str = Query("id", description="Sort by field (id, name, weight, value_usd)")
):
    """Получение списка посылок для текущей сессии."""
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        raise HTTPException(status_code=401, detail="No session")
    
    try:
        parcels_data = await service.list_parcels(
            session_id=session_id, 
            type_id=type_id, 
            has_price=has_price, 
            limit=limit, 
            offset=offset,
            order_by=order_by
        )
        return [ParcelResponse(**parcel_data) for parcel_data in parcels_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(
    parcel_id: int, 
    request: Request, 
    service: ParcelService = Depends(get_parcel_service)
):
    """Получение конкретной посылки по ID."""
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        raise HTTPException(status_code=401, detail="No session")
    
    try:
        parcel_data = await service.get_parcel(parcel_id, session_id)
        return ParcelResponse(**parcel_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Parcel not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
