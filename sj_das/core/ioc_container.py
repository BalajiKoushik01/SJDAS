
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger("SJ_DAS.Core.IoC")

T = TypeVar('T')


class ServiceContainer:
    """
    Inversion of Control (IoC) Container.
    Manages service lifecycles and dependency injection.
    """
    _instance = None

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}

    @classmethod
    def instance(cls) -> 'ServiceContainer':
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """Register a pre-instantiated singleton."""
        self._services[interface] = instance
        logger.debug(f"Registered Singleton: {interface.__name__}")

    def register_factory(
            self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a transient factory."""
        self._factories[interface] = factory
        logger.debug(f"Registered Factory: {interface.__name__}")

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a dependency."""
        # 1. Check Singletons
        if interface in self._services:
            return self._services[interface]

        # 2. Check Factories
        if interface in self._factories:
            return self._factories[interface]()

        raise ValueError(f"Service not registered: {interface.__name__}")

    def reset(self):
        """Clear all services (Useful for testing)."""
        self._services.clear()
        self._factories.clear()
