import sys
import asyncio
import functools
from loguru import logger
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_session_id: ContextVar[str] = ContextVar("session_id", default="-")


def setup_logging():
    """Configure and return logger for the process."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | {name} | {message}",
    )
    return logger


def bind_context(request_id: str = "-", session_id: str = "-"):
    """Bind request/session id to contextvars and return bound logger."""
    _request_id.set(request_id)
    _session_id.set(session_id)
    return logger.bind(request_id=request_id, session_id=session_id)


def log_call(fn):
    """Декоратор логирования и тайминга. Работает для async и sync функций.

    Декоратор берёт request/session id из contextvars и логирует вызов и время работы.
    """
    is_async = asyncio.iscoroutinefunction(fn)

    if is_async:
        @functools.wraps(fn)
        async def _aw(*args, **kwargs):
            log = bind_context(_request_id.get(), _session_id.get())
            log.info(f"CALL {fn.__name__} start")
            try:
                import time
                t0 = time.monotonic()
                result = await fn(*args, **kwargs)
                t1 = time.monotonic()
                log.info(f"CALL {fn.__name__} done in {(t1-t0):.3f}s")
                return result
            except Exception:
                log.exception(f"Exception in {fn.__name__}")
                raise

        return _aw

    else:
        @functools.wraps(fn)
        def _sw(*args, **kwargs):
            log = bind_context(_request_id.get(), _session_id.get())
            log.info(f"CALL {fn.__name__} start")
            try:
                import time
                t0 = time.monotonic()
                result = fn(*args, **kwargs)
                t1 = time.monotonic()
                log.info(f"CALL {fn.__name__} done in {(t1-t0):.3f}s")
                return result
            except Exception:
                log.exception(f"Exception in {fn.__name__}")
                raise

        return _sw
