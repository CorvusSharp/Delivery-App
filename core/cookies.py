"""
Утилиты для работы с куки.
"""
import os
from fastapi import Response


def set_secure_session_cookie(response: Response, cookie_name: str, session_id: str) -> None:
    """Устанавливает безопасную сессионную куку с правильными параметрами."""
    is_production = os.getenv("ENV_FOR_DYNACONF", "development") == "production"
    
    response.set_cookie(
        cookie_name,
        session_id,
        httponly=True,
        samesite="lax",
        secure=is_production,  # HTTPS только в продакшене
        max_age=86400 * 7  # 7 дней
    )
