import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from core.settings import auth
from core.logging import bind_context

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        session_cookie = auth.session_cookie_name
        session_id = request.cookies.get(session_cookie) or str(uuid.uuid4())
        # в state и в лог-контекст
        request.state.request_id = request_id
        request.state.session_id = session_id
        bind_context(request_id, session_id)
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        if request.cookies.get(session_cookie) is None:
            response.set_cookie(session_cookie, session_id, httponly=True, samesite="lax")
        return response
