from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from schemas.parcel import ParcelRegisterRequest, ParcelResponse, ParcelTypeResponse
from repositories.parcel import ParcelRepository
from domain.services import ParcelService
import uuid

router = APIRouter(prefix="/parcels", tags=["Parcels"])

@router.post("/register", response_model=ParcelResponse)
async def register_parcel(
    data: ParcelRegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    try:
        return await service.register_parcel(data, session_id)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/types", response_model=list[ParcelTypeResponse])
async def get_types(db: AsyncSession = Depends(get_db)):
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    return await service.get_types()

@router.get("/", response_model=list[ParcelResponse])
async def list_parcels(
    request: Request,
    db: AsyncSession = Depends(get_db),
    type_id: int = Query(None),
    has_price: bool = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401, "No session")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    return await service.list_parcels(session_id, type_id, has_price, limit, offset)

@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(parcel_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401, "No session")
    repo = ParcelRepository(db)
    service = ParcelService(repo)
    try:
        return await service.get_parcel(parcel_id, session_id)
    except Exception as e:
        raise HTTPException(404, str(e))
