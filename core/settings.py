# core/settings.py
from dynaconf import Dynaconf

settings = Dynaconf(
    load_dotenv=True,
    environments=True,  # [default], [development], [production] и т.д.
)

class _View:
    def __init__(self, key: str):
        self._k = key

    def __getattr__(self, name: str):
        section = settings.get(self._k)  # безопасно для регистра
        if section is None:
            raise AttributeError(f"Settings section '{self._k}' is missing")
        try:
            return section[name]
        except KeyError as e:
            raise AttributeError(f"Key '{name}' is missing in settings section '{self._k}'") from e

    def as_dict(self) -> dict:
        return settings.get(self._k) or {}
    

fastapi = _View("fastapi")
db      = _View("db")
redis   = _View("redis")
rabbitmq= _View("rabbitmq")
celery  = _View("celery")
auth    = _View("auth")
