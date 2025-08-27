from pydantic import BaseModel, Field
from typing import Optional


class ParcelWebRegisterRequest(BaseModel):
    """Схема для регистрации посылки через веб-форму."""
    name: str = Field(..., min_length=1, description="Название посылки")
    weight: float = Field(..., gt=0, description="Вес посылки в кг")
    type_id: int = Field(..., description="ID типа посылки")
    value_usd: float = Field(..., ge=0, description="Стоимость посылки в USD")


class ParcelTypeResponse(BaseModel):
    """ Схема для ответа на запрос о типе посылки."""
    id: int
    name: str


class ParcelRegisterRequest(BaseModel):
    """ Схема для регистрации посылки."""
    name: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0)
    type_id: int
    value_usd: float = Field(..., ge=0)


class ParcelResponse(BaseModel):
    """ Схема для ответа на запрос о посылке."""
    id: int
    name: str
    weight: float
    type: Optional[ParcelTypeResponse]
    value_usd: float
    delivery_price_rub: Optional[float] = None
