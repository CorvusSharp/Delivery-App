from pydantic import BaseModel, Field
from typing import Optional


class ParcelTypeResponse(BaseModel):
    id: int
    name: str


class ParcelRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0)
    type_id: int
    value_usd: float = Field(..., ge=0)


class ParcelResponse(BaseModel):
    id: int
    name: str
    weight: float
    type: Optional[ParcelTypeResponse]
    value_usd: float
    delivery_price_rub: Optional[float] = None
