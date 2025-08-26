from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError, HTTPException
from loguru import logger


def success_response(data=None, message="OK"):
    """Стандартизированный успешный ответ."""
    return {"success": True, "message": message, "data": data}


def error_response(message, status_code=400, data=None):
    """Стандартизированный ответ об ошибке."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "data": data},
    )


def add_exception_handlers(app):
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTPException: {exc.detail}")
        return error_response(exc.detail, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # exc.errors() возвращает структуру с деталями валидации
        logger.error(f"Validation error: {exc.errors()}")
        return error_response("Validation error", status_code=422, data=exc.errors())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled error: {exc}")
        return error_response("Internal server error", status_code=500)
