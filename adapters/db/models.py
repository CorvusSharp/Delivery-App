from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from adapters.db.session import Base
from typing import Optional

class ParcelType(Base):
    __tablename__ = "parcel_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)

class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("parcel_types.id"), nullable=False)
    value_usd = Column(Float, nullable=False)
    delivery_price_rub = Column(Float, nullable=True)
    session_id = Column(String(64), nullable=False)
    type = relationship("ParcelType")
