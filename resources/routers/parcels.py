from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.parcel import ParcelRegisterRequest, ParcelResponse, ParcelTypeResponse
from repositories.parcel import ParcelRepository
from application.parcel_service import ParcelService
import uuid
from core.settings import auth as auth_settings

router = APIRouter(prefix="/parcels", tags=["Parcels"])

@router.post("/register", response_model=ParcelResponse)
async def register_parcel(
    data: ParcelRegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(session_cookie, session_id, httponly=True, samesite="lax")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    try:
        # Сервис теперь принимает отдельные параметры и возвращает словарь
        parcel_data = await service.register_parcel(
            name=data.name,
            weight=data.weight,
            type_id=data.type_id,
            value_usd=data.value_usd,
            session_id=session_id
        )
        # Маппинг словаря на DTO
        return ParcelResponse(**parcel_data)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/types", response_model=list[ParcelTypeResponse])
async def get_types(db: AsyncSession = Depends(get_db)):
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    # Сервис возвращает список словарей, маппим на DTO
    types_data = await service.get_types()
    return [ParcelTypeResponse(**type_data) for type_data in types_data]

@router.get("/", response_model=list[ParcelResponse])
async def list_parcels(
    request: Request,
    db: AsyncSession = Depends(get_db),
    type_id: int = Query(None),
    has_price: bool = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        raise HTTPException(401, "No session")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    # Сервис возвращает список словарей, маппим на DTO
    parcels_data = await service.list_parcels(session_id, type_id, has_price, limit, offset)
    return [ParcelResponse(**parcel_data) for parcel_data in parcels_data]

@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(parcel_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    session_cookie = auth_settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if not session_id:
        raise HTTPException(401, "No session")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    try:
        # Сервис возвращает словарь, маппим на DTO
        parcel_data = await service.get_parcel(parcel_id, session_id)
        return ParcelResponse(**parcel_data)
    except Exception as e:
        raise HTTPException(404, str(e))
