from pydantic import BaseModel, Field, computed_field
from typing import Optional
from core.localization import translate_parcel_type


class ParcelTypeResponse(BaseModel):
    id: int
    name: str

    @computed_field
    @property
    def name_ru(self) -> str:
        return translate_parcel_type(self.name)


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

    @computed_field
    @property
    def type_ru(self) -> str:
        # support both string and object shapes just in case
        t = self.type
        if t is None:
            return ""
        if isinstance(t, str):
            return translate_parcel_type(t)
        # ParcelTypeResponse or dict-like
        try:
            name = t.name  # ParcelTypeResponse
        except Exception:
            name = t.get("name") if isinstance(t, dict) else str(t)
        return translate_parcel_type(name or "")
