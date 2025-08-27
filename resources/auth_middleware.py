"""
Middleware для аутентификации и авторизации.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.settings import auth
import os


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для защиты административных эндпоинтов."""
    
    def __init__(self, app, protected_paths: list[str] | None = None):
        super().__init__(app)
        self.protected_paths = protected_paths or ["/admin", "/web"]
        self.is_production = os.getenv("ENV_FOR_DYNACONF", "development") == "production"
        
        # Проверяем, включена ли аутентификация
        try:
            self.auth_enabled = getattr(auth, "enabled", True)
        except (AttributeError, KeyError):
            self.auth_enabled = True  # По умолчанию включена
    
    async def dispatch(self, request: Request, call_next):
        # Если аутентификация отключена, пропускаем все проверки
        if not self.auth_enabled:
            response = await call_next(request)
            return response
            
        # Проверяем, нужно ли защищать путь
        path = request.url.path
        is_protected = any(path.startswith(protected_path) for protected_path in self.protected_paths)
        
        if is_protected:
            # В продакшене скрываем административные пути
            if self.is_production:
                return JSONResponse(
                    status_code=404, 
                    content={"detail": "Not Found"}
                )
            
            # В разработке проверяем простую аутентификацию
            if not self._check_auth(request):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required"},
                    headers={"WWW-Authenticate": "Basic"}
                )
        
        response = await call_next(request)
        return response
    
    def _check_auth(self, request: Request) -> bool:
        """Примитивная проверка авторизации."""
        # Проверяем Basic Auth
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False
        
        import base64
        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
            
            # Получаем логин/пароль из настроек
            admin_username = getattr(auth, "admin_username", "admin")
            admin_password = getattr(auth, "admin_password", "admin123")
            
            return username == admin_username and password == admin_password
        except Exception:
            return False
