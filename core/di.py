"""
Dependency Injection контейнер.
Связывает порты (интерфейсы) с их реализациями (адаптерами).
"""
from typing import Callable, Any, Dict
from functools import partial

from domain.repositories.interfaces import ParcelRepository, TaskQueuePort
from adapters.db.repositories.parcel import SQLAlchemyParcelRepository
from adapters.messaging.celery import CeleryTaskQueueAdapter


class Container:
    """Простой DI контейнер для связывания портов с адаптерами."""
    
    def __init__(self):
        self._providers: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, name: str, provider: Callable[[], Any], singleton: bool = False):
        """
        Регистрирует провайдер.
        
        Args:
            name: Имя сервиса
            provider: Функция-фабрика для создания экземпляра
            singleton: Если True, создается только один экземпляр
        """
        self._providers[name] = provider
        if singleton and name not in self._singletons:
            self._singletons[name] = None

    def resolve(self, name: str) -> Any:
        """Разрешает зависимость по имени."""
        provider = self._providers.get(name)
        if provider is None:
            raise KeyError(f"Provider '{name}' not registered")
        
        # Проверяем, нужен ли singleton
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = provider()
            return self._singletons[name]
        
        return provider()
    
    def has(self, name: str) -> bool:
        """Проверяет, зарегистрирован ли провайдер."""
        return name in self._providers


# Глобальный контейнер
container = Container()

# Регистрируем адаптеры для портов
def register_adapters():
    """Регистрирует все адаптеры в DI контейнере."""
    
    # Messaging адаптер (singleton)
    container.register(
        "messaging_adapter",
        lambda: CeleryTaskQueueAdapter(),
        singleton=True
    )


# Команды/события (пока не используется)
command_bus = None 
