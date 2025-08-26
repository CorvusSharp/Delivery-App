from repositories.parcel import ParcelRepository
from domain.models import Parcel, ParcelType
from schemas.parcel import ParcelRegisterRequest, ParcelResponse, ParcelTypeResponse
from loguru import logger
from functools import wraps

# Декоратор логирования
def log_call(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        logger.info(f"Call {fn.__name__}")
        return await fn(*args, **kwargs)
    return wrapper

class ParcelService:
    def __init__(self, repo: ParcelRepository):
        self.repo = repo

    @log_call
    async def register_parcel(self, data: ParcelRegisterRequest, session_id: str) -> ParcelResponse:
        parcel = Parcel(
            name=data.name,
            weight=data.weight,
            type_id=data.type_id,
            value_usd=data.value_usd,
            session_id=session_id
        )
        parcel = await self.repo.add(parcel)
        return ParcelResponse(
            id=parcel.id,
            name=parcel.name,
            weight=parcel.weight,
            type=ParcelTypeResponse(id=parcel.type.id, name=parcel.type.name) if parcel.type is not None else None,
            value_usd=parcel.value_usd,
            delivery_price_rub=parcel.delivery_price_rub
        )

    @log_call
    async def get_parcel(self, parcel_id: int, session_id: str) -> ParcelResponse:
        parcel = await self.repo.get_by_id(parcel_id, session_id)
        if not parcel:
            raise ValueError("Parcel not found")
        return ParcelResponse(
            id=parcel.id,
            name=parcel.name,
            weight=parcel.weight,
            type=ParcelTypeResponse(id=parcel.type.id, name=parcel.type.name) if parcel.type is not None else None,
            value_usd=parcel.value_usd,
            delivery_price_rub=parcel.delivery_price_rub
        )

    @log_call
    async def list_parcels(self, session_id: str, type_id=None, has_price=None, limit=10, offset=0):
        parcels = await self.repo.list(session_id, type_id, has_price, limit, offset)
        return [
            ParcelResponse(
                id=p.id,
                name=p.name,
                weight=p.weight,
                type=ParcelTypeResponse(id=p.type.id, name=p.type.name) if p.type is not None else None,
                value_usd=p.value_usd,
                delivery_price_rub=p.delivery_price_rub
            ) for p in parcels
        ]

    @log_call
    async def get_types(self):
        types = await self.repo.get_types()
        result = []
        for t in types:
            result.append(ParcelTypeResponse(id=t.id, name=t.name))
        return result
