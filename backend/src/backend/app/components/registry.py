import importlib
import inspect
import logging
import pkgutil

from backend.app.components.base import BaseComponent

logger = logging.getLogger(__name__)


class ComponentRegistry:
    def __init__(self):
        self._components: dict[str, type[BaseComponent]] = {}

    def register(self, component_cls: type[BaseComponent]) -> None:
        name = component_cls.get_name()
        self._components[name] = component_cls

    def get(self, name: str) -> type[BaseComponent] | None:
        return self._components.get(name)

    def list_components(self) -> list[type[BaseComponent]]:
        return list(self._components.values())

    def to_catalog(self) -> list[dict]:
        """Returns JSON-serializable list of all component schemas."""
        return [cls.get_schema() for cls in self._components.values()]

    def discover_package(self, package_name: str) -> None:
        """Dynamically imports and registers all BaseComponent subclasses in a package."""
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return

        for _, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__, package.__name__ + "."
        ):
            if is_pkg:
                continue
            try:
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseComponent) and obj is not BaseComponent:
                        self.register(obj)
            except (ImportError, AttributeError) as exc:
                logger.warning("Could not load component module %s: %s", module_name, exc)

_global_registry: ComponentRegistry | None = None

def get_registry() -> ComponentRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = ComponentRegistry()
    return _global_registry
