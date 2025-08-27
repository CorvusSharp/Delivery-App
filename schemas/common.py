"""
Общие схемы для API ответов и ошибок.
"""
from pydantic import BaseModel
from typing import List, Any


class HTTPValidationError(BaseModel):
    """Схема для ошибок валидации HTTP."""
    detail: List[dict]


class ValidationError(BaseModel):
    """Детали ошибки валидации."""
    loc: List[str]
    msg: str
    type: str
    ctx: dict = None


class SuccessResponse(BaseModel):
    """Общий успешный ответ."""
    success: bool = True
    message: str
    data: Any = None
