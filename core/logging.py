import sys, time, asyncio, functools
from loguru import logger
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_session_id: ContextVar[str] = ContextVar("session_id", default="-")

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | req={extra[request_id]} ses={extra[session_id]} | {message}",
    )
    return logger

def bind_context(request_id: str = "-", session_id: str = "-"):
    _request_id.set(request_id); _session_id.set(session_id)
    return logger.bind(request_id=request_id, session_id=session_id)

def log_call(fn):
    """Декоратор логирования и тайминга. Работает для async и sync."""
    is_async = asyncio.iscoroutinefunction(fn)

    @functools.wraps(fn)
    async def _aw(*args, **kwargs):
        log = bind_context(_request_id.get(), _session_id.get())
        start = time.perf_counter()
        log.info(f"▶ {fn.__qualname__}()")
        try:
            res = await fn(*args, **kwargs)
            log.info(f"✔ {fn.__qualname__}() in {(time.perf_counter()-start)*1000:.1f} ms")
            return res
        except Exception:
            log.exception(f"✖ {fn.__qualname__}() failed")
            raise

    @functools.wraps(fn)
    def _sw(*args, **kwargs):
        log = bind_context(_request_id.get(), _session_id.get())
        start = time.perf_counter()
        log.info(f"▶ {fn.__qualname__}()")
        try:
            res = fn(*args, **kwargs)
            log.info(f"✔ {fn.__qualname__}() in {(time.perf_counter()-start)*1000:.1f} ms")
            return res
        except Exception:
            log.exception(f"✖ {fn.__qualname__}() failed")
            raise

    return _aw if is_async else _sw
