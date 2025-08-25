from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    load_dotenv=True,
    environments=True,
)

class _View:
    def __init__(self, key: str): self._k = key
    def __getattr__(self, name): return getattr(settings, self._k)[name]

fastapi = _View("fastapi")
db      = _View("db")
redis   = _View("redis")
rabbitmq= _View("rabbitmq")
celery  = _View("celery")
auth    = _View("auth")
