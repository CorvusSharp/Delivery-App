"""
Чистые доменные сущности без зависимостей от ORM или внешних библиотек.
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class ParcelType:
    """Тип посылки - чистая доменная сущность."""
    id: Optional[int]
    name: str
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Название типа посылки не может быть пустым")


@dataclass  
class Parcel:
    """Посылка - основная доменная сущность."""
    id: Optional[int]
    name: str
    weight: Decimal
    type: ParcelType
    value_usd: Decimal
    delivery_price_rub: Optional[Decimal] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Валидация бизнес-правил."""
        if not self.name or not self.name.strip():
            raise ValueError("Название посылки не может быть пустым")
            
        if self.weight <= 0:
            raise ValueError("Вес посылки должен быть положительным")
            
        if self.value_usd < 0:
            raise ValueError("Стоимость посылки не может быть отрицательной")
    
    def calculate_delivery_price(self, usd_rate: Decimal) -> Decimal:
        """Расчет стоимости доставки на основе веса и стоимости."""
        # Базовая стоимость: 100 руб + 50 руб за кг + 1% от стоимости
        base_price = Decimal("100")
        weight_price = self.weight * Decimal("50")
        value_price = self.value_usd * usd_rate * Decimal("0.01")
        
        return base_price + weight_price + value_price
    
    def set_delivery_price(self, price: Decimal):
        """Установка стоимости доставки."""
        if price < 0:
            raise ValueError("Стоимость доставки не может быть отрицательной")
        self.delivery_price_rub = price
